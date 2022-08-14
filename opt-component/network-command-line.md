# 网络排查命令总结

## tcpdump抓包

```bash
host tcp and host 10.4.7.60 and port 80
```

## tcpdump常用相关参数

### 技巧一

- **-W：** 生成的循环文件数量，生成到最大数量后，新的报文数据会覆盖写入第一个文件，以此类推
- **-C:** 每个文件的大小，单位是MB。
- **-G:** 每次新生成文件的间隔时间，单位是分钟
- **-s:** 可以指定抓包的长度
- **-w:** 指定文件路径

下面这个例子。

```bash
# 每100MB或者60分钟（满足任一条件即可）就生成一个文件，一共10个文件
tcpdump -i eth0 -w file.pcap -W 10 -C 100 -G 60
# 抓取从二层到四层的报文头部，不带TCP Options
tcpdump -s 54
# 抓取所有TCP Options，对排查TCP行为足够用
tcpdump -s 74
tcpdump -i any
tcpdump -i virbr1
tcpdump -i virbr1 port 80
tcpdump -i virbr1 tcp port 80
tcpdump -i virbr1 udp port 80
tcpdump -i virbr1 tcp port 80 -w /tmp/grafana.cap
tcpdump -i any tcp port 80 and host 8.8.8.8
tcpdump -i any host 8.8.8.8 -n
tcpdump host 10.4.7.200
tcpdump src 10.4.7.200
tcpdump dst 10.4.7.200
tcpdump udp
tcpdump tcp
tcpdump -i any tcp and not port 22

```

如果要对应用层的头部（比如HTTP头部）也进行抓取，那可以设置更大的-s参数值。整体来说，这样的抓包文件，要比抓满的情况（1514字节）小很多

> 补充： 1514字节是网络层MTU的1500字节，加上帧头的14字节。所以
> 一般不指定-s参数的抓包文件，其满载的帧大小就是1514字节

## openssl使用技巧

```bash
curl -vk https://www.baidu.com
openssl s_client -connect sharkfesteurope.wireshark.org:443
```
