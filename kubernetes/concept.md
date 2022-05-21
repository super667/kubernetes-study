# kubernetes组件介绍

## etcd

kubernetes的后端存储数据库，采用golang实现。
1.**可用性角度：高可用**。作为集群控制面存储，他保存了各个服务的部署，运行信息。若它出现问题，会导致集群状态无法变更，服务副本数无法协调。可能会影响用户数据面。
2.**数据一致性角度：提供读取最新数据机制。** 协调服务必须有高可用的目的，必然不能存在单点故障，etcd支持集群部署，并使用了raft协议保证集群中各个服务的数据强一致性。
3.**容量角度： 低容量，仅存储关键元数据配置**
4.**功能： 增删改查，监听数据变化。** etcd保存k8s集群中所有的服务状态，节点的配置信息，提供了watch机制，当配置信息发生变更时，能及时通知到各个组件
5.**运维复杂度：可维护性。** 提供API实现平滑变更成员节点信息，大大降低运维复杂度，减少运维成本

## kube-apiserver

kubernetes API Server的核心功能是提供各类资源的增删改查及Watch等HTTP Rest接口，是各个功能模块间数据交互的中心枢纽。另外还提供了一下功能：

+ 1.集群管理的API入口

+ 2.资源配额控制的入口

+ 3.提供了完备的集群安全机制

## kube-controller

kube-controller这个组件集成了大部分资源的控制器，它通过API Server提供的List-Watch接口实现监控集群中特定资源的状态变化，当发生各种故障导致某个资源的状态发生变化时，Controller会尝试将其调整为期望的状态。Controller Manager是集群内部的管理控制中心，也是kubernetes自动化功能的核心。
比如：Node意外宕机时，Node Controller会及时发现此故障并执行自动化修复流程，确保其处于期望的工作状态。

## kube-scheduler

Kubernetes Scheduler在整个系统中承担了承上启下的重要功能，“呈上”是指它负责接收Controller Manager创建的新Pod，将其调度到合适的目标Node上；“启下”是指安置工作完成后，目标node上的kubelet服务接管后继工作，创建Pod。

  kubernetes Scheduler当前提供的默认调度分为一下两步。

+ (1)预选调度流程，遍历所有的目标Node，选出服务要求的节点。kubernetes内置了多种预选策略可以选择。

+ (2)优选阶段，在第一步的基础上，采用优选策略计算出积分最高的Node。

## kubelet

在kubernetes集群中，每个Node上都会启动一个kubelet服务进程，该进程用于处理Master下发到本节点的任务，管理Pod及Pod中的容器。每个kubelet进程都会在API Server上注册节点自身的信息，定期向Master汇报节点资源的使用情况，并通过cAdvisor监控容器和节点资源。

  kubelet通过一下方式获取要要运行的Pod清单。

+ (1)文件：默认目录为/etc/kubernetes/manifests。也可以通过--config指定的配置文件指定目录。

+ (2)HTTP端点URL：通过“--manifest-url”参数设置。

+ (3)API Server: kubelet通过API Server监听etcd目录，同步到pod列表

文件或URL方式创建的Pod为Static Pod。

  kubelet主要功能有：

+ 节点管理，上报节点状态

+ pod管理，监听API Servier, 创建或者删除Pod

+ 容器健康检查，有exec ，http, tcp

+ cAdvisor被集成到kubelet代码中，监控容器的状态信息

## kube-proxy

kube-proxy是kubernetes的网络代理组件，在介绍kube-proxyz之前有必要介绍下Service资源，Service起一个透明代理及负载均衡器的作用，其核心功能是将到某个Service的访问请求转发到后端的多个Pod实例上。kube-proxy运行的过程中动态创建与Service相关的iptables规则，这些规则实现了将访问服务的请求转发到后端Pod的功能。 Iptalbles机制针对的是本地端口，所以每个Node上都要运行kube-proxy组件，这样在任意Node上都可以发起对Service的矾根请求。

 **kube-proxy有三种模式**

+ (1) **usersapce:** 这种模式下，kube-proxy进程是一个真实的TCP/UDP代理，负责Service到Pod的访问流量的转发。这种转发模式需要将数据包重新复制到用户态，效率较低。

+ (2) **iptables:** 这种模式下，kube-proxy将不再起到Proxy的作用，其核心功能通过API Server的Watch接口实时跟踪Service与Endpoint的变更信息，并立即更新iptables规则，Client的请求流量则通过iptables的NAT机制“直接路由”到目标Pod。

+ (3) **ipvs:** 这种模式下，kube-proxy使用iptables的扩展ipset，ipset使用了高效的数据结构(Hash表)，允许无限的规模扩张

## CRI接口

kubelet的主要功能就是启动和停止容器的组件，我们称之为容器运行时，现在有docker/containerd/podman等。 kubernetes从1.5版本就开始加入容器运行时插件API，即Container Runtime Interface,简称CRI。

    kubelet使用gRPC框架通过UNIX socket与容器运行时进行通信。kubelet是客户端，CRI代理是服务端。
    Protocol Buffers API提供了两个gRPC服务：ImageService和RuntimeService。
![cri](images/cri%E4%B8%BB%E8%A6%81%E7%BB%84%E4%BB%B6.png)

## CNI接口

## CSI接口

## 其它配套服务

### harbor

### gluster

### ceph

### flannel

### calico

