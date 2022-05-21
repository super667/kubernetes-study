# kubernetes部署

## 部署架构图

## 虚拟机分配

|machine         |  ip       | install component                                  |cpu, memory |
|----------------|-----------|----------------------------------------------------|------------|
|master          |10.4.7.10  | kube-apiserver,kube-controller,kube-scheduler,etcd |2C,2G       |
|master          |10.4.7.11  | kube-apiserver,kube-controller,kube-scheduler,etcd |2C,2G       |
|worker          |10.4.7.12  | kubelet,kube-proxy, docker                         |2C,2G       |
|worker          |10.4.7.13  | kubelet,kube-proxy, docker                         |2C,2G       |
|worker          |10.4.7.14  | kubelet,kube-proxy, docker                         |2C,2G       |
|harbor          |10.4.7.15  | harbor,bind, nfs-server                            |2C,2G       |

## 部署集群

### 部署etcd

### 部署kube-apiserver

### 部署kube-controller-manager

### 部署kube-scheduler

### 部署kubelet

### 部署kube-proxy

### 部署dashboard

### 部署traefik

## 部署监控

## 部署ELK

## 部署Jenkins

## 部署应用
