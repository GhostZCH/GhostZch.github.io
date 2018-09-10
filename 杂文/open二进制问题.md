## open二进制问题

[www.zhaoch.top](http://www.zhaoch.top) > [杂文](http://www.zhaoch.top/杂文)

## 打开文件w,r, 与wb,rb的区别

与具体语言无关，与操作系统相关，以下来自ubuntu的`man fopen`的内容:

    The mode string can also include the letter 'b' either as a last character or  as  a  character
    between  the  characters in any of the two-character strings described above.  This is strictly
    for compatibility with C89 and has no effect; the 'b' is ignored on all POSIX  conforming  sys‐
    tems,  including  Linux.  (Other systems may treat text files and binary files differently, and
    adding the 'b' may be a good idea if you do I/O to a binary file and expect that  your  program
    may be ported to non-UNIX environments.)

这里只说明了linux会忽略b选项，也就是wb,rb等同于w,r但是不确定其他操作系统的操作

经过测试和查资料发现在windows上有如下不同

+ w 会将 \n 转换成 \r\n 而wb不会
+ r 会将 \r\n 转换成 \n 而rb不会（未测试）

所以建议二进制读写都设置b选项

## The End

+ My [github location](https://github.com/GhostZCH/)
+ View Source of this website [GhostZch.github.io](https://github.com/GhostZCH/GhostZch.github.io/)
+ Commit [issues](https://github.com/GhostZCH/GhostZch.github.io/issues) to discuss with me and others
