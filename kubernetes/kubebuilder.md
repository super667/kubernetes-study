# kubebuilder实践

## 安装

## 创建一个项目

```bash
# 查看当前kubebuilder版本
[root@hdss7-200 kubebuilder-demo2]# kubebuilder version
Version: main.version{KubeBuilderVersion:"3.6.0", KubernetesVendor:"1.24.1", GitCommit:"f20414648f1851ae97997f4a5f8eb4329f450f6d", BuildDate:"2022-08-03T11:47:17Z", GoOs:"linux", GoArch:"amd64"}

# 初始化项目
mkdir kubebuilder-demo
cd kubebuilder-demo
go mod init github.com/kubebuilder-demo
kubebuilder init --domain bading.tech
kubebuilder create api --group ingress --version v1beta1 --kind App
```
