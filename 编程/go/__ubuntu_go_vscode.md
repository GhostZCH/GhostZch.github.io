## 在ubuntu 18.04上配置vscode 开发golang

之前装了golang和vscode但是一直苦于没有函数帮助的自动显示和智能补全的功能，用起来非常不方便。花了几个小时仔细研究了下，总算解决了，记录下方法

### 清理环境

如果之前转过golang，或者做个配置需要清理下环境。把golang相关的包都卸载(例如：apt-get perge golang)。检查自己电脑上的影响环境变量的文件，关于golang的全部删除掉。例如：

    /etc/profile
    /etc/environment
    /etc/bash.bashrc
    ~/.bashrc
    ...

不放心的话vscode 安装的go插件也可以卸载了

### 安装ｇolang

我选择的apt-get方式安装，方便更新，也不用自己配置环境变量。自己编译的同学可以参考其他的帖子，编译安装需要仔细检查环境变量。
安装后执行`go env`查看环境变量，`GOPATH`对应的路径不可能存在，需要自己建立文件夹，后面的库才能正常安装。

### vscode　配置

+ 安装go开发插件，有个微软出的go插件就可以了
+ 配置gopath, file-> performence -> setting -> user setting -> extensitions -> go configuration -> 编辑json 添加　`"go.gopath": "/go/path/"` （也就是上面`go env`后建立的文件夹）

### 安装代码提示工具

理论上，vscode的golang插件会自动安装，但是由于访问google服务器有问题，所以需要手动安装golang.org的工具。具体安装那些可以参考vscode的安装提示，安装失败的一个个来。go get 失败的一些可以在git上直接clone下了，clone的时候需要注意下路径。$GOPATH/src的路径下。按照包的名称存放文件夹。主要时golang/tool，这边可以自己看下帮助 https://github.com/golang/tools 。特别的，gocode需要在文件夹中执行下go install 才能生效。可以参考如下路径：

    ➜  go tree -d -L 4
    .
    ├── bin
    ├── pkg
    │   └── linux_amd64
    │       └── gopkg.in
    └── src
        ├── github.com
        │   ├── acroca
        │   │   └── go-symbols
        │   ├── derekparker
        │   │   └── delve
        │   ├── go-delve
        │   │   └── delve
        │   ├── karrick
        │   │   └── godirwalk
        │   ├── mdempsky
        │   │   └── gocode
        │   ├── pkg
        │   │   └── errors
        │   ├── ramya-rao-a
        │   │   └── go-outline
        │   ├── rogpeppe
        │   │   └── godef
        │   └── uudashr
        │       └── gopkgs
        ├── golang.org
        │   └── x
        │       └── tools
        └── gopkg.in
            └── yaml.v2

    29 directories

### TODO

其他的问题发现了再补充