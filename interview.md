[TOC]

# 面试总结

## celery原理

## 部署系统总结

### 为什么做这样一个系统

根据业务需要创建了很多测试环境，每个测试环境都是一个k8s集群，所以面临的是一个多集群管理的问题，

+ 创建yaml文件，由开发使用kubectl去部署
+ 暴露一个统一的部署接口

使用第二种部署方式的优点：

+ 1.测试环境分开发自测环境和测试环境，可以做权限限制

+ 2.开发人员比较多，经常修改并且部署，有可能会有峰值，导致部署失败

+ 3.开发和测试人员也不用学习k8s

+ 4.部署界面可以限制部署的应用，只部署标准应用（）

+ 5.部署前可以检查集群内存，动态扩展节点，减少部署失败次数

+ 6.测试环境的所有配置参数能够集中管理

### 需要解决哪些问题

+ 1.由于测试环境中部署了nginx，使用了confd和etcd作为服务发现去生成nginx的配置文件，而且服务启动也需要一定的时间，整个服务部署操作是比较耗时的，需要创建异步任务去执行。
+ 2.环境挂掉后，能够快速恢复，或者能够快速复制环境，
+ 3.集群中配置的参数能够持久化，比如nodeport，挂载的volume，dnsmasq访问的域名

### 使用了哪些技术，架构实现

选用的celery+django框架

+ **celery：** celery是一个简单灵活，可靠的分布式系统，可用于处理大量消息，
+ **django：** django是一个比较流行的框架，使用python语言开发，基于django，开发效率比较高
+ **kubernetes客户端：** python版本的kubernetes
+ **redis：** 作为缓存和分布式锁
+ **kafka** 定时任务，定时向daemon进程发送请求检查应用的健康状态，服务器的磁盘，执行特殊命令等，执行结果写入kafka，

## redis使用总结

1. 缓存（configapp相关信息）
2. 限流队列，部署的时候
3. 分布式锁，

## k8s二次开发项目

## 代码中的高可用

1. 重试
2. 告警
3. 

## 28所面试题

### 1. 有没有使用redis？
当问到redis的时候，一定要多说，
项目中哪些场景使用到了redis，
当用作缓存的时候需要注意哪些问题？
当使用分布式锁的时候需要注意哪些问题？
限流队列

### 2. 部署的流程？
回答详细点，怎么发起一个部署任务，中间经历了哪些状态，如何确定部署成功
### 3. informer缓存的什么？
### 4. 请求如何向其他环境转发？
服务启动的时候，根据kubernetesPOD中声明周期中的poststart，向etcd注册服务，注册中心，更新nginx的配置文件，nginx根据header转发请求


## 蔚来面试

### 1. celery介绍？
### 2. informer数据结构

## 字节面试

### 1. 工作中有什么重大的事故怎么解决的？
### 2. 如何提升kubernetes集群利用率？（超卖），如何资源分配
### 3. 如果有大量集群节点内核需要升级，怎么整？
按节点，机架，机房粒度去驱逐节点
### 4. 限流的实现？为什么使用限流。 升级令牌桶

### 5. 算法题：两个节点翻转；删除倒数第n个节点


## 寻序人工智能

### 1. 介绍master只要有哪些功能？哪些组件
### 2. kubernetes为什么选择etcd
### 3. 介绍一下django
### 4. calico与flanneld的本质区别?
### 5. k8s POD之间通信流程
### 6. 制作镜像有哪些规范？
### 7. zabbix监控
### 8. docker网络相关
### 9. k8s存储相关，都有哪些持久化方式
### 10. python深拷贝，浅拷贝

## 华为OD面试

### 一面
### 1. crontab相关
### 2. python基础知识
generate生成器，dict原理，可变类型和非可变类型，变量的声明周期，python中相关数据接口
### 3. linux排查问题常用命令
### 4. linux中文件权限相关的
ls、lsattr、setcap
selinux(有空就看)

### 5. 快排算法原理
### 6. copy、deepcopy
### 7. 各个数据接口代码中的使用场景举例（元组）

### 二面

### 1. 熟悉的设计模式
单例模式：整个项目的全局配置文件

工厂模式：我们想要什么对象，提供一个名称，就可以创建响应的类型

策略模式：一种场景，排序算法，不同的算法在子类中实现

模板模式：

建造者模式，

### 2. 项目使用的web框架介绍
### 3. python的垃圾回收机制
https://baijiahao.baidu.com/s?id=1713030534901127703&wfr=spider&for=pc

https://blog.csdn.net/weixin_43662553/article/details/125294885

python的GC模块主要运用了引用计数来跟踪和回收垃圾；通过标记-清除解决容器对象可能产生的循环引用问题；通过分代回收以空间换时间进一步提高垃圾回收的效率

#### 引用计数

为每一个对象维护一个引用计数，当一个对象的引用被创建或者复制时，计数器+1，当一个对象的引用被销毁时，计数器的值-1，当计数器的值为0时，就意味着对象已经z再没有被使用了，可以将内存释放掉
#### 标记-清除

标记清除的出现打破了循环引用，也就是它只关注那些可能会产生循环引用的对象，python中循环引用总是发生在容器container对象之间，也就是在内部能够持有其他对象的对象（比如：list，dict，class等).这也使得该方法带来的开销只依赖容器对象的数量。

