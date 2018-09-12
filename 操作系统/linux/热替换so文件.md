## 热替换so文件

[www.zhaoch.top](http://www.zhaoch.top) > [操作系统](http://www.zhaoch.top/操作系统) > [linux](http://www.zhaoch.top/操作系统/linux)

## 代码准备

reload.c, 启动文件，用来模拟正在运行的程序，不断重建加载so.so文件

    #include <dlfcn.h>
    #include <stdio.h>

    typedef void (*F)();

    int my_dlopen()
    {
        void* h = dlopen("so.so", RTLD_NOW|RTLD_GLOBAL);
        if (!h) {
            fprintf(stderr, "%s\n", dlerror());
            return 1;
        }

        F f = (F)dlsym(h, "action");
        f();

        return 0;
    }

    int main(int argc, char const *argv[])
    {
        printf("start...\n");

        while (1) {
            printf("run\n");
            if (my_dlopen() != 0) {
                return 1;
            }
            sleep(2);
        }

        return 0;
    }

so1.c 模拟其中一个so文件

    #include <stdio.h>

    void action()
    {
        printf("11111111111111111\n");
    }


so2.c 模拟其中另一个so文件，接口相同，打印内容不同

    #include <stdio.h>

    void action()
    {
        printf("222222222222222222222\n");
    }

编译

    gcc reload.c -ldl -o reload
    gcc -fPIC -shared so1.c -o so1.so
    gcc -fPIC -shared so2.c -o so2.so

注意

    所有的实验需要 export LD_LIBRARY_PATH=./

## 第一次尝试，直接cp替换

先将 so1.so 设置成默认的 so文件

    cp so1.so so.so

启动程序， 然后执行 `cp so2.so so.so`

    ./reload 
    start...
    run
    11111111111111111
    run
    11111111111111111
    run
    11111111111111111
    run
    11111111111111111  <-- 执行 cp so2.so so.so
    run
    [1]    38314 segmentation fault (core dumped)  ./reload

程序直接崩溃


同时测试了下，`rm so.so`并不影响执行,但是停止程序再启动显示`so.so: cannot open shared object file: No such file or directory
` 这个可能说明，so文件被打开一次后句柄并不会关闭，下次打开任然用这个句柄。只是重新读取文件。cp 改变文件内容，并不改变文件inode。

## 先rm再cp

    cp so1.so so.so

    ./reload
    start...
    run
    11111111111111111
    run
    11111111111111111
    run
    11111111111111111
    run
    11111111111111111
    run
    11111111111111111  <-- rm so.so;cp so2.so so.so
    run
    11111111111111111
    run
    11111111111111111
    run
    11111111111111111

结果就是更新无效，猜想还是句柄没关闭的原因。rm的后，程序还指向原来的文件（这个文件外界看不到）, cp产生了一个新的文件，程序根本没有理睬这个文件。

## dlclose 再加载

在代码中加入 dlclose(h)，如下：

    int my_dlopen()
    {
        void* h = dlopen("so.so", RTLD_NOW|RTLD_GLOBAL);
        if (!h) {
            fprintf(stderr, "%s\n", dlerror());
            return 1;
        }

        F f = (F)dlsym(h, "action");
        f();

        dlclose(h); // <--

        return 0;
    }

这次可以了

    ./reload
    start...
    run
    11111111111111111
    run
    11111111111111111
    run
    11111111111111111
    run
    11111111111111111   <-- cp so2.so so.so
    run
    222222222222222222222
    run
    222222222222222222222
    run
    222222222222222222222
    run
    222222222222222222222

说明确实时句柄的问题，这里涉及到linux inode的问题。每个文件都会对应一个inode, 内部都是按照inode来处理的，同一个文件名的不一定是同一个inode。一个文件只有在没有任何引用的时候才被删除，当程序打开一个so文件，这个文件就被引用了，即使外部删除这个文件，程序还是在使用这个so文件，这个文件只有在程序关闭时才被系统回收。cp过来时个全新的文件，只是文件名相同，inode并不相同,其实程序还是用着老的so文件。dlclose恰恰时关闭了这个文件，之后再次按文件名打开就是新的文件。

## PS

看了下nginx的代码，reload的时候貌似不会dlclose, 这个太奇怪了。

## The End

+ My [github location](https://github.com/GhostZCH/)
+ View Source of this website [GhostZch.github.io](https://github.com/GhostZCH/GhostZch.github.io/)
+ Commit [issues](https://github.com/GhostZCH/GhostZch.github.io/issues) to discuss with me and others
