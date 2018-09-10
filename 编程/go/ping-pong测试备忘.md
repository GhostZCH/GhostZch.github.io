## ping-pong测试备忘

[www.zhaoch.top](http://www.zhaoch.top) > [编程](http://www.zhaoch.top/编程) > [go](http://www.zhaoch.top/编程/go)

## 简单测试了下go的网络io处理能力

### 测试环境

家用i7台式机上建立的虚拟机，４core, 4G mem

### 代码

服务端代码，收到http请求，回复hello go，支持keepalive

    package main

    import (
        "net"
        "log"
    )

    func echoToclient(conn net.Conn) {
        var buf = make([]byte, 4096)
        for {
            var _, err = conn.Read(buf)

            if err != nil {
                conn.Close()
                break
            }

            conn.Write([]byte("HTTP/1.1 200 OK\r\nConnection: Keep-Alive\r\nContent-Length: 9\r\n\r\nhello go!"))
        }
    }


    func main() {
        listener,err := net.Listen("tcp", "0.0.0.0:8080" ) 
        if err != nil {
            log.Fatal(err)
        }
        defer listener.Close() //关闭监听的端口
        for {
            conn,err := listener.Accept() //用conn接收链接
            if err != nil {
                log.Fatal(err)
            }
            go echoToclient(conn)
        }
    }

### 测试

curl 测试功能完整正确

    ➜  ~ curl -vv http://127.0.01:8080/
    * Hostname was NOT found in DNS cache
    *   Trying 127.0.0.1...
    * Connected to 127.0.01 (127.0.0.1) port 8080 (#0)
    > GET / HTTP/1.1
    > User-Agent: curl/7.35.0
    > Host: 127.0.01:8080
    > Accept: */*
    > 
    < HTTP/1.1 200 OK
    < Connection: Keep-Alive
    < Content-Length: 9
    < 
    * Connection #0 to host 127.0.01 left intact
    hello go!%          

ab测试性能

    ➜  ~ ab -c 1000 -n 100000 -k  http://127.0.01:8080/
    This is ApacheBench, Version 2.3 <$Revision: 1528965 $>
    Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
    Licensed to The Apache Software Foundation, http://www.apache.org/

    Benchmarking 127.0.01 (be patient)
    Completed 10000 requests
    Completed 20000 requests
    Completed 30000 requests
    Completed 40000 requests
    Completed 50000 requests
    Completed 60000 requests
    Completed 70000 requests
    Completed 80000 requests
    Completed 90000 requests
    Completed 100000 requests
    Finished 100000 requests


    Server Software:        
    Server Hostname:        127.0.01
    Server Port:            8080

    Document Path:          /
    Document Length:        9 bytes

    Concurrency Level:      1000
    Time taken for tests:   0.525 seconds
    Complete requests:      100000
    Failed requests:        0
    Keep-Alive requests:    100000
    Total transferred:      7100000 bytes
    HTML transferred:       900000 bytes
    Requests per second:    190427.59 [#/sec] (mean)
    Time per request:       5.251 [ms] (mean)
    Time per request:       0.005 [ms] (mean, across all concurrent requests)
    Transfer rate:          13203.48 [Kbytes/sec] received

    Connection Times (ms)
                min  mean[+/-sd] median   max
    Connect:        0    0   0.5      0      14
    Processing:     0    1   1.2      1     201
    Waiting:        0    1   1.2      1     201
    Total:          0    1   1.6      1     212

    Percentage of the requests served within a certain time (ms)
    50%      1
    66%      1
    75%      1
    80%      1
    90%      1
    95%      2
    98%      2
    99%      3

qps在190k, 与之前做过c和python的测试，结果如下

| 语言 | qps |
|--|--|
|go| ≈180k|
|c + epoll | ≈180k |
|python + epoll | ≈10k|
|python + gevent | ≈10k|

在不处理业务的情况下go的性能与c无异，通过控制程序的实现，在业务中达到ｃ/c++ 50%以上的性能是可以的。考虑到开发速度以及提供库的易用性上，后续开发可以考虑使用go代替c/c++作为骨架语言，一些系统接口可以通过ｃ封装提供go调用。
## The End

+ My [github location](https://github.com/GhostZCH/)
+ View Source of this website [GhostZch.github.io](https://github.com/GhostZCH/GhostZch.github.io/)
+ Commit [issues](https://github.com/GhostZCH/GhostZch.github.io/issues) to discuss with me and others
