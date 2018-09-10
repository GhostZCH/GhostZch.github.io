## dlopen的一些记录

[www.zhaoch.top](http://www.zhaoch.top) > [编程](http://www.zhaoch.top/编程) > [c_cpp](http://www.zhaoch.top/编程/c_cpp)

## 测试dlopen函数的功能，主要时符号加载

### 设置如下4个文件
base.h

    int add(int a, int b);

base.c

    int add(int a, int b)
    {
        return a + b;
    }

so.c

    #include <stdio.h>
    #include "base.h"
    void action()
    {
        int re = add(3, 4);
        printf("action [%p] %d + %d = %d\n", add, 3, 4, re);
    }

so1.c

    int action1()
    {
        return action();
    }

main.c

    #include "base.h"
    #include <dlfcn.h>
    #include <stdio.h>
    typedef void (*F)();
    int main()
    {
        int re = add(1,2);
        printf("main [%p] %d + %d = %d\n", add, 1, 2, re);
        void* h = dlopen("/home/zhaoch/code/cpp_test/sotest/so.so", RTLD_NOW|RTLD_GLOBAL);
            if (!h) {
                fprintf(stderr, "%s\n", dlerror());
                return 1;
        }
        F f = (F)dlsym(h, "action");
        f();
        void* h1 = dlopen("/home/zhaoch/code/cpp_test/sotest/so1.so", RTLD_NOW|RTLD_GLOBAL);
        if (!h1) {
                fprintf(stderr, "%s\n", dlerror());
                return 1;
        }
        f = (F)dlsym(h1, "action1");
        f();
     
        return 0;
    }

## 测试的一些记录

### 编译so的时候不会检查每个函数是否有定义

例如：gcc -g -O0 -fPIC -shared  so.c -o so.so 是可以通过的 但是只有在dlopen的时候才检查add是否存在，发现并不存在报错 undefined symbol: add

### 防止上述错误可以把调用的内容一起编译进来，如gcc -g -O0 -fPIC -shared so.c base.c -o so.so，但是测试的add与主程序的add函数并不是同一个,打印信息如下

    main [0x4007bd] 1 + 2 = 3
    action [0x7fa2206236dc] 3 + 4 = 7

### so中没有办法调用主程序的函数，例如例子1中提到的，主程序中有add函数，但是action函数无法使用，除非通过 -Wl,-E告诉连接器把所有的符号都导出

### 后面加载的so文件可以调用之前加载so文件的函数，需要有RTLD_GLOBAL标志,打印如下

    main [0x4007bd] 1 + 2 = 3
    action [0x7f1007cbc6dc] 3 + 4 = 7
    action [0x7f1007cbc6dc] 3 + 4 = 7

不加 RTLD_GLOBAL标志会报错
   
    /xxx/so1.so: undefined symbol: action

### so和主程序出现重名的情况下，gdb会有下面的现象

    (gdb) p add
    $1 = {int (int, int)} 0x4007bd <add>
    (gdb) b add
    Note: breakpoint 1 also set at pc 0x4007c7.
    Note: breakpoint 1 also set at pc 0x7ffff75de6e6.
    Breakpoint 2 at 0x4007c7: add. (2 locations)

## 参考

> http://www.cppblog.com/markqian86/archive/2017/09/27/215269.html

## The End

+ My [github location](https://github.com/GhostZCH/)
+ View Source of this website [GhostZch.github.io](https://github.com/GhostZCH/GhostZch.github.io/)
+ Commit [issues](https://github.com/GhostZCH/GhostZch.github.io/issues) to discuss with me and others