原理：将集合对象的引用计数复制一份副本，用于找寻root object集合。当成功找到root object集合，首先将现在的内存链表一分为二，一条链表维护root object集合，成为root链表；另外一条维护剩下的对象，成为unreachable链表。

一旦在标记的过程中，发现现在在unreachable链表可能存在被root链表中直接或间接引用的对象，就将其从unreachable链表中移到root链表中；当完成标记后，unreachable链表剩下的所有对象就是垃圾对象了，接下来的垃圾回收只需限制在unreachable链表即可。

缺点：该机制所带来的额外操作和需要回收的内存块成正比

#### 分代回收

活的越长的对象，就越不可能是垃圾，就应该减少对他的垃圾收集频率。

#### 其他

### 4. 日志处理方式
### 5. 编程题：leetcode 11
### 6. python中变量的生命周期

变量作用域指的是变量的生效范围，python中一共有两种作用域。能够改变变量作用域的关键字class，def，lambda

**全局作用域：** 全局作用域在程序执行时创建，在程序执行结束时销毁。所有函数以外的区域都是全局作用域。在全局作用域中定义的变量，都属于全局变量，全局变量可以在程序的任意位置被访问。

**函数作用域：** 函数作用域在函数调用时创建，在调用结束时销毁。函数每调用一次就会产生一个新的函数作用域（不调用不产生）。在函数作用域中定义的变量，都是局部变量，它只能在函数内部被访问。

**局部变量：** 局部变量是定义在函数体内部的变量，即只在函数体内部生效。

**全局变量：** 所谓全局变量，指的是在函数体内、外都能生效的变量。

**global关键字：** 关键字的作用是，在函数内部声明一个变量为全局变量。换句话说如果希望在函数内部修改全局变量，则需要使用global关键字来声明变量。

**变量的查找：**
当我们使用变量时，会优先在当前作用域中寻找该变量，如果有则使用，如果没有则继续去上一级作用域中寻找，如果有则使用，如果依然没有则继续去上一级作用域中寻找，以此类推。直到找到全局作用域，依然没有找到，则会抛出异常 NameError: name 'a' is not defined。


### 7. 数据库如何排查慢查询语句



### 8. 常使用的python内部支持的库
datetime，time，os，math，json，re, collections

```
import collections
该模块实现了特定目标的容器，提供了python标准内建容器的Dict，list，set，tuple的替代选择
中文文档 
```
import json
import datetime
import time
import math
import re
import os
import sys


## 邮惠万家

高可用相关

### 1. pod创建流程
<img src="./images/pod_create.png" alt="pod_create" style="zoom:150%;" />

### 2. docker构建规范，常用指令

```
FROM 
ADD
COPY
LABEL
ENV
RUN
CMD
ENTRYPOINT
WORKDIR
EXPOSE
VOLUME
```
### 3. web框架介绍
django框架介绍
（1）重量级框架，提供了很多原生的功能组件，例如：
模板语言，表单，文件管理，认证，权限，缓存
（2）MVT模式
（3）强大的数据库功能，几行代码就可以拥有一个丰富，动态的数据库操作接口，如果需要也可以执行SQL语句
（4）自带的强大的后台功能，几行代码让网站拥有一个强大的后台，轻松管理内容
（5）安全性： django非常安全，该框架默认下可以防止XSS攻击，csrf攻击，SQL语句注入，点击劫持，用户管理，cookies,邮件标头注入，密码攻击，目录遍历攻击等

### 4. python与go语言的区别，使用上的差异感悟

|             |  python          |   go      |
|-------------|------------|---------|   
|  范例       |            |         |

1. 范例
pyhton是一种基于面向对象编程的多范式，命令式和函数式编程语言。他坚信这样一种观点，即如果一种语言在某些情境中表现出某种特定的方式，理想情况下他应该在多有情景中有相似的作用。但是，他又部署纯粹的OOP语言，他不支持强封装，这是OPP的主要原则之一。
go是一种基于并发编程凡是的过程编程语言，他与C具有表面相似性。实际上go更像是C的更新版本。

2. 类型化
python是动态类型语言，而go是一种静态类型语言，他实际上有助于在编译时捕获错误，这可以进一步减少生产后期的严重错误。

3. 并发

python没有提供内置的并发机制，而go有内置的并发机制

4. 安全性

5. 管理内存
go允许程序员在很大程度上管理内存。而python中的内存完全自动化并由python VM管理，他不允许程序员对
内存进行管理负责。

6. 库
与GO相比，python提供的库的数量要大得多。然后go仍然是新的，并没有取得很大进展

7. 语法
python的语法使用缩进来指示代码块。go的语法基于打开和关闭括号

8. 详细程度
为了实现相同的功能，golang代码通常要比python多


### 5. nginx里边的配置， upstream配置后面的参数，负载均衡

(1)负载均衡算法

```bash
# 轮询（weight）
upstream bakend {
    server 192.168.1.10 weight=1;
    server 192.168.1.11 weight=2;
}
```

```bash
# ip_hash 每个请求按ip的hash结果分配，这样每个访客固定访问一个后端服务器，可以解决session不能跨服务器的问题。
upstream backend {
	ip_hash
    server 192.168.1.10:8080;
    server 192.168.1.10:8080;
}
```

```bash
# 按后端服务器的响应时间来分配请求，响应时间短的优先分配
upstream resinserver {
    server 192.168.1.10:8080;
    server 192.168.1.11:8080;
    fair;
}
```

