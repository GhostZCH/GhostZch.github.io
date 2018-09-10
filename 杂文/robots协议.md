## robots协议

[www.zhaoch.top](http://www.zhaoch.top) > [杂文](http://www.zhaoch.top/杂文)

## robots协议

看下博客的访问日志，偶尔发现有些方位时robots.txt, 原来和爬虫有关，顺手查了下，做个记录。

主要功能时通过在根目录下增加一个robots.txt文件，标示那些路径可以访问，哪些不可以，支持部分通配符

**只是一个协议，没有强制约束**

示例如下

    Disallow: /*?*
    Disallow: /.jpg$
    Disallow:/ab/adc.html
    Allow: /cgi-bin/

参考：

https://baike.baidu.com/item/robots协议/2483797?fr=aladdin&fromid=9518761&fromtitle=robots.txt
## The End

+ My [github location](https://github.com/GhostZCH/)
+ View Source of this website [GhostZch.github.io](https://github.com/GhostZCH/GhostZch.github.io/)
+ Commit [issues](https://github.com/GhostZCH/GhostZch.github.io/issues) to discuss with me and others
