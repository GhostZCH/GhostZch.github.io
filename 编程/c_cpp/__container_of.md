## container_of

已知结构体某个元素的地址，获取这个结构体起始地址。定义如下

    /**
    * container_of - cast a member of a structure out to the containing structure
    * @ptr:     the pointer to the member.
    * @type:     the type of the container struct this is embedded in.
    * @member:     the name of the member within the struct.
    *
    */
    #define container_of(ptr, type, member) ({             \
    const typeof( ((type *)0)->member ) *__mptr = (ptr);     \
    (type *)( (char *)__mptr - offsetof(type,member) );})

例如：

    typdef struct {
        int x;
        int y;
    } Point;

    Point p;

    int *a = &p.x

    assert(&p == container_of(a, Point, x));

在linux下c编程中主要用作通过链表等数据结构获得父容器,这种用法非常常见。

    typdef struct list_node_s{
        struct list_node_s* next;
    }list_node_t;

    typdef struct user_s {
        char *name;
        char *pwd;
        list_node_t node;
    }user_t;

    user_t u1, u2;
    u1.node.next = &u2.node;

    assert(&u2 == container_of(u1.node.next, user_t, node))

> http://blog.csdn.net/zhuxiaowei716/article/details/7562986