```bash
# url_hash 按访问url的hash结果来分配请求，使每个url定向到同一个后端服务器，后端服务器为缓存服务器时比较有效。
upstream resinserver {
    server 192.168.1.10:8080;
    server 192.168.1.11;8080;
    hash $request_uri
    hash_method crc32;
}
```

设备的状态有：
+ （1）down表示当前的server暂时不参与负载
+ （2）weight表示权重，默认为1，weight越大负载的权重越大
+ （3）max_fails: 允许请求失败的次数，默认为1.当超过最大次数时，返回proxy_next_upstream模块定义的错误
+ （4）fail_timeout: max_fails次失败后，暂停的时间；
+ (5)backup：备用服务器，当其他所有的非backup机器down或者忙的时候，请求backup机器，所以这台机器压力最轻。


```bash
# 负载均衡实例
upstream tel_img_stream {
    ip_hash;
    server 192.168.11.68:20201;
    server 192.168.11.69:20201 weight=100 down;
    server 192.168.11.69:20201 weight=100;
    server 192.168.11.69:20201 weight=100 backup;
    server 192.168.11.69:20201 weight=100 max_fails=3 fail_timeout=30s;
}
```

**proxy_next_upstream**

```bash 
# http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_next_upstream
upstream nginxretry {
    server 127.0.0.1:9030 weight=10;
    server 127.0.0.1:9031 weight=10;
}

server {
    listen 9039;
    location / {
        proxy_pass http://nginxretry;
        proxy_next_upstrem err timeout; # 默认值
    }
    location /h {
        proxy_pass http://nginxretry;
        proxy_next_upstrem err timeout http_500;
    }
    # 通常情况下如果请求时非幂等方法(POST, LOCK, PATCH),请求失败后不会再到其他服务器重试。加上non_idempotent选项后，即使是非幂等请求类型(例如POST),发生错误也会重试
    location /g {
        proxy_pass http://nginxretry;
        proxy_next_upstrem err timeout http_500 no_idempotent;
    }
}
```



### 6. celery框架流程
![](./images/celery.webp)

celery组件如下：
Celery Beat:任务调度器
Celery Worker：执行任务的消费者，通常会在多台服务器运行多个消费者来提高执行效率。
Broker： 消息代理， 或者叫做消息中间件，接收任务生产者发送过来的任务消息，存进队列再按照顺序分发给任务消费方（通常是消息队列或者数据库)
Producer：调用了Celery提供的API，函数或者装饰器而产生任务并交给任务队列处理的都是任务生产者
Result Backend: 任务处理完后保存状态信息，以供查询。celery默认已支持redis，Rabbitmq，MongoDB，等方式

### 7. 服务的认证服务jwt，go版本

```
package main

import (
	"fmt"
	"log"
	"time"

	"github.com/golang-jwt/jwt"
)

var mySigningKey = []byte("asfasfdafasdfdasfa.")

func main() {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"name": "wangxianchao",
		"exp":  time.Now().Unix() + 5,
		"iss":  "sywdebug",
	})

	tokenString, err := token.SignedString(mySigningKey)
	if err != nil {
		log.Println(err.Error())
		return
	}
	fmt.Println("加密后的token字符串", tokenString)
	time.Sleep(time.Second * 10)
	//在这里如果也使用jwt.ParseWithClaims的话，第二个参数就写jwt.MapClaims{}
	//例如jwt.ParseWithClaims(tokenString, jwt.MapClaims{},func(t *jwt.Token) (interface{}, error){}

	token, err = jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
		return mySigningKey, nil
	})
	if err != nil {
		log.Println(err.Error())
		return
	}
	fmt.Println("token:", token)
	fmt.Println("token.Claims:", token.Claims)
	fmt.Println(token.Claims.(jwt.MapClaims)["name"])

}
```

### 8. 常用的设计模式

1. 单例模式

```python
class Singleton(object):
    def __int__(self):
        pass

    def __new__(cls, *arg, **kwargs):
        if not hasattr(Singleton, "_instance"):
            Singletom._instance = object.__new__(cls)
        return Singleton._instance

obj1 = Singleton()
obj2 = Singleton()
```

2. 简单工厂模式

   工厂模式是软件开发中用来创建对象的设计模式。

   工厂模式包含一个超类，这个类提供一个接口来创建特定类型的对象，而不是决定哪个对象可以被创建。

   

   ```python
   # encoding: utf-8
   import math
   
   
   # 现金收费基类
   class CashSuper(object):
       def accept_cash(self, money):
           raise NotImplementedError
   
   
   # 正常收费子类
   class CashNormal(CashSuper):
       def accept_cash(self, money):
           return money
   
   
   # 打折收费子类
   class CashRebate(CashSuper):
       def __init__(self, rebate=1.0):
           self._rebate = rebate
   
       def accept_cash(self, money):
           return money * self._rebate
   
   
   # 返利收费子类
   class CashReturn(CashSuper):
       def __init__(self, condition=0, money_return=0):
           self._condition = condition
           self._return = money_return
   
       def accept_cash(self, money):
           result = money
           if money >= self._condition:
               result = money - math.floor(money / self._condition) * self._return
           return result
   
   
   # 现金收费工厂类
   class CashFactory(object):
       @staticmethod
       def create_cash_accept(cash_type):
           cash_type_instance = None
           if cash_type == '正常收费':
               cash_type_instance = CashNormal()
           elif cash_type == '打8折':
               cash_type_instance = CashRebate(0.8)
           elif cash_type == '满300返100':
               cash_type_instance = CashReturn(300, 100)
           return cash_type_instance
   
   
   if __name__ == '__main__':
       print CashFactory.create_cash_accept('正常收费').accept_cash(400)
       print CashFactory.create_cash_accept('打8折').accept_cash(400)
       print CashFactory.create_cash_accept('满300返100').accept_cash(400)
   ```

   

