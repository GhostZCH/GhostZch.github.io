## gcc常用参数

[www.zhaoch.top](http://www.zhaoch.top) > [编程](http://www.zhaoch.top/编程) > [c_cpp](http://www.zhaoch.top/编程/c_cpp)

## gcc 常用参数

### -shared

编译共享库

### -fPIC

编译时固定地址，编译共享库要添加

### -Wl

选项告诉编译器将后面的参数传递给链接器。

### -Wl -rpath

制定二进制文件运行时的查找路径，在程序需要的库和系统库不一致时非常有用

### -Wl,--export-all-symbols

编译时导出所有符号，例如下面的场景：

可执行文件app调用b.so,b.so编译要用c.a,app需要调用一个c.a中的函数，在编译b.so时需要增加这个参数

TODO 写代码确认下
## The End

+ My [github location](https://github.com/GhostZCH/)
+ View Source of this website [GhostZch.github.io](https://github.com/GhostZCH/GhostZch.github.io/)
+ Commit [issues](https://github.com/GhostZCH/GhostZch.github.io/issues) to discuss with me and others
