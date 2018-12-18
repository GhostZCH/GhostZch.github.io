## 背景

工作需要开发可一个nginx模块，里面用到了prce进行一些正则处理。模块的代码是通过ffi开放给lua调用的，运行也有段时间没啥问题。最近希望在lua中定时更新正则表达式，于是顺利成章的使用ngx-lua中的ngx.timer来进行修改，代码修改很少，看起来也没啥毛病。结果一测试，问题来了，执行报错。

## 分析

看了几圈代码，没发现啥毛病。调试发现pcre_exec执行的时候返回了-4，也就是`PCRE_ERROR_BADMAGIC`。先把nginx的worker数量改成1，然后gdb attach到worker上，打印了下对应的参数发现，magic真的不对。打印的时候有点麻烦，因为pcre结构体不能直接打印，只好指针强转到uint*,好在magic是第一个字段不用自己计算偏移了：

    // pcre_exec 原型，第一个参数时编译好的正则
    PCRE_EXP_DECL int  pcre_exec(const pcre *, const pcre_extra *, PCRE_SPTR,int, int, int, int *, int);

    // pcre在32位下的定义
    typedef struct real_pcre32 {
        pcre_uint32 magic_number;
        pcre_uint32 size;               /* Total that was malloced */
        pcre_uint32 options;            /* Public options */
        pcre_uint32 flags;              /* Private flags */
        pcre_uint32 limit_match;        /* Limit set from regex */
        pcre_uint32 limit_recursion;    /* Limit set from regex */
        pcre_uint32 first_char;         /* Starting character */
        pcre_uint32 req_char;           /* This character must be seen */
        pcre_uint16 max_lookbehind;     /* Longest lookbehind (characters) */
        pcre_uint16 top_bracket;        /* Highest numbered group */
        pcre_uint16 top_backref;        /* Highest numbered back reference */
        pcre_uint16 name_table_offset;  /* Offset to name table that follows */
        pcre_uint16 name_entry_size;    /* Size of any name items */
        pcre_uint16 name_count;         /* Number of name items */
        pcre_uint16 ref_count;          /* Reference count */
        pcre_uint16 dummy;              /* To ensure size is a multiple of 8 */
        const pcre_uint8 *tables;       /* Pointer to tables or NULL for std */
        void             *nullpad;      /* NULL padding */
    } real_pcre32;

反复调试了几次，发现编译好的正则的地址没变，但是从编译完成后到编译执行时的过程中指向的内容变化了。`pcre_compile`返回的结果内容是正确的，但是用的时候内容就变了。测试环境并没有其他的访问，谁改的呢？代码没看出问题，于是在正则编译完成后加了个watch断点。然后得到这么一个调用栈：

    _int_free
    ngx_destroy_pool
    ngx_http_lua_close_fake_connection
    ngx_http_lua_finalize_fake_request
    ngx_http_lua_finalize_request
    ngx_http_lua_timer_handler
    ngx_event_expire_timers
    ngx_process_events_and_timers
    ...

于是情况就清楚，timer结束后，ngx-lua会去清理timer过程中申请的临时内存，这些内存都放在一个`ngx_pool_t`中，通过`ngx_destroy_pool`清理。

但是为啥会清理到编译好的正则呢？这个就扯出来pcre的内存分配机制。pcre通过`pcre_free`,`pcre_malloc`两个全局函数指针来设置内存的申请和释放函数，为了方便内存管理，nginx和ngx-lua都各自修改了这两个函数的指针。见下面两个函数：

