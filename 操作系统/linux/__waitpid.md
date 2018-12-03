## 主要用于等待子进程结束并或取子进程结束的状态

+ 常用原型 `pid_t waitpid(pid_t pid, int *wstatus, int options);`， options可以指定等待子进程结束还是立即返回
+ wstatus 保存了了进程退出的信号等信息， WTERMSIG(wstatus)，WCOREDUMP(wstatus)用户获取结束时的信号，和是否产生core更多可以参考man page
+ 通常用在mater等待子进程结束，或者在子进程意外退出后获取异常信息

## 示例代码（nginx）

    static void ngx_process_get_status(void)
    {
        int              status;
        char            *process;
        ngx_pid_t        pid;
        ngx_err_t        err;
        ngx_int_t        i;
        ngx_uint_t       one;

        one = 0;

        for ( ;; ) {
            pid = waitpid(-1, &status, WNOHANG);

            if (pid == 0) {
                return;
            }

            if (pid == -1) {
                err = ngx_errno;

                if (err == NGX_EINTR) {
                    continue;
                }

                if (err == NGX_ECHILD && one) {
                    return;
                }

                /*
                * Solaris always calls the signal handler for each exited process
                * despite waitpid() may be already called for this process.
                *
                * When several processes exit at the same time FreeBSD may
                * erroneously call the signal handler for exited process
                * despite waitpid() may be already called for this process.
                */

                if (err == NGX_ECHILD) {
                    ngx_log_error(NGX_LOG_INFO, ngx_cycle->log, err,
                                "waitpid() failed");
                    return;
                }

                ngx_log_error(NGX_LOG_ALERT, ngx_cycle->log, err,
                            "waitpid() failed");
                return;
            }


            one = 1;
            process = "unknown process";

            for (i = 0; i < ngx_last_process; i++) {
                if (ngx_processes[i].pid == pid) {
                    ngx_processes[i].status = status;
                    ngx_processes[i].exited = 1;
                    process = ngx_processes[i].name;
                    break;
                }
            }

            if (WTERMSIG(status)) {
    #ifdef WCOREDUMP
                ngx_log_error(NGX_LOG_ALERT, ngx_cycle->log, 0,
                            "%s %P exited on signal %d%s",
                            process, pid, WTERMSIG(status),
                            WCOREDUMP(status) ? " (core dumped)" : "");
    #else
                ngx_log_error(NGX_LOG_ALERT, ngx_cycle->log, 0,
                            "%s %P exited on signal %d",
                            process, pid, WTERMSIG(status));
    #endif

            } else {
                ngx_log_error(NGX_LOG_NOTICE, ngx_cycle->log, 0,
                            "%s %P exited with code %d",
                            process, pid, WEXITSTATUS(status));
            }

            if (WEXITSTATUS(status) == 2 && ngx_processes[i].respawn) {
                ngx_log_error(NGX_LOG_ALERT, ngx_cycle->log, 0,
                            "%s %P exited with fatal code %d "
                            "and cannot be respawned",
                            process, pid, WEXITSTATUS(status));
                ngx_processes[i].respawn = 0;
            }

            ngx_unlock_mutexes(pid);
        }
    }

## 参考
man waitpid
