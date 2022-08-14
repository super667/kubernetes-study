
[TOC]

# Redis常见面试题

## redis持久化策略选择

### 1. redis中的RDB备份方式

bgsave开始时，会fork主机进程得到子进程，子进程共享主进程的内存数据，完成fork后读取内存数据并写入RDB文件.
fork采用的是copy-on-write技术：

+ 当主进程执行读操作时，访问共享数据；
+ 当主进程执行写操作时，则会拷贝一份数据，执行写操作。

_根据异步备份流程分析可得，当rdb子进程备份数据较慢时，整个redis服务所占用的内存可以达到所有数据的2倍，部署redis时，应该预留一部分内存给备份时使用。_

![vartar](images/redis-rdb.png)

RDB**触发条件**

+ 手动触发：save/bgsave
+ 自动触发: 满足redis配置文件中的自动触发条件RDB
+ 自动触发：每次关闭redis也会自动触发RDB
+ 自动触发：执行flushall命令也会自动触发RDB

redis**配置文件**

```bash
save 60 1000  # 每60秒内有1000次修改触发RDB
```

RDB**触发命令**

```bash
save        # save命令会阻塞redis服务的正常进程,直到RDB创建文件结束
bgsave      # bgsave会fork一个子进程,父进程继续处理了请求,不会影响redis服务,但是此时会拒绝客户端发送的save或bgsave命令,避免重复执行,竞争资源
flushall    # 用于清空整个redis服务器的数据
```

### 2. redis中的AOF备份方式

备份过程

触发命令

redis配置文件

```bash
appendonly yes
```

## 3. 过期key处理策略

Redis的所有数据都可以设置过期时间，时间一到自动删除

### 过期的key集合

redis会将每个设置了过期时间的key放入到一个单独的字典中，以后会定时遍历这个字典来删除到期的key。除了定时遍历之外，还使用了惰性策略来删除过期的key，所谓惰性策略就是在客户端访问到这个key的时候，redis对key的过期时间进行检查，如果过期了就立即删除。定时删除是集中处理，惰性删除是零散处理

+ 定时删除

+ 惰性删除

### 定时扫描策略

Redis默认会每秒进行10次过期扫描，过期扫描不会遍历字典中的所有key,而是采用了一种简单的贪心策略。

```bash
    1.从过期字典中随机选择20个key
    2.删除这20个key中过期的key
    3.如果过期的key比率超过1/4，就重复步骤一
```

同时保证扫描过期不会出现循环过度，导致线程卡死现象，算法还增加了扫描时间上线，默认不会超出25ms.

### 从库的过期策略

从库不会执行过期策略，从库对过期的处理是被动的。主库在key到期时，会在AOF文件里增加一条del指
令，同步到所有的从库，从库通过执行这条del指令来删除过期的key。
 因为指令同步是异步进行的，所以主库过期的key的del指令没有及时同步到从库，会出现主从数据不一致。

## 4. 物理内存超出maxmemory时的淘汰策略 --LRU算法

当Redis内存超出物理内存限制时，内存的数据会开始和磁盘就行频繁的交换(如果swap开启的话)。 交换会让redis的性能急剧下降。
生产环境中redis提供了配置参数maxmemory来限制内存超出期望大小。
当实际使用内存超出maxmemory时，redis提供了几种可选策略，让维护者自己决定如何腾出新的内存空间继续提供读写服务

+ **noevicition：** 服务不会继续处理写请求（del请求可以继续服务），读请求可以继续执行。

+ **volatitle-lru：** 尝试淘汰设置了过期时间的key，最近最少使用的key优先被淘汰。没有设置过期时间的key不会被淘汰，这样可以保证需要持久化的数据不会突然丢失。

+ **volatitle-ttl：** 尝试淘汰设置了过期时间的key, 剩余寿命ttl值越小，越被优先淘汰。

+ **volatitle-random：** 尝试淘汰设置了过期时间的key， 淘汰的key是随机选择的。

+ **allkeys-lru：** 这个淘汰策略的对象是所有的key，最近最少使用优先被淘汰。

+ **allkeys-random：** 这个淘汰策略的对象是所有的key，淘汰的key是随机选择的。

> 如果数据呈现幂律分布，也就是一部分数据访问频率高，一部分数据访问频率低，则使用allkeys-lru
> 如果数据呈现平等分布，也就是所有的数据访问频率都相同，则使用allkeys-random

## 4.redis的部署模式

### 主从模式

### 哨兵模式

#### 哨兵模式工作原理

哨兵集群中每个节点都会启动三个定时任务