3. 策略模

   ```python
   # encoding: utf-8
   import math
   
   
   # 现金收费基类
   class CashSuper(object):
       def accept_cash(self, money):
           raise NotImplementedError
   
   
   # 正常收费子类
   class CashNormal(CashSuper):
       def accept_cash(self, money):
           return money
   
   
   # 打折收费子类
   class CashRebate(CashSuper):
       def __init__(self, rebate=1.0):
           self._rebate = rebate
   
       def accept_cash(self, money):
           return money * self._rebate
   
   
   # 返利收费子类
   class CashReturn(CashSuper):
       def __init__(self, condition=0, money_return=0):
           self._condition = condition
           self._return = money_return
   
       def accept_cash(self, money):
           result = money
           if money >= self._condition:
               result = money - math.floor(money / self._condition) * self._return
           return result
   
   
   # 上下文类，维护一个对收费模型的引用
   class CashContext(object):
       def __init__(self, cash_type_instance):
           self.cash_type_instance = cash_type_instance
   
       def get_result(self, money):
           return self.cash_type_instance.accept_cash(money)
   
   
   if __name__ == '__main__':
       def init_cash_accept(cash_type):
           cash_content = None
           if cash_type == '正常收费':
               cash_content = CashContext(CashNormal())
           elif cash_type == '打8折':
               cash_content = CashContext(CashRebate(0.8))
           elif cash_type == '满300返100':
               cash_content = CashContext(CashReturn(300, 100))
           return cash_content
   
       print init_cash_accept('正常收费').get_result(400)
       print init_cash_accept('打8折').get_result(400)
       print init_cash_accept('满300返100').get_result(400)
   
   
   ```

   4.工厂模式和策略模式结合

   ```python
   # encoding: utf-8
   import math
   
   
   # 现金收费基类
   class CashSuper(object):
       def accept_cash(self, money):
           raise NotImplementedError
   
   
   # 正常收费子类
   class CashNormal(CashSuper):
       def accept_cash(self, money):
           return money
       
       def CashType():
           return "正常收费"
   
   
   # 打折收费子类
   class CashRebate(CashSuper):
       def __init__(self, rebate=1.0):
           self._rebate = rebate
   
       def accept_cash(self, money):
           return money * self._rebate
       
       def CashType():
           return "打8折"
   
   
   # 返利收费子类
   class CashReturn(CashSuper):
       def __init__(self, condition=0, money_return=0):
           self._condition = condition
           self._return = money_return
   
       def accept_cash(self, money):
           result = money
           if money >= self._condition:
               result = money - math.floor(money / self._condition) * self._return
           return result
       
       def CashType():
           return "满300返100"
   
   
   # 上下文类，维护一个对收费模型的引用
   class CashContext(object):
       def __init__(self, cash_type):
           self._cash_type = cash_type
           self.cash_type_instance = None
           self.init_cash_accept()
           self.cash_type_instance_list = []
   
       def init_cash_accept(self):
           if self._cash_type == '正常收费':
               self.cash_type_instance = CashNormal()
           elif self._cash_type == '打8折':
               self.cash_type_instance = CashRebate(0.8)
           elif self._cash_type == '满300返100':
               self.cash_type_instance = CashReturn(300, 100)
               
       def add_cash_type_instance(cash_type):
           if isinstance(cash_type, CashSuper):
               self.cash_type_instance_list.append(cash_type)
           else:
               pass
   
       def get_result(self, money):
           return self.cash_type_instance.accept_cash(money)
   
   
   if __name__ == '__main__':
       print CashContext('正常收费').get_result(400)
       print CashContext('打8折').get_result(400)
       print CashContext('满300返100').get_result(400)
   ```

   

   

### 9. 设计模式六大原则
https://www.cnblogs.com/huansky/p/13700861.html

1. 单一职责原则

```
对于一个类而言，应该仅有一个引起他变化的原因。否则就应该把多余的职责分离出去，再去创建一些类来完成每一个职责。
单一职责原则是实现高内聚低耦合的最好方法，没有之一。
```
该原则提出对象不应该承担太多职责，如果一个对象承担了太多的职责，至少存在以下两个缺点：
+ 一个职责的变化可能会削弱或者抑制这个类实现其他职责的能力；
+ 当客户端需要该对象的某一个职责时，不得不将其他不需要的职责全都包含进来，从而造成冗余代码或代码的浪费。

单一职责的优点：

+ 降低类的复杂度。一个类只负责一项职责，其逻辑肯定要比负责多项职责简单得多。
+ 提高类的可读性。复杂性降低，自然其可读性会提高。
+ 提高系统的可维护性。可读性提高，那自然更容易维护了。
+ 变更引起的风险降低。变更是必然的，如果单一职责原则遵守得好，当修改一个功能时，可以显著降低对其他功能的影响。

