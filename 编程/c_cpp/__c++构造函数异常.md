## 构造函数中异常的

与其他有异常的机制的语言，不同，c++的构造函数有一些不同，测试了如下几个情况，记录下。

### 全局变量被构造，触发异常

目前没有发现这类异常的捕获方法，会直接触发程序退出。

测试代码

    class A{
    public:
        A(){
            throw 1;
        }
    };

    A a;

    int main(int argc, char const *argv[])
    {
        return 0;
    }

执行结果

    terminate called after throwing an instance of 'int'
    [1]    5768 abort (core dumped)  ./a.out


### 函数中局部变量被初始化

可以在上层函数中捕获，测试代码如下：

    #include <string>
    #include <iostream>

    using namespace std;


    class A{
    public:
        A(){
            throw 1;
        }
    };

    int func(){
        A a;
        return 1 + 1;
    }

    int main(int argc, char const *argv[])
    {
        try {
            func();
        } catch (int e) {
            cout << e << endl;
        }

        return 0;
    }

执行结果

    １

### 构造函数异常是不会触发析构函数的

这是一个值得重视的坑，先看下面的代码

    #include <string>
    #include <iostream>
    #include <memory>

    using namespace std;

    class Excp {
    public:
        Excp(const char* msg, const char* file, int line) {
            msg_ = msg;
            file_ = file;
            line_ = line;
        }

        friend ostream& operator << (ostream& out,const Excp& ex) {
            out << ex.file_ << "[" << ex.line_ << "]: " << ex.msg_;
            return out;
        }

    private:
        const char* msg_;
        const char* file_;
        int line_;
    };


    class A{
    public:
        A(){
            cout << "item" << endl;
        }

        ~A() {
            cout << "~item" << endl;
        }

        void Action(){
            throw Excp("Action", __FILE__, __LINE__);
        }
    };



    class B{
    public:
        B(){
            cout << "item" << endl;
            throw Excp("Construct", __FILE__, __LINE__);
        }

        ~B() {
            cout << "~item" << endl;
        }
    };


    int main(int argc, char const *argv[])
    {
        try {
            A a;
            a.Action();        
        } catch (Excp& ex){
            cout << ex << endl;
        }

        try {
            shared_ptr<A> a = shared_ptr<A>(new A());
            a->Action();        
        } catch (Excp& ex){
            cout << ex << endl;
        }

        try {
            B b;
        } catch (Excp& ex){
            cout << ex << endl;
        }

        try {
            shared_ptr<B> b = shared_ptr<B>(new B());
        } catch (Excp& ex){
            cout << ex << endl;
        }

        return 0;
    }

运行输出

    item
    ~item
    ept_test.cpp[38]: Action
    item
    ~item
    ept_test.cpp[38]: Action
    item
    ept_test.cpp[48]: Construct
    item
    ept_test.cpp[48]: Construct

可以看出如下两点

+ 局部变量的被动构造和指针的主动构造在异常处理上没有差别
+ 构造函数中的异常时是不会自动调用析构函数（也无法手动调用） 

所以由于c++的局部变量，全局变量，参数等存在“被构造”这种情况，所以还是不建议在构造函数做复杂的初始化操作，建议另外写一个init函数。