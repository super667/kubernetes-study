[TOC]

# Prometheus使用

## Prometheus命令行格式

## prometheus数据类型

+  Gauges：最简单、使用最多的指标，获取一个返回值，这个返回值没有变化规律，不能肯定它一定是增长或是减少的状态，采集回来是多少就是多少。比如硬盘容量、CPU内存使用率都适合使用Gauges数据类型。
+ Counters: 计数类型。数据在理想状态下应该是从0开始永远递增或者是不变。比如系统运行时间、HTTP访问量等。这类型的数据通常要借助rate、irate、topk、increase等函数来获取一个变化状态，如增长率。
+ Histograms：可以理解为柱状图的意思，常用于跟踪事件发生的规模，例如：
+ Summary：

#### Histogram和Summary

**相同点：**
都包含 \<basename\>_sum,\<basename\>_count
Histogram需要通过\<basename\>_bucket计算quantile，而summary直接存储了quantile值。

**选择：** Summary结构有频繁的全局锁操作，对高并发程序性能存在一定影响。histogram仅仅是给每个桶做一个原子变量的计数就可以了，而summary要每次执行算法计算出最新的X分位value是多少，算法需要并发保护。会占用客户端的cpu和内存。
summary的百分位是提前在客户端里指定的，在服务端观测指标数据时不能获取未指定的分为数。而histogram则可以通过promql随便指定，虽然计算的不如summary准确，但带来了灵活性。
histogram不能得到精确的分为数，设置的bucket不合理的话，误差会非常大。会消耗服务端的计算资源。

**两条经验**
如果需要聚合（aggregate），选择histograms。
如果比较清楚要观测的指标的范围和分布情况，选择histograms。如果需要精确的分为数选择summary。

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
prometheus_http_requests_total{handler=~"/graph|/rules|/metrics"}
```

### 3.数值过滤

标签过滤之后就是数值的过滤

```bash
# 找出 wait_connection数量 ⼤于200的 
count_netstat_wait_connections{exported_instance=~"web.*"} > 200
```

### 4.时间范围查询

```bash
prometheus_http_requests_total{handler="/-/reload", code="200"}[5m]
```

+ s-秒
+ m-分钟
+ h-小时
+ d-天
+ w-周
+ y-年

在时间序列的查询上，除了以当前时间为基准，也可以使用offset进行时间位移的操作。如以一小时前的时间点为基准，查询瞬时向量和5分钟内的范围向量。

### 5.聚合操作

PromQL语言提供了不少内置的聚合操作，用于对瞬时向量的样本进行聚合操作，形成一个新的序列。

+ sum(求和)
+ min(最小值)
+ max(最大值)
+ avg(平均值)
+ stddev(标准差)
+ stdvar(标准方差)
+ count(计数)
+ topk(前n条时序)
+ quantile(分位数)

sum(prometheus_http_requests_total{}) without(code, handler, job)
sum(prometheus_http_requests_total{} by (instance)

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
sum(increase(node_cpu_seconds_total{mode="idle"}[1m])) by (instance)
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

## prometheus服务发现方式

### 静态服务发现

```
- job_name: "nodes"
# metrics_path defaults to '/metrics'
# scheme defaults to 'http'.
    static_configs:
     - targets:  
        - 10.99.31.206:9100
        - 10.99.31.201:9100
        - 10.99.31.202:9100
```

### file_sd_configs

yaml格式

```
- targets: ['192.168.1.220:9100']
  labels:
    app:    'app1'
    env:   'game1'
    region: 'us-west-2'
- targets: ['192.168.1.221:9100']
  labels:
    app:    'app2'
    env:   'game2'
    region: 'ap-southeast-1'
```

json格式

```
[
  {
    "targets": [ "192.168.1.221:29090"],
    "labels": {
      "app": "app1",
      "env": "game1",
      "region": "us-west-2"
    }
  },
  {
    "targets": [ "192.168.1.222:29090" ],
    "labels": {
      "app": "app2",
      "env": "game2",
      "region": "ap-southeast-1"
    }
  }
]
```

创建prometheus配置文件/data/promtheus/conf/prometheus-file-sd.yml
Prometheus默认每5min重新读取一次文件内容，当需要修改时，可以通过refresh_interval进行设置，例如：

```bash
  - job_name: 'file_sd_test'
    scrape_interval: 10s
    file_sd_configs:
    - refresh_interval: 30s # 30s重载配置文件,prometheus会周期性的读取文件中的内容。
      files:
      - /data/prometheus/static_conf/*.yml
      - /data/prometheus/static_conf/*.json
```

### eureka_sd_config

```
prometheus.yml 配置
global:
  scrape_interval:     10s
  evaluation_interval: 10s
scrape_configs:
  - job_name: eureka
    metrics_path: /metrics
    eureka_sd_configs:
    - server: <your eureka address>/eureka
```

### 基于console的服务发现


### kubernetes_sd_configs


https://www.cnblogs.com/sfnz/p/15619240.html