1. 每个sentinel节点每隔1s向所有的master、slave、其他sentinel节点发送一个ping命令，作为心跳检测
2. 每个sentinel每隔2s都会向master的__sentinel__:hello这个channel中发送自己掌握的集群信息和自己的一些信息，这个是利用redis的pub/sub功能，每个sentinel节点都会订阅这个channel，也就是说每个sentinel节点都知道别的sentinel节点掌握的集群信息，作用：了解别的sentinel的信息和他们对于主节点的判断
3. 每个sentinel节点每隔10s都会向master和slave发送INFO命令，作用：发现最新的集群拓扑机构

#### 哨兵如何判断master宕机

主观下线

当sentinel节点向master节点发送PING命令，如果超过down-after-milliseconds时间没有收到有效回复，该哨兵节点会认为master节点宕机，也就是sentinel节点认为master节点主观下线(SDOWN),修改其状态为SRI_S_DOWN

客观下线

> 哨兵模式中几个重要参数
> quorum: 如果要认为master客观下线，最少需要主观下线的sentinel节点个数，举例：如果5个sentinel节点，quorum=2，那只要2个sentinel节点主观下线，就可以判断master客观下线
> majority: 如果确定了master客观下线了，就要把其中的一个slave切换成master，做这个是的并不是整个sentinel集群，而是sentinel集群会选出来一个sentinel节点来做，原则就是需要大多数节点都同意这个sentinel来做故障转移才可以，大多数节点就是这个参数。注意：如果sentinel节点个数5，quorum=2，majority=3，那就是三个节点同意就可以，如果quorum=5， majority=3，这时候majority=3就不管用了，需要5个节点都同意才可以。
> configuration epoch: 这个其实就是version，类似于每中国每个皇帝都有一个年号一样，每个master都要生成一个自己的configuration epoch，就是一个编号

客观下线处理过程

1. 每个主观下线的sentinel节点都会向其他sentinel节点发送SENTINEL is-master-down-by-addr ip port current_epoch runid,(ip:主观下线的服务ip，port：主观下线服务的端口，current_epoch: sentinel的纪元，runid：*表示检测服务下线状态，如果是sentinel运行id，表示用来选举领头sentinel)来询问其他sentinel节点是否同意服务下线
2. 每个sentinel收到命令之后，会根据发送过来的ip和端口检查自己判断的结果，如果自己也认为下线了，就会回复，回复包含三个参数： down_state(1表示已下线，0表示未下线)， leader_runid(领头sentinel id)， leader_epoch(领头sentinel纪元)。由于上面发送的runid参数是*， 这里后面两个参数忽略。
3. sentinel收到回复之后，根据quorum的值，判断是否达到这个值，如果大于或等于，就认为这个master客观下线

#### 哨兵如何执行主从切换

选择sentinel leader
到现在为止，已经知道了master客观下线，那么就需要一个sentinel来负责故障转移，sentinel leader节点通过选举实现，具体选举过程如下：

1. 判断客观下线的sentinel节点向其他sentinel节点发送SENTINEL is-master-down-by-addr ip port current_epoch runid(这时的runid是自己的runid， 每个sentinel都有一个自己运行时id)
2. 目标sentinel回复，由于这个leader选举的过程符合先到先得的原则，举例：sentinel1判断了客观下线，向sentinel2发送了第一步中的指令，sentinel2回复了sentinel1，说选你为leader。这时候sentinel3也向sentinel2发送第一步的指令，sentinel2会直接拒绝回复
3. 当sentinel发现选自己的节点数超过了majority的个数时，自己就是领头leader
4. 如果没有一个sentinel达到majority的数量，等一段时间重新选举

故障转移
通过上面的介绍，已经有了领头sentinel，下面就需要做故障转移

1. 剔除不符合作为leader的slave

+ 剔除列表中已经下线的从服务
+ 剔除5s内没有回复sentinel的info命令的从服务
+ 剔除与已经下线的主服务连接断开时间超过down-after-milliseconds*10 + master宕机时长的从服务

2. 选择最合适的slave节点作为master

+ 选择优先级最高的节点，通过sentinel配置文件中的replica-priority配置项，这个参数越小，表示优先级越高
+ 如果第一步中的优先级相同，选择offset最大的，offset表示主节点此昂从节点同步数据的偏移量，越大表示同步的数据越多
+ 如果第二部offset也相同，选择run id较小的

3. 主从切换

+ 领头sentinel向别的slaver发送slaveof命令，告诉他们新的master是谁。
+ 如果之前的master重新上线，领头的sentinel同样会发送slaveof命令，将其变成从节点。

#### 哨兵模式存在的问题

主节点写压力过大