2. 开闭原则

```
一个软件实体如类，模块和函数应该对扩展开放，对修改关闭。目的是为了保护程序的扩展性，
易于维护和升级
开闭原则被称为面向对象设计的基石，实际上，其他原则都可以看做是实现开闭原则的工具和手段。意思就是：软件对扩展应该是开放的，对修改是封闭的，通俗来说就是，开发一个软件时，应该对其进行功能扩展，不需要对原来的程序进行修改
好处：软件可用性非常灵活，扩展性强。需要新的功能时，可以增加新的模块来满足新需求。另外由于原来的模块没有修改，所以不用担心稳定性的问题。
```


3. 里氏代换原则

子类可以扩展父类的功能，但是不能改变父类原有的功能

```
在第一条原则开放封闭原则中，主张“抽象”和“多态”。维持设计的封装性“抽象”是语言提供的功能，“多态”由继承语意实现。因此如何去度量继承关系中的质量？

答案是：继承必须明确确保超类（父类）所拥有的性质在子类中仍然成立。

在面向对象的思想中，一个对象就是一组状态和一系列行为的组合体。状态是对象的内在特性，行为是对象的外在特性。LSP表述的就是在同一继承体系中的队形应该具有共同的行为特征。
```
4. 依赖倒置原则

是一个类与类之间的调用规则。这里的依赖就是代码中的耦合。高层模块不应该依赖底层模块，二者都应该依赖其抽象；抽象不依赖细节；细节应该依赖抽象

```
主要思想：如果一个类中的成员或者参数成为一个具体的类型，那么这个类就依赖这个具体的类型。如果在一个继承结构中，上层类中的一个成员或者参数为下一层类型，那么就是这个继承结构高层依赖底层，就要尽量面向抽象或者面向接口编程
```

作用：
+ 依赖倒置原则可以降低类间的耦合性
+ 依赖倒置原则可以提高系统的稳定性
+ 依赖倒置原则可以减少并行开发引起的风险
+ 依赖倒置原则可以提高代码的可读性和可维护性

实现方法：
+ 底层模块尽量都要有抽象类或接口，或者两者都有
+ 变量的声明类型尽量是抽象类或者接口
+ 任何类都不应该从具体类派生
+ 继承时遵循里氏替换原则

5. 接口隔离原则

接口隔离原则要求程序员尽量将臃肿庞大的接口拆分成更小的和更具体的接口，让接口中只包含客户感兴趣的方法。

2002 年罗伯特·C.马丁给“接口隔离原则”的定义是：客户端不应该被迫依赖于它不使用的方法（Clients should not be forced to depend on methods they do not use）。该原则还有另外一个定义：一个类对另一个类的依赖应该建立在最小的接口上（The dependency of one class to another one should depend on the smallest possible interface）。
以上两个定义的含义是：要为各个类建立它们需要的专用接口，而不要试图去建立一个很庞大的接口供所有依赖它的类去调用。

接口隔离原则和单一职责都是为了提高类的内聚性、降低它们之间的耦合性，体现了封装的思想，但两者是不同的：
+ 单一职责原则注重的是职责，而接口隔离原则注重的是对接口依赖的隔离
+ 单一职责主要是约束类，她针对的是程序中的实现和细节；接口隔离原则主要是约束接口，主要针对抽象和程序整体框架的构建

接口隔离原则的优点：
接口隔离原则是为了约束接口、降低类对接口的依赖性，遵循接口隔离原则有以下 5 个优点。
+ 将臃肿庞大的接口分解为多个粒度小的接口，可以预防外来变更的扩散，提高系统的灵活性和可维护性。
+ 接口隔离提高了系统的内聚性，减少了对外交互，降低了系统的耦合性。
+ 如果接口的粒度大小定义合理，能够保证系统的稳定性；但是，如果定义过小，则会造成接口数量过多，使设计复杂化；如果定义太大，灵活性降低，无法提供定制服务，给整体项目带来无法预料的风险。
+ 使用多个专门的接口还能够体现对象的层次，因为可以通过接口的继承，实现对总接口的定义。
+ 能减少项目工程中的代码冗余。过大的大接口里面通常放置许多不用的方法，当实现这个接口的时候，被迫设计冗余的代码。

6. 迪米特原则

```
LAW of Demeter(最小知识原则)：一个对象应该对其他对象有最少的了解。通俗来说就是，一个类对自己需要耦合或者调用的类知道的最少，你类内部怎么复杂，那是你的事，我只知道你有那么多公用的方法我能调用。
迪米特原则核心观念就是：类间解耦，弱耦合。
```



### 10. 服务是自己完全开发的，与开源软件的区别

### 11. go的web框架（有时间看一个）

### 12. django与其他web服务的区别
web开发是python的应用领域之一，其包含着各种各样的开发框架，比如说django，flask，tornado等，这三个框架有什么区别呢？
django和flask对比：
flask是小而精的微框架，他不像django那样大而全，如果使用flask开发，开发者需要自己决定使用哪个数据库orm、模块系统，用户认证系统等。
与falsk相比，开发者在项目开始的时候可能需要花费更多的时间去了解挑选各个组件，开发者可以根据自己的需要去选择合适的插件。
django与Tornado框架的对比：
Tornado是一个Python Web框架和异步网络库，最初由FriendFeed 开发，其设计目的主要是为了解决10000个并发连接问题。

