# Prometheus使用

## Prometheus命令行格式

### 1.精确匹配

```bash
count_netstat_wait_connections{exported_instance="log"}
```

### 2.模糊匹配

```bash
# .*属于正则表达式
# =~ 模糊匹配
# !~ 模糊不匹配
count_netstat_wait_connections{exported_instance=~"web.*"}
```

### 3.数值过滤

标签过滤之后就是数值的过滤

```bash
# 找出 wait_connection数量 ⼤于200的 
count_netstat_wait_connections{exported_instance=~"web.*"} > 200
```

## 常用函数介绍及示例

1.increase()

increase函数在prometheus中，是用来针对Counter这种持续增长的数值，截取其中一段时间的增量。

```bash
# 取得是一分钟内的增量
increase(node_network_receive_bytes[1m]) 
```

2.rate()

rate是取一段时间增量的平均每秒数量

```bash
# 取的是一分钟的增量除以60秒的数量
rate(node_network_receive_bytes[1m])
```

3.sum()

sum函数起到value加和的作用

```bash
# 把收集的所有网卡一分钟之内接收到的数据速率加起来，收集多个机器那就包含多个机器的数据
sum(rate(node_network_receive_bytes[1m]))
```

4.sum(metrics) by (label)

instance函数可以把sum加和到一起的数值按照指定的方式进行一层的拆分，instance代表的是机器名称

```bash
# 查看CPU的空闲率
sum(increase(node_cpu_seconds_totol{mode="idle"}[1m])) by (instance)
# 查看CPU的使用率
(1-sum(rate(node_cpu_seconds_total{mode="idle"}[1m])) by (instance)/sum(rate(node_cpu_seconds_total[1m])) by (instance))* 100 
```

5.topk()

取前几位的最高值

```bash
# 取大的三个值
topk(3, rate(node_network_receive_bytes_total[20m]))
```

6.count

把数值符合条件的输出数目进行加和

```bash
# 找出当前或者历史的TCP等待数大于200的机器数量
count(count_netstat_wait_connections > 200)
```

7.irate

(irate和rate都会用于计算某个指标在一定时间间隔内的变化速率。但是它们的计算方法有所不同：irate取的是在指定时间范围内的最近两个数据点来算速率，而rate会取指定时间范围内所有数据点，算出一组速率，然后取平均值作为结果。
> 所以官网文档说：irate适合快速变化的计数器（counter），而rate适合缓慢变化的计数器（counter）。

根据以上算法我们也可以理解，对于快速变化的计数器，如果使用rate，因为使用了平均值，很容易把峰值削平。除非我们把时间间隔设置得足够小，就能够减弱这种效应。)

## Promethesu报警规则收集

[https://awesome-prometheus-alerts.grep.to/rules#nginx]()