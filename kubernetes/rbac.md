# 集群安全机制

## API Server授权模式

使用kubernetes提供的RBAC授权模式可以对资源精确的权限管理，如下是对某个pod单独访问的控制
目前kubernetes也支持对具体资源进行授权，但是由pod的管理器自动生成的pod不方便进行管理，例如Deployment，当Deployment资源更新后，新生成的pod名称会变化。

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-admin-role
  namespace: default
rules:
- apiGroups:
  - ""
  resources:
  - pods
  - services
  verbs:
  - get
  - list
- apiGroups:
  - ""
  resources:
  - pods
  - pods/log
  - pods/exec
  - services
  resourceNames: ["nginx-deployment", "nginx-deployment-558fc78868-tnfpl"]
  verbs:
  - get
  - list
  - create

---

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-admin-rolebinding
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: app-admin-role
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: app-admin

```

```sh
User="app-admin"
Server="https://10.4.7.60:6443"
openssl genrsa -out app-admin-key.pem 2048
openssl req -new -out app-admin-req.csr -key app-admin-key.pem -subj "/CN=${User}"
openssl x509 -req -in app-admin-req.csr -out app-admin-cert.pem -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -days 100

kubectl config set-cluster kubernetes --certificate-authority /etc/kubernetes/pki/ca.crt --embed-certs=true --server=https://10.4.7.60:6443 --kubeconfig appconfig
kubectl config set-credentials app-admin --client-certificate=app-admin-cert.pem --client-key=app-admin-key.pem --embed-certs=true --kubeconfig=./appconfig
kubectl config set-context app-admin@kubernetes --cluster=kubernetes --user=app-admin --kubeconfig=./appconfig
kubectl config use-context app-admin@kubernetes --kubeconfig appconfig

kubectl apply -f rbac.yaml
```