django框架特点：
+ 重量级的Web框架
+ 丰富的第三方库
+ 稳定，相对于Flask整体封闭性比较好，适合做企业级网站的开发
+ 自带admin后台管理
+ 自带ORM模板引擎

Flask框架特点:
+ 轻量级的Web框架
+ 适合做小网站，Web服务器的API。（开发大网站需要自己设计架构）
+ 跟非关系型的数据库结合远远优于Django框架

### 13. golang的模型



### 14. csrf
### 15. ELK线上如何批量修改配置，而不影响服务


+ 数据备份冗余，防止数据丢失
+ 故障自动切换，正在服务的节点故障时，可以自动切换到备用节点
+ 在线扩容，根据需求动态增加，减少服务实例

1. redis哨兵模式，主从模式
2. k8s集群部署多个master节点，多个master节点使用nginx做反向代理，当其中一个挂掉之后，客户端无感知，集群正常提供服务
3. k8s集群中无状态服务部署多个deployment，即使其中一个服务出现异常，也可以正常提供服务
4. gluster服务，创建复制多个副本的volume
5. kafka多个集群

紧急处理事件：
1. pod网络不通
2. nginx配置导致https访问出现异常

优化点：

1. 部分集群增加了多master节点保证集群稳定性
2. nginx增加缓存文件保证启动正常
3. dockerfile构建优化

## 保时捷

### 1. Pod重启策略

+ Always： 容器失效是，自动重启该pod，这是默认值
+ OnFailure： 容器停止运行且退出码不为0时重启
+ Never：不论状态为何，都不重启该容器

Pod中容器启动过程

+ initContainer容器：
  + 多个initC顺序启动，前一个启动成功后才启动下一个；
  + 仅当最后一个initC执行完毕后，才会启动主容器；
  + 常用于进行初始化操作或等待依赖的服务已ok；

+ postStart钩子：
  - postStart与container的主进程**并行执行**；
  - 在postStart执行完毕前，容器一直是waiting状态，pod一直是pending状态；
  - 若postStart运行失败，容器会被杀死；
+ startupProbe钩子：
  - v1.16版本后新增的探测方式；
  - 若配置了startupProbe，就会先禁止其他探测，直到成功为止；
+ readinessProbe探针：
  - 探测容器状态是否ready，准备好接收用户流量；
  - 探测成功后，将pod的endpoint添加到service；
+ livenessProbe探针：
  - 探测容器的健康状态，若探测失败，则按照重启策略进行重启；
+ containers:
  - 多个container之间是顺序启动的，参考[源码](https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/kuberuntime/kuberuntime_manager.go#L835)；

### 2. 怎么限制pod的资源



### 2. pvc扩容

修改storageClass的allowVolumeExpansion:true
再修改pvc.spec.resources.requests.storage字段

### 3. elk

### 4. kafka创建topic流程

### 5. redis怎么使用

1. 集群中使用redis服务（Sentinel模式)
2. 项目中如何使用redis介绍
3. 

### 6.驱逐pod命令

```bash
# 驱逐pod命令
kubectl drain nodename --delete-local-data --ignore-daemonsets --force
# 将node设置为不可调度状态
kubectl cordon nodename
```

### 7.如何对服务进行扩容

手动扩容
```bash
# 查看当前副本个数
kubectl get pods
# 修改当前pod副本数
kubectl scale deployment nginx-deployment --replicas 5
```

自动扩容

1. 首先需要安装metrics-server

```bash
# 为deployment资源nginx-deployment创建hpa资源，pod数量上限5个，下限一个，在pod平均cpu达到50%后开始扩容
kubectl autoscale deployment nginx-deployment --max=5 --min=1 --cpu-percent=10
```


## 腾云悦智

### 1.pvc，pvc的区别以及都有什么策略

| 模式          | 解释                                                   |
| ------------- | ------------------------------------------------------ |
| ReadWriteOnce | 可读可写，但只支持单个节点挂载                         |
| ReadOnlyOnce  | 只读，可以被多个节点挂载                               |
| ReadWriteMany | 多路可读可写，这种存储方式以读写的方式被多个节点共享。 |

不是每一种存储都支持这三种方式，像共享方式，目前支持的还是比较少，比较常用的是NFS，在PVC绑定PV时通常根据两个条件来绑定，一个是存储的大小，一个是访问模式



### 2.pod的重启策略

### 3.kuberntes中都有哪些健康检查

+ livenessProbe，存活性检测，正常情况下显示POD Running状态
+ readnessProbe，就绪性检测，当正常情况下回显示ready状态正常，加入到svc后端
+ startupProbe，启动检测，开始的时候只启动startupProbe，其他检测不生效

### 4.如何使用etcd作为服务发现

### 5.helm使用？

### 6.docker的架构

### 7.dockerfile文件编写及常用指令

### 8.docker数据目录下都有哪些目录

### 9.kubernetes的架构组成

### 10.jenkins pipline

### 11.服务的发布形式

https://blog.csdn.net/qswdcs1/article/details/103615872

+ 蓝绿发布
+ 灰度发布
+ 金丝雀发布

### 现有的devops系统了解哪些？

### 系统的发布频率，发布流程

### kubernetes中的secret怎么使用和configmap的区别

### kubernetes中亲和性和反亲和性

