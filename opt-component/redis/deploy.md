# redis部署

## 主从模式

## sentinel模式

## 集群模式搭建

```bash
[root@hdss7-200 redis]# cat redis-cluster/Procfile
# Use goreman to run `go get github.com/mattn/goreman`
# Change the path of bin/etcd if etcd is located elsewhere
# A learner node can be started using Procfile.learner
redis1: /opt/data/centos-7-51/redis/redis-6.0.0-src/src/redis-server /opt/data/centos-7-51/redis/redis-cluster/redis01/redis.conf
redis2: /opt/data/centos-7-51/redis/redis-6.0.0-src/src/redis-server /opt/data/centos-7-51/redis/redis-cluster/redis02/redis.conf
redis3: /opt/data/centos-7-51/redis/redis-6.0.0-src/src/redis-server /opt/data/centos-7-51/redis/redis-cluster/redis03/redis.conf
redis4: /opt/data/centos-7-51/redis/redis-6.0.0-src/src/redis-server /opt/data/centos-7-51/redis/redis-cluster/redis04/redis.conf
redis5: /opt/data/centos-7-51/redis/redis-6.0.0-src/src/redis-server /opt/data/centos-7-51/redis/redis-cluster/redis05/redis.conf
redis6: /opt/data/centos-7-51/redis/redis-6.0.0-src/src/redis-server /opt/data/centos-7-51/redis/redis-cluster/redis06/redis.conf
```

```bash
# 启动redis服务
goreman -f /opt/data/centos-7-51/redis/redis-cluster/Procfile start
```

```bash
# 配置redis集群模式
[root@hdss7-200 redis]# redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 127.0.0.1:7006 --cluster-replicas 1
>>> Performing hash slots allocation on 6 nodes...
Master[0] -> Slots 0 - 5460
Master[1] -> Slots 5461 - 10922
Master[2] -> Slots 10923 - 16383
Adding replica 127.0.0.1:7005 to 127.0.0.1:7001
Adding replica 127.0.0.1:7006 to 127.0.0.1:7002
Adding replica 127.0.0.1:7004 to 127.0.0.1:7003
>>> Trying to optimize slaves allocation for anti-affinity
[WARNING] Some slaves are in the same host as their master
M: 3769d38acb98c7ca1e80a6b5e78ef40c8c611960 127.0.0.1:7001
   slots:[0-5460] (5461 slots) master
M: eef06ae5b15194747ffd3829eedb1e524c241220 127.0.0.1:7002
   slots:[5461-10922] (5462 slots) master
M: b534ff53963fa4c2767062975d8caa02653f1079 127.0.0.1:7003
   slots:[10923-16383] (5461 slots) master
S: f521df6909068f456d24f94a0929e17c7b3332c4 127.0.0.1:7004
   replicates 3769d38acb98c7ca1e80a6b5e78ef40c8c611960
S: f0e2d02ec531f4b85e83f7150d0ece86125af15b 127.0.0.1:7005
   replicates eef06ae5b15194747ffd3829eedb1e524c241220
S: 7f3a9a4d0dc898a13c604c7f5728f015c3310735 127.0.0.1:7006
   replicates b534ff53963fa4c2767062975d8caa02653f1079
Can I set the above configuration? (type 'yes' to accept): y

```