# Linux基础知识

## IO多路复用

## 写实复制

## MMAP机制

### 虚拟内存

虚拟内存是操作系统为了方便操作对物理内存做的抽象，他们之间是靠页表（Page Table）进行关联的，关联关系如下

![virtualmem](/linux/images/virtualmem.png)

每个页表都有自己的pagetable，进程的虚拟内存地址通过pagetable对应于物理内存，

### 内存映射MMAP

![mmapmem](/linux/images/mmapmem.png)

当使用mmap的方式发送磁盘中的文件到网卡时的流程如下：

1. 用户进程通过系统调用mmap函数进入内核态，发生一次上下文切换，并建立内核缓冲区；
2. 若发生缺页中断，CPU通知DMA读取数据，DMA拷贝数据到物理内存，并建立内核缓冲区和物理内存的映射关系；
3. 建立用户空间的进程缓冲区和同一块内存的映射关系，由内核态转换为用户态，发生第二次上下文切换；
4. 用户进程进行逻辑处理后，通过系统调用socket send，用户态进入内核态，发生第三次上下文切换；
5. 系统调用send创建网络缓冲区，并拷贝内核中的读缓冲区数据；
6. DMA控制器将网络缓冲区的数据发送网卡，并返回，由内核态进入用户态，发生第四次上下文切换；

## IO调度机制

## 常用命令总结

### ps

## 零拷贝

零拷贝是指将数据直接从磁盘文件复制到网卡设备中，而不需要经由应用程序，大大提高了应用程序的性能，减少了内核和用户态之间的上下文切换。

> 零拷贝技术：
> 零拷贝技术依赖于底层的sendfile()方法的实现
> 正常情况下将一个静态文件A发动出去需要在一个进程调用两次函数
>
> read(file, tmp_buf, len);
> write(socket, tmp_buf, len);
>
> 这个过程，文件A经历了四次复制
>
> + 调用read方法时，文件A中的内容复制到了内核模式下的Read Buffer中。
>
> + CPU控制将内核模式数据复制到用户模式下。
> + 调用write时，将用户模式下的内容复制到内核模式下的socket Buffer中。
> + 将内核模式下的socket buffer的数据复制到网卡设备中

>![image](/opt-component/%E6%B6%88%E6%81%AF%E9%98%9F%E5%88%97/images/%E9%9D%9E%E9%9B%B6%E6%8B%B7%E8%B4%9D%E6%8A%80%E6%9C%AF.png)
>
>
>![image](/opt-component/%E6%B6%88%E6%81%AF%E9%98%9F%E5%88%97/images/%E9%9B%B6%E6%8B%B7%E8%B4%9D%E6%8A%80%E6%9C%AF.png)
> 零拷贝技术通过DMA技术将文件内容复制到内核模式下的Read Buffer中。不过没有数据被复制到Socket Buffer中，只把包含数据的位置和长度信息的文件描述符加载到Socket Buffer中。DMA引擎直接将数据从内核模式中传递到网卡设备。这里数据只经历了2次复制就从磁盘中传送出去。上下文切换也变成了2次。

>| IO方式                |   系统调用         |  CPU拷贝  | DMA拷贝  | 上下文切换  |
>|-----------------------|-------------------|----------|----------|------------|
>| traditional IO        |  read/write       |    2     |    2     |      4     |
>| map                   |  mmap/write       |    1     |    2     |      4     |
>| sendfile              |  sendfile         |    1     |    2     |      2     |
>| Sendfile + DMA gather |  sendfile         |    0     |    2     |      2     |
>| splice                |  splice           |    0     |    2     |      2     |
>| tee                   |  tee              |    0     |    2     |      2     |

## TCP

**1．为什么建立连接协议是三次握手，而关闭连接却是四次握手呢？**

这是因为服务端的LISTEN状态下的SOCKET当收到SYN报文的建连请求后，它可以把ACK和SYN（ACK起应答作用，而SYN起同步作用）放在一个报文里来发送。但关闭连接时，当收到对方的FIN报文通知时，它仅仅表示对方没有数据发送给你了；

但未必你所有的数据都全部发送给对方了，所以你可以未必会马上会关闭SOCKET,也即你可能还需要发送一些数据给对方之后，再发送FIN报文给对方来表示你同意现在可以关闭连接了，所以它这里的ACK报文和FIN报文多数情况下都是分开发送的。

**2．为什么TIME_WAIT状态还需要等2MSL后才能返回到CLOSED状态？**

这是因为虽然双方都同意关闭连接了，而且握手的4个报文也都协调和发送完毕，按理可以直接回到CLOSED状态（就好比从SYN_SEND状态到ESTABLISH状态那样）：

一方面是可靠的实现TCP全双工连接的终止，也就是当最后的ACK丢失后，被动关闭端会重发FIN，因此主动关闭端需要维持状态信息，以允许它重新发送最终的ACK。

另一方面，但是因为我们必须要假想网络是不可靠的，你无法保证你最后发送的ACK报文会一定被对方收到，因此对方处于LAST_ACK状态下的SOCKET可能会因为超时未收到ACK报文，而重发FIN报文，所以这个TIME_WAIT状态的作用就是用来重发可能丢失的ACK报文。

TCP在2MSL等待期间，定义这个连接(4元组)不能再使用，任何迟到的报文都会丢弃。设想如果没有2MSL的限制，恰好新到的连接正好满足原先的4元组，这时候连接就可能接收到网络上的延迟报文就可能干扰最新建立的连接。

**3、发现系统存在大量TIME_WAIT状态的连接，可以通过调整内核参数解决** 

```bash
# vi /etc/sysctl.conf 加入以下内容：
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_fin_timeout = 30
# 然后执行 /sbin/sysctl -p 让参数生效。
# net.ipv4.tcp_syncookies = 1 表示开启SYN Cookies。当出现SYN等待队列溢出时，启用cookies来处理，可防范少量SYN攻击，默认为0，表示关闭；
# net.ipv4.tcp_tw_reuse = 1 表示开启重用。允许将TIME-WAIT sockets重新用于新的TCP连接，默认为0，表示关闭；
# net.ipv4.tcp_tw_recycle = 1 表示开启TCP连接中TIME-WAIT sockets的快速回收，默认为0，表示关闭。
# net.ipv4.tcp_fin_timeout 修改系統默认的 TIMEOUT 时间
```