**这个是ngx-lua的**

    ngx_pool_t *
    ngx_http_lua_pcre_malloc_init(ngx_pool_t *pool)
    {
        ngx_pool_t          *old_pool;

        if (pcre_malloc != ngx_http_lua_pcre_malloc) {

            dd("overriding nginx pcre malloc and free");

            ngx_http_lua_pcre_pool = pool;

            // 另外找两个全局变量记录原有指针
            old_pcre_malloc = pcre_malloc;
            old_pcre_free = pcre_free;

            // 修改指针到自己的函数
            pcre_malloc = ngx_http_lua_pcre_malloc;
            pcre_free = ngx_http_lua_pcre_free;

            return NULL;
        }

        dd("lua pcre pool was %p", ngx_http_lua_pcre_pool);

        old_pool = ngx_http_lua_pcre_pool;
        ngx_http_lua_pcre_pool = pool;

        dd("lua pcre pool is %p", ngx_http_lua_pcre_pool);

        return old_pool;
    }

    void
    ngx_http_lua_pcre_malloc_done(ngx_pool_t *old_pool)
    {
        dd("lua pcre pool was %p", ngx_http_lua_pcre_pool);

        ngx_http_lua_pcre_pool = old_pool;

        dd("lua pcre pool is %p", ngx_http_lua_pcre_pool);

        if (old_pool == NULL) {
            // 通过这个还原回去
            pcre_malloc = old_pcre_malloc;
            pcre_free = old_pcre_free;
        }
    }

**这个是nginx的**

    void
    ngx_regex_init(void)
    {
        pcre_malloc = ngx_regex_malloc;
        pcre_free = ngx_regex_free;
    }

因为没法给这两个函数指针执行的函数传参数，于是又有两个全局变量记录需要分配的内存池

    static ngx_pool_t  *ngx_pcre_pool;
    static ngx_pool_t *ngx_http_lua_pcre_pool = NULL;

案发现场是这样的，nginx启动的时候已经设置了`pcre_malloc`和`pcre_free`。ngx-lua中也用到了pcre，没办法，只能每个phase需要进入到lua代码前先把nginx设置的两个指针存起来，执行完lua代码在把那两个指针恢复了，不然nginx就出错。timer执行的时候ngx-lua已经设置好了这两个指针并且初始化了一个pool用于临时pcre数据存放。偏偏我在timer里执行了正则编译操作，并且保存下了这个结果等着以后用。不巧的是timer结束后，这个pool被释放了，我的编译结果也就变成了野指针。后面请求处理的时候，magic自然也就对不上。

## 解决方法

基本上就两种:

+ 在自己的这段程序前设置好这两个指针，保存旧指针，用后恢复
+ 封装一下`pcre_compile`函数，大概时下面这个样子

    my_pcre_compile(..., malloc_ptr)
    {
        old_malloc = pcre_malloc;
        pcre_malloc = malloc_ptr;
        pcre_compile(...);
        pcre_malloc = old_malloc;
    }

第二个增加了太多的赋值操作，ngx-lua选择了第一个，我也选择了第一个，在增加了两个函数，３个全局变量后，总算归于平静。当然这个方法也很危险，万一代码在变更了函数指针后执行到某个位置提前退出忘记恢复指针了，整个程序估计就歇菜了。

## 吐槽

Ｃ程序经常要自己管理内存，pcre显然考虑到了这一点，不过感觉通过全局函数指针这个方式设置内存管理函数显得还是太简单粗暴了一些。

如果程序很简单，自然没啥问题。但是如果程序中有多个模块都要调用pcre并且希望以不同的方式分配内存，如果这堆模块还互相调用（就像上面的情形），代码不知要多多少行，要多多少全局变量，要多多少不安全的操作，而且代码变得很混乱。

静下来想一想，如果时我设计这个api会怎么操作。也许是增加一个mem_manager的结构体，记录malloc和free的指针以及其他参数，类似c++ std中使用的alloctor。每个api都增加一个可选参数，传递这个结构体。

    typedef struct {
        xxx free;
        xxx malloc;
        xxx data;
    }mem_manager_t;

当然我更喜欢的还是把申请工作放在函数之外，把申请好的空间传递给api进行赋值，申请和释放都由调用者来处理。不过这样结构体的设计变得比较复杂，尤其是涉及到变长结构的时候。