集群脑裂

主从数据不一致

### 集群模式

#### 槽位定位算法

#### 为什么指定16384个槽位

#### 

## 5.雪崩、击穿，穿透

### 雪崩

缓存雪崩表示在某一时间段，缓存集中失效，导致请求全部走数据库，有可能会搞垮数据库，使整个服务瘫痪。

![img](./images/%E7%BC%93%E5%AD%98%E9%9B%AA%E5%B4%A9.png)

缓存集中失效的原因：

1. 缓存中大批量的热点数据过期后，系统涌入大量的查询请求，Redis的数据失效，请求就会渗透到数据库，造成查询阻塞甚至宕机
2. redis宕机

解决方法

1. redis数据永不过期，这种方式是最可靠、最安全的，但是占用空间，内存消耗大，
2. 将缓存失效的时间分散开，比如每个key的过期时间都是随机的。防止同一时间大量数据过期的现象发生，就不会出现同一时间全部请求都落在数据库
3. 因为redis宕机超时缓存雪崩的问题，可以启动服务的熔断机制，暂停业务应用对缓存服务的访问，直接返回错误，但是暂停了业务应用访问缓存系统，全部业务都无法正常工作
4. 创造redis集群，对数据进行读写分离

### 击穿

我们的业务通常会有几个数据被频繁的访问，这类被频繁访问的数据称为热点数据
如果缓存中的某个热点数据过期了，此次大量的请求访问了热点数据，无法从缓存中读取，直接访问数据库，数据库很容易被大量的请求冲垮

![](./images/redis%E7%BC%93%E5%AD%98%E5%87%BB%E7%A9%BF.png)

解决方法：

1. 互斥锁， 保证同一时间只有一个业务线程更新缓存，未能获得互斥锁的的请求，要么等待锁释放后重新读取数据，要么就返回空值和默认值
2. 不给热点数据设置过期时间，由后台异步更新缓存，或者在热点数据过期钱，提前通知后台线程更新缓存以及重新设置过期时间。

### 穿透

缓存穿透是指用户不断的发起请求访问缓存和数据库中都没有的数据，比如发起id为-1或id特别大的不存在的数据，这时用户可能就是攻击者导致数据库压力过大

![vartar](./images/redis%E7%A9%BF%E9%80%8F.png)

解决方法：

1. 接口层增加校验，如用户鉴权校验；id做基础校验，指定接口的请求方式，只接收一种或几种的请求方式
2. 对缓存取不到的数据，在数据库中也没有取到，这时可以将key-value写成key-null，缓存有效时间设置30s，这样可以防止攻击用户反复用同一个id暴力攻击
3. 布隆过滤器

## redis本类型的底层编码结构

### string

### set

### list

### map

### zset

### boom filter

几个哈希函数+位图

## 经常使用场景

1.延时队列，订单信息 zset
2.位图bitmap，打卡
3.缓存
4.分布式锁，string
6.排行榜，zset

## 集群模式

## redis为什么这么快

### 基于内存

### 高效的数据结构

### 单线程模型

> 并发(concurrency): 指在同一时刻只能有一条指令执行，但多个进程进程可以被快速的轮换执行，是的在宏观上具有多个进程同时执行的效果，但在微观上并不是同时执行的，只是把时间分成若干时间段，使多个进程快速交替的执行
> 并行(parallel): 指在同一时刻，有多条指令在多个处理器上同时执行。所以无论从微观上还是从宏观来看，二者都是一起执行的。

> 注意：我们一直说的redis单线程，只是在处理我们的网络请求的时候只有一个线程来处理，一个正式的redis server运行的时候肯定不止一个线程的
> 例如：redis就行持久化的时候会fork一个子进程执行持久化操作

### io多路复用

### 使用底层模型不同

底层实现方式以及客户端时间的应用协议不一样，redis直接自己构建了VM机制，因为一般的系统调用系统函数会浪费一定的时间去移动和请求

vm相关配置
```bash
#开启vm功能
vm-enabled yes
#交换出来的value保存的文件路径
vm-swap-file /tmp/redis.swap
#设置当内存消耗达到上限时开始将value交换出来
vm-max-memory 1000000
#设置单个页面的大小，单位是字节
vm-page-size 32
#设置最多能交换保存多少个页到磁盘
vm-pages 13417728
#设置完成交换动作的工作线程数，设置为0表示不使用工作线程而使用主线程,这会以阻塞的方式来运行。建议设置成CPU核个数
vm-max-threads 4
```

