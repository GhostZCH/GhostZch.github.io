## 计算元素在结构体中的位置

    define offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER);

