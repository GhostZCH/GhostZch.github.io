## offsetof

[www.zhaoch.top](http://www.zhaoch.top) > [编程](http://www.zhaoch.top/编程) > [c_cpp](http://www.zhaoch.top/编程/c_cpp)

## 计算元素在结构体中的位置

    define offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER);