https://blog.csdn.net/Seky_fei/article/details/106843764?spm=1001.2101.3001.6661.1&utm_medium=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-1-106843764-blog-125603596.pc_relevant_default&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-1-106843764-blog-125603596.pc_relevant_default&utm_relevant_index=1
#### VM工作机制1：vm-max-threads=0

数据换出：
数据换入：

#### VM工作机制2：vm-max-threads>0

数据换出：
数据换入：

## redis常见性能问题和解决方案

1. master最好不要写内存快照，

2. 如果数据比较重要某个Slave开启AOF备份数据，策略设置为每秒

3. 为了主从复制的速度和连接的稳定性，Master和Slave最好在同一个局域网

4. 尽量避免在压力很大的主库上增加从库

5. 主从复制不要使用图状结构，使用单向链表更为稳定，即：Master<-Slave1<-Slave2<-Slave3

> 这样的结构方便解决单点故障问题，实现Slave对Master的替换。如果Master挂了，可以立刻开启Slave1做Master，其他不变

## Redis修改配置不重启Redis会实时生效吗？

## redis有哪些适合的场景？

## redis分布式锁

> 分布式锁就是，控制分布式系统不同进程共同访问共享资源的一种锁的实现。如果不同的系统或同一系统的不同主机之间共享了某个临界资源，往往需要互斥锁来防止彼此干扰，以保证一致性

分布式锁的特征

+ 互斥性： 任意时刻，只有一个客户能持有锁
+ 锁超时释放： 持有锁超时，可以释放，防止不必要的资源浪费，也可以防止死锁
+ 可重入性：一个线程如果获取了锁之后，可以再次对其请求加锁
+ 高性能和高可用：加锁和解锁需要开销尽可能低，同时保证高可用，避免分布式锁失效
+ 锁只能被持有的客户端删除，不能被其他客户端删除

使用redis锁的注意事项

1. 不要用于较长时间的任务
2. 

### Redis分布式锁方案1: SET EX PX NX + del

下面的指令就组合成了分布式锁，setnx expire是原子操作。这个实现没有解决超时问题

```bash
> set lock:codehole true ex 5 nx
OK
> do something critical
> del
```

### Redis分布式锁方案2:(超时)SET EX PX NX + 校验唯一随机值，再释放锁

方案1存在的问题：当加锁和释放锁之间的逻辑执行的太长，以致于超出了锁的超时限制，锁被释放。
第二个线程重新持有了这把锁，但是第一个线程执行完了业务逻辑，就把锁释放了。第三个线程会在第二个线程逻辑执行完之前拿到了锁。

解决方法： set指令的value参数设置一个随机数，释放锁时，先匹配随机数是否一致，然后再删除key。但是匹配value和删除key之间不是一个原子操作，redis没有提供类似delifequals这样的指令，这就要使用Lua脚本处理。

```python
tag = random.nextint()
if redis.set(key, tag, nx=True, ex=5):
    do_something()
    redis.delifequals(key, tag)
```

```Lua
# delifequals
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

> Redis使用Lua脚本时为什么能保证原子性？

### Redis分布式锁方案3:(可重入性)

可重入性是指线程再持有锁的情况下再次请求加锁，如果一个线程支持同一个线程的多次加锁，那么这个锁就是可重入的。redis分布式锁如果要支持可重入，需要对客户端的set方法进行包装，使用线程的Threadlocal变量存储当前持有锁的计数

```python
import redis
import threading

locks = threading.local()
locks.redis = {}

def key_for(user_id):
    return "account_{}".format(user_id)

def _lock(client, key):
    return bool(client.set(key, True, nx=True, ex=5))

def _unlock(client, key):
    client.delete(key)

def lock(client, user_id):
    key = key_for(user_id)
    if key in locks.redis:
        locks.redis[key] += 1
        return True
    ok = _lock(client, key)
    if not ok:
        return False
    locks.redis[key] = 1
    return True

def unlock(client, user_id):
    if key in locks.redis:
        locks.redis[key] -= 1
        if locks.redis[key] <= 0:
            del locks.redis[key]
        return True
    return False