### kubernetes中有哪些污点

taint污点

```bash
kubectl taint node k8s-01 key=value:NoSchedule
kubectl taint node k8s-02 key=value:NoExecute
kubectl taint node k8s-03 key=value:PreferNoSchedule
```

+ NoSchedule不能容忍新的pod调度过来，但是之前运行在node节点中的pod不受影响
+ NoExecute不能容忍新的pod调度过来，老的pod也会被quzhu
+ PreferNoScheduler尽量不调度到污点节点中去

node控制器当某种条件条成立时，会自动的给node打上污点。下面是其中内置的污点：

```bash
node.kubernetes.io/not-ready:node # node不是ready状态，对应于node的condition ready=false
node.kubernetes.io/unreachable:node # controller与node失联了，对应于node的condition ready=unknow
node.kubernetes.io/out-of-disk:node # 磁盘空间不足了
node.kubernetes.io/network-unavaliable:node # node的网断了
node.kubernetes.io/unschedulable:node  # node不是可调度状态
# 是由外部云提供商提供的时候，刚开始
# 刚开始的时候会打上这个污点来标记还未被使用。当cloud-controller-manager控制器初始化完这个node，kubelet会自动移除这个污点。
node.cloudprovider.kubernetes.io/uninitalized:kubelet 
```



### kubernetes中污点打在什么资源上

污点打在node节点上，防止pod调度到该节点上

容忍度tolerations配置在pod资源上，可以调度到某些节点上

### docker如何镜像加速

查号阿里云加速镜像服务器的地址

修改/etc/docker/daemon.json文件，在"registry-mirrors"字段中追加阿里云的镜像服务器地址，重启docker

### ingress配置高可用

ingress-nginxcontroller控制器部署的时候使用daemonset的方式部署，然后再node上添加label，daemonset控制器中配置pod模板的时候，指定要部署的节点。同时该节点不要调度其他pod，防止争抢资源。

### kube-dns

https://www.jianshu.com/p/6ce87f35a081

https://www.cnblogs.com/Bjwf125/p/14633127.html

```bash
# 1、找到容器ID，并打印它的NS ID
docker inspect --format "{{.State.Pid}}"  16938de418ac
# 2、进入此容器的网络Namespace
nsenter -n -t  54438
# 3、抓DNS包
tcpdump -i eth0 udp dst port 53|grep youku.com
```

DNS策略(dnsPolicy)

+ None
+ default
+ ClusterFirst
+ ClusterFirstWithHostNet

## 亿通

### 介绍下你做过的一个python模块

+ 服务的部署，

### ansible用过没有？

### 运维如何对软件选型？

运维成本，改造成本，

### 开发新服务的时候，运维人员什么时候参与比较合适

# 脉景

### AJAX跨域问题

1. 浏览器的同源策略：协议、域名、端口号都相同——用户信息安全

2. AJAX跨域：当使用AJAX请求数据时，如果三者中的任意一个不一样，那么就是一个跨域请求

   ```
   http://teach.mengmacoding.com/interface/letter.php
   协议：http
   域名：teach.mengmacoding.com
   端口号：80
   ```

3. 跨域的解决方案

   1）设置本地代理服务器：服务器请求资源不受同源策略影响

   原理：将远端的资源请求到本地后再访问

   2） CORS：服务端允许跨域请求——主流解决方案

   ```
   //告诉浏览器允许所有的域访问
   //注意 * 不能满足带有cookie的访问,Origin 必须是全匹配
   //resp.addHeader("Access-Control-Allow-Origin", "*");
   //解决办法通过获取Origin请求头来动态设置
   String origin = request.getHeader("Origin");
   if (StringUtils.hasText(origin)) {
       resp.addHeader("Access-Control-Allow-Origin", origin);
   }
   //允许带有cookie访问
   resp.addHeader("Access-Control-Allow-Credentials", "true");
   //告诉浏览器允许跨域访问的方法
   resp.addHeader("Access-Control-Allow-Methods", "*");
   //告诉浏览器允许带有Content-Type,header1,header2头的请求访问
   //resp.addHeader("Access-Control-Allow-Headers", "Content-Type,header1,header2");
   //设置支持所有的自定义请求头
   String headers = request.getHeader("Access-Control-Request-Headers");
   if (StringUtils.hasText(headers)){
       resp.addHeader("Access-Control-Allow-Headers", headers);
   }
   //告诉浏览器缓存OPTIONS预检请求1小时,避免非简单请求每次发送预检请求,提升性能
   resp.addHeader("Access-Control-Max-Age", "3600");
   ```

