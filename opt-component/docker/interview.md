# Docker

## dockerfile

### 指令

``` bash
FROM        # 指定基础镜像
LABEL       # 为镜像添加标签，当前镜像会继承父镜像的标签，如果与父标签重复，会覆盖之前的标签。
MAINTAINER  # 设置生成镜像的作者
USER        # RUN指令设置用户名或（UID）和可选用户组（或GID），用于运行Dockerfile中接下来的RUN、CMD、ENTRYPOINT指令。
 COPY        # COPY 指令和 ADD 指令的唯一区别在于：是否支持从远程URL获取资源。COPY 指令只能从执行 docker build 所在的主机上读取资源并复制到镜像中。而 ADD 指令还支持通过 URL 从远程服务器读取资源并复制到镜像中。
RUN         # 在当前镜像层之上的新层执行命令，并且提交结果
CMD         # 使用镜像创建容器，并运行容器执行的命令；只有最后一个生效；
ENTRYPOINT  # ENTRYPOINT和CMD一样，都是在指定容器启动程序以及参数，不会它不会被docker run的命令行指令所覆盖。如果要覆盖的话需要通过docker run --entrypoint来指定。
ENV         # 设置环境变量，这个环境变量可以在后续任何RUN命令中使用，并在容器运行时保持
ARG         # 定义用户只在构建时使用的变量，不会保留在镜像中
WORKDIR     # WORKDIR指令为Dockerfile中接下来的RUN、CMD、ENTRYPOINT、ADD、COPY指令设置工作目录。
EXPOSE      # 通知容器运行时映射端口
VOLUME      # 创建一个具有指定名称的挂载数据卷
ONBUILD     # ONBUILD指令作为触发指令添加到镜像中，只有在该镜像作为基础镜像时执行。触发器将在下游构建的Dockerfile中的FROM指令之后执行。如果任何触发器失败，FROM指令将中止，从而导致生成失败。如果所有触发器都成功，FROM指令将完成，构建将照常继续。
STOPSIGNAL  # 设置容器退出时唤起的系统调用信号。该信号可以是与内核系统调用表中的位置匹配的有效无符号数字，例如9，或格式为SIGNAME的信号名称，如SIGKILL。
HEALTHCHECK # 
```

**STOPSIGNAL：** 默认的stop-signal是SIGTERM，在docker stop的时候会给容器内PID为1的进程发送这个信号，通过--stop-signal可以设置需要的signal，主要用于让容器内的程序在接收到signal之后可以先处理些未完成的事务，实现优雅结束进程后退出容器。如果不做任何处理，容器将在一段时间后强制退出，可能会造成业务强制中断，默认时间是10s。

### 构建镜像的时候需要注意什么？

构建镜像有两种方式

1. 编写dockerfile文件

```bash
docker build -t docker.io/nginx:latest .
```

2. 使用现有的容器container容器提交镜像

```bash
docker container commit [OPTIONS] CONTAINER [REPOSITORY[:TAG]]
```