client = redis.StrictRedis() 
print "lock", lock(client, "codehole") 
print "lock", lock(client, "codehole") 
print "unlock", unlock(client, "codehole") 
print "unlock", unlock(client, "codehole")
```

### Redis分布式锁方案3:(续期)

**Watchdog** 设计原则

1. 每隔定期时间向redis服务器重新设置锁的过期时间以延长lifetime

2. 当使用锁的用户线程出错时，watchdog也需要停止自动续约以防止其他客户端无法再次获得锁

3. watchdog应当只对用户为主动设置lock_timeout的锁进行自动续约，对用户已经主动设置了改参数的锁不进行续约。

**Watchdog** 实现

基于上述的设计原则，协程是非常好的watchdog实现选型。watchdog协程与用户的工作携程处在同一个线程，当用户的携程出现问题之后，该线程报错，进而也就终止了watchdog的工作，那我watchdog就不会自动续约，锁在一段时间之后就会自动过期

当加锁的时候，用户没有


```python
    #代码有删减
    async def lock(self, resource, lock_timeout=None):
        # 生成锁的标识符
        lock_identifier = str(uuid.uuid4())

        if lock_timeout is not None and lock_timeout <= 0:
            raise ValueError("Lock timeout must be greater than 0 seconds.")

        # 如果用户没有设置锁的lock_timeout， 使用默认的internal_lock_timeout 
        lease_time = lock_timeout or self.internal_lock_timeout
        
        # 尝试向N个Redis实例申请锁太长了就省略掉
        try:
            ...
        except Exception as exc:
            ...
            raise

        lock = Lock(self, resource, lock_identifier, lock_timeout, valid=True)
        # 申请成功后，如果用户没有对锁设置lock_timeout, 则给锁分配watchdog，加入到事件循环中
        if lock_timeout is None:
            self._watchdogs[lock.resource] = asyncio.ensure_future(self._auto_extend(lock))
        self._locks[resource] = lock

        return lock
```

```python
     async def _auto_extend(self, lock):
        # 等待0.6 *self.internal_lock_timeout
        await asyncio.sleep(0.6 * self.internal_lock_timeout)
        try:
            # 尝试延长锁的lifetime
            await self.extend(lock)
        except Exception:
            self.log.debug('Error in extending the lock "%s"',
                           lock.resource)
        # 延长结束之后再把自己加入到事件循环中
        self._watchdogs[lock.resource] = asyncio.ensure_future(self._auto_extend(lock))
```

```python
    async def unlock(self, lock):
        self.log.debug('Releasing lock "%s"', lock.resource)
        
        # 取消掉锁的看门狗
        if lock.resource in self._watchdogs:
            self._watchdogs[lock.resource].cancel()

            done, _ = await asyncio.wait([self._watchdogs[lock.resource]])
            for fut in done:
                try:
                    await fut
                except asyncio.CancelledError:
                    pass
                except Exception:
                    self.log.exception(f"Can not  unlock {lock.resource}")

            self._watchdogs.pop(lock.resource)
        
        # 从Redis实例中删除锁
        await self.redis.unset_lock(lock.resource, lock.id)
        # raises LockError if can not unlock

        lock.valid = False
```

https://zhuanlan.zhihu.com/p/101913195

### 集群环境下redis分布式锁

以上三节详细分析了分布式锁的原理，他的使用比较简单，一条指令就可以完成加锁操作。不过在集群模式下，这种操作是有缺陷的，他不是绝对安全的。
比如在sentinel集群中，主节点挂掉时，从节点取而代之，客户端没有明显感知。原先第一个客户端在主节点中申请成功了一把锁，但是这把锁还没有来得及同步到从节点，主节点突然挂掉了。然后从节点变成了主节点，这个新的节点内部没有这个锁，所以当另一个客户端过来请求加锁时，立即就批准了。这样就会导致系统中同样一把锁被两个客户端同时持有，不安全性由此产生。
不过这种不安全也仅仅是在主从发生 failover 的情况下才会产生，而且持续时间极短，
业务系统多数情况下可以容忍

RedLock算法

为了使用RedLock，需要提供多个Redis实例，这些实例之前相互独立没有主从关系。同很多分布式算法一样，redLock也使用【大多数机制】
加锁时，它会向过半节点发送 set(key, value, nx=True, ex=xxx) 指令，只要过半节点 set成功，那就认为加锁成功。释放锁时，需要向所有节点发送 del 指令。不过 Redlock 算法还需要考虑出错重试、时钟漂移等很多细节问题，同时因为 Redlock 需要向多个节点进行读写，意味着相比单实例 Redis 性能会下降一些。

Redlock使用场景：

优点：

+ 提供高可用

缺点：

+ 需要更多的redis实例
+ 代码上需要引入额外的library，性能下降
+ 运维成本增加


## redis缓存一致性

> CAP原理：

**强一致性：** 保证写入后可以立即读取
**弱一致性：** 不保证可以立刻读到写入的值，而是尽可能的保证在经过一定时间后可以读取到，在弱一致性的场景最为广泛的模型则是最终一致性模型，即保证在一定时间之后写入和读取达到一致的状态

### 方案1：

## Redis使用Lua脚本时为什么能保证原子性

## redis一致性Hash