4) 通过nginx解决跨域问题

   跨域是浏览器的问题，浏览器出现跨域问题的时候，会发送两次请求，第一次请求的方法是‘Option’，第二次请求是正常的GET或者POST.

   ```
   server {
           listen       8099;
           server_name  localhost;
    
           #charset koi8-r;
    
           #access_log  logs/host.access.log  main;
    
           location  / {
   			root   html;
   			index  index.html index.htm;
   			# 配置html以文件方式打开
   			# 配置html以文件方式打开
   			if ($request_method = 'POST') {
   				#add_header 'Access-Control-Allow-Origin' '*' always;
   				add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS,PUT,DELETE,OPTION';
   				add_header 'Access-Control-Allow-Credentials' 'true';
   				add_header 'Access-Control-Allow-Headers' 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,Accept,Referer,Accept-Encoding,Accept-Language,Access-Control-Request-Headers,Access-Control-Request-Method,Connection,Host,Origin,Sec-Fetch-Mode';
   			}
   			if ($request_method = 'GET') {
   				#add_header 'Access-Control-Allow-Origin' '*' always;
   				add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS,PUT,DELETE,OPTION';
   				add_header 'Access-Control-Allow-Credentials' 'true';
   				add_header 'Access-Control-Allow-Headers' 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,Accept,Referer,Accept-Encoding,Accept-Language,Access-Control-Request-Headers,Access-Control-Request-Method,Connection,Host,Origin,Sec-Fetch-Mode';
   			}
   			if ($request_method = 'OPTIONS') {
   				add_header 'Access-Control-Allow-Origin' '*' always;
   				add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS,PUT,DELETE,OPTION';
   				# 允许带有cookies访问
   				add_header 'Access-Control-Allow-Credentials' 'true';
   				add_header 'Access-Control-Allow-Headers' 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,Accept,Referer,Accept-Encoding,Accept-Language,Access-Control-Request-Headers,Access-Control-Request-Method,Connection,Host,Origin,Sec-Fetch-Mode';
   				return 204;
   			}
   			# 代理到ip地址端口
   			proxy_pass       http://xxxx:xxxx;
    
   		}
    
           #error_page  404              /404.html;
    
           # redirect server error pages to the static page /50x.html
           #
           error_page   500 502 503 504  /50x.html;
       }
   ```

### Nginx高可用配置

keepalived + 双nginx，高可用模式

### 阿里云负载均衡器介绍

https://blog.csdn.net/javalingyu/article/details/125069476

### python中各种数据结构，以及是否是线程安全的

python的内置类型dict，list，tuple是线程安全

### python中上下文管理器with

```python
class Connect(object):
    def __init__(self, filename):
        self.filename = filename

    # with运行的时候出发此方法的运行
    def __enter__(self):
        self.f = open(self.filename)
        return self.f
	# with结束后触发此方法的运行
    # exc_type如果抛出异常这里获取异常的类型
    # exc_val如果抛出异常，这里获取异常内容
    # exc_tb如果抛出异常，这里显示所在位置
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("*"*40)
        print(exc_type)
        print("*"*40)
        print(exc_val)
        print("*"*40)
        print(exc_tb)
        print("with 语句执行之后。。。。。")
        self.f.close()

with Connect('/etc/passwd') as conn:
    for i in conn.readlines():
        print(i)
    print(2/0)
```
```bash
****************************************
<class 'ZeroDivisionError'>
****************************************
division by zero
****************************************
<traceback object at 0x7f71cb37a500>
with 语句执行之后。。。。。
Traceback (most recent call last):
  File "/opt/data/centos-7-51/celery/celery/practice.py", line 26, in <module>
    print(2/0)
ZeroDivisionError: division by zero
```

```python
try:
    fp = open(r"/etc/passwd", "r")
    content = fp.read()
    print(content)
finally:
    fp.close()
    
```

### python中的魔法方法

```
```

### 单例模式

```python
from datetime import date

class Person(object):
    def __new__(cls, *arg, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(Person, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, name):
        self.name = name
```

dockerfile，环境太多了，jwt验证

## GO jwt

```go
package main

import (
	"fmt"
	"log"
	"time"

	"github.com/golang-jwt/jwt"
)

var mySigningKey = []byte("asfasfdafasdfdasfa.")

func main() {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"name": "wangxianchao",
		"exp":  time.Now().Unix() + 5,
		"iss":  "sywdebug",
	})

	tokenString, err := token.SignedString(mySigningKey)
	if err != nil {
		log.Println(err.Error())
		return
	}
	fmt.Println("加密后的token字符串", tokenString)
	time.Sleep(time.Second * 10)
	//在这里如果也使用jwt.ParseWithClaims的话，第二个参数就写jwt.MapClaims{}
	//例如jwt.ParseWithClaims(tokenString, jwt.MapClaims{},func(t *jwt.Token) (interface{}, error){}

	token, err = jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
		return mySigningKey, nil
	})
	if err != nil {
		log.Println(err.Error())
		return
	}
	fmt.Println("token:", token)
	fmt.Println("token.Claims:", token.Claims)
	fmt.Println(token.Claims.(jwt.MapClaims)["name"])

}
```



优势：执行力不错，领导给的任务都可以完成

缺点：我对应应聘岗位的知识深度和广度还有一点距离，应聘的岗位主要使用go语言，如果针对k8s二级开发的话，需要加强这方面的学习

为什么来中兴：我目前的工作运维开发岗位，使用到的技术知识，跟公司招聘的岗位有很大的重合度，非常合适。另外我也想在云平台或者虚拟化相关的方向发展。中兴公司在全国也是比较有名的企业，平台比较大。

职业规划：

描述你朋友是个什么样的人：值得信赖的人，值得学习的人，

2. 一类朋友，乐观开朗，喜欢运动，很会享受生活的一个人
3. 一类朋友，工作狂，技术狂，

注意与HR互动：

评价一下当前团队有哪些优点和缺点：

优点：每个人技术方面的特长说下

缺点：技术气氛不是很强，所用的技术框架跟市场上主流的有些区别，跟公司的整体架构耦合性比较强，









