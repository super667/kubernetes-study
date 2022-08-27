# Reflector解析

## 背景

Reflector是保证Informer可靠性的核心组件，在丢失事件，收到异常事件，处理事件失败等多种异常情况下需要考虑的细节有很多，单独的listwatcher组件缺少重新连接和重新同步的机制，有可能出现数据不一致等问题。

## Reflector

Reflector可以成为反射器，将etcd中的数据发射到存储DeltaFIFO中，Reflector通过其内部的List操作获取所有资源对象数据，保存到本地存储，之后wathch见识资源变化，触发对应事件处理例如：Add，Update，Delete等

### Reflector中watcher处理过程

```go
func (r *Reflector) watchHandler(start time.Time, w watch.Interface, resourceVersion *string, errc chan error, stopCh <-chan struct{}) error {
    eventCount := 0

    // Stopping the watcher should be idempotent and if we return from this function there's no way
    // we're coming back in with the same watch interface.
    defer w.Stop()

loop:
    for {
        select {
        case <-stopCh:
            return errorStopRequested
        case err := <-errc:
            return err
        case event, ok := <-w.ResultChan():
            if !ok {
                break loop
            }
            if event.Type == watch.Error {
                return apierrors.FromObject(event.Object)
            }
            if r.expectedType != nil {
                if e, a := r.expectedType, reflect.TypeOf(event.Object); e != a {
                    utilruntime.HandleError(fmt.Errorf("%s: expected type %v, but watch event object had type %v", r.name, e, a))
                    continue
                }
            }
            if r.expectedGVK != nil {
                if e, a := *r.expectedGVK, event.Object.GetObjectKind().GroupVersionKind(); e != a {
                    utilruntime.HandleError(fmt.Errorf("%s: expected gvk %v, but watch event object had gvk %v", r.name, e, a))
                    continue
                }
            }
            meta, err := meta.Accessor(event.Object)
            if err != nil {
                utilruntime.HandleError(fmt.Errorf("%s: unable to understand watch event %#v", r.name, event))
                continue
            }
            newResourceVersion := meta.GetResourceVersion()
            switch event.Type {
            case watch.Added:
                err := r.store.Add(event.Object)
                if err != nil {
                    utilruntime.HandleError(fmt.Errorf("%s: unable to add watch event object (%#v) to store: %v", r.name, event.Object, err))
                }
            case watch.Modified:
                err := r.store.Update(event.Object)
                if err != nil {
                    utilruntime.HandleError(fmt.Errorf("%s: unable to update watch event object (%#v) to store: %v", r.name, event.Object, err))
                }
            case watch.Deleted:
                // TODO: Will any consumers need access to the "last known
                // state", which is passed in event.Object? If so, may need
                // to change this.
                err := r.store.Delete(event.Object)
                if err != nil {
                    utilruntime.HandleError(fmt.Errorf("%s: unable to delete watch event object (%#v) from store: %v", r.name, event.Object, err))
                }
            case watch.Bookmark:
                // A `Bookmark` means watch has synced here, just update the resourceVersion
            default:
                utilruntime.HandleError(fmt.Errorf("%s: unable to understand watch event %#v", r.name, event))
            }
            *resourceVersion = newResourceVersion
            r.setLastSyncResourceVersion(newResourceVersion)
            if rvu, ok := r.store.(ResourceVersionUpdater); ok {
                rvu.UpdateResourceVersion(newResourceVersion)
            }
            eventCount++
        }
    }

    watchDuration := r.clock.Since(start)
    if watchDuration < 1*time.Second && eventCount == 0 {
        return fmt.Errorf("very short watch: %s: Unexpected watch close - watch lasted less than a second and no items received", r.name)
    }
    klog.V(4).Infof("%s: Watch close - %v total %v items received", r.name, r.expectedTypeName, eventCount)
    return nil
} 
```

BookMark类型
> 背景：List-Watch 是kubernetes中server和client通信的最核心的机制， 比如说api-server监听etcd， kubelet监听api-server， scheduler监听api-server等等，其实其他模块监听api-server相当于监听etcd，因为在k8s的设计中，只有api-server能跟etcd通信，其他模块需要etcd的数据就只好监听api-server
>
> **但什么是List-Watch呢？**
>
> 简单来讲就是先list当前时间点为止的全量变化，然后watch增量变化。
> 实现这个逻辑的模块就是go-client中大名鼎鼎的Reflector。
>
> 存在的问题：
>
> 但是还有一个问题，etcd保存历史变更时间太短，默认etcd3仅仅保存5分钟的变更。 另外resourceversion是一类资源共用一个自增长的数列，啥意思呢，举例来讲：所有的pod都使用同一个自增数列，而List-Watch机制是带filter的，比如说某一个kubelet就只关心位于自己node上的pod，所以在噶kubelet看来，resourceversion只是增长的，但是并不连续， 比如改kubelet看到的resourceversion是（1，3，8， 23， 44）， 没有的resourceversion因为并不在改kubelet所在的node上，所以该kubelet并不关心。
> 想象一个场景，某kubelet的watch connection断开了，reconnect的时候上传的断开前的resourceversion是5，但是此时api-server保存的历史变更已经是resourceversion = 10了， 并不是说这个reconnct花了超过5分钟，而是resourceversion = 5之后的几个版本改kubelet并不关心，所以没有更新version，一直保持resourceversion=5，一旦reconnect只能拿着5来找server（这段要好好理解）， server也没办法啊，只要返回一个错：too old version error，然后client（kubelet）看到这个错只好清空自己之前的积累（cache），重新List，如果累计了太多的历史变更，这得花较长的时间。
>
> 如何解决问题：
> 我们看看你bookmark干啥，其实就是server到client的一个通知机制，甭管你关心不关心（filter），一旦发生变更我通知你，但是因为你不关心你，所以我仅仅通知你变更的resourceversion，至于变更是什么内容，不告诉你，这样client就有了最新的resourceversion，这样就大大减少了List的几率，据说List的次数降低到原来的3%，很了不起的成就！

## 调用流程

```go
// NewFilteredDeploymentInformer constructs a new informer for Deployment type.
// Always prefer using an informer factory to get a shared informer instead of getting an independent
// one. This reduces memory footprint and number of connections to the server.
// 总是倾向于使用一个informer工厂来获取一个shared informer，而不是一个独立的informer，这样可以减少
// 内存占用和服务器的连接数。
func NewFilteredDeploymentInformer(client kubernetes.Interface, namespace string, resyncPeriod time.Duration, indexers cache.Indexers, tweakListOptions internalinterfaces.TweakListOptionsFunc) cache.SharedIndexInformer {
    return cache.NewSharedIndexInformer(
        &cache.ListWatch{
            ListFunc: func(options metav1.ListOptions) (runtime.Object, error) {
                if tweakListOptions != nil {
                    tweakListOptions(&options)
                }
                return client.AppsV1().Deployments(namespace).List(context.TODO(), options)
            },
            WatchFunc: func(options metav1.ListOptions) (watch.Interface, error) {
                if tweakListOptions != nil {
                    tweakListOptions(&options)
                }
                return client.AppsV1().Deployments(namespace).Watch(context.TODO(), options)
            },
        },
        &appsv1.Deployment{},
        resyncPeriod,
        indexers,
    )
}
```

## Example

```go
package main
 
import (
    "fmt"
    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/fields"
    "k8s.io/apimachinery/pkg/util/wait"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/tools/cache"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/client-go/util/homedir"
    "path/filepath"
    "time"
)
 
func Must(e interface{}) {
    if e != nil {
        panic(e)
    }
}
 
func InitClientSet() (*kubernetes.Clientset, error) {
    kubeconfig := filepath.Join(homedir.HomeDir(), ".kube", "config")
    restConfig, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        return nil, err
    }
    return kubernetes.NewForConfig(restConfig)
}
 
// 生成listwatcher
func InitListerWatcher(clientSet *kubernetes.Clientset, resource, namespace string, fieldSelector fields.Selector) cache.ListerWatcher {
    restClient := clientSet.CoreV1().RESTClient()
    return cache.NewListWatchFromClient(restClient, resource, namespace, fieldSelector)
}
 
// 生成pods reflector
func InitPodsReflector(clientSet *kubernetes.Clientset, store cache.Store) *cache.Reflector {
    resource := "pods"
    namespace := "default"
    resyncPeriod := 0 * time.Second
    expectedType := &corev1.Pod{}
    lw := InitListerWatcher(clientSet, resource, namespace, fields.Everything())
 
    return cache.NewReflector(lw, expectedType, store, resyncPeriod)
}
 
// 生成 DeltaFIFO
func InitDeltaQueue(store cache.Store) cache.Queue {
    return cache.NewDeltaFIFOWithOptions(cache.DeltaFIFOOptions{
        // store 实现了 KeyListerGetter
        KnownObjects: store,
        // EmitDeltaTypeReplaced 表示队列消费者理解 Replaced DeltaType。
        // 在添加 `Replaced` 事件类型之前，对 Replace() 的调用的处理方式与 Sync() 相同。
        // 出于向后兼容的目的，默认情况下为 false。
        // 当为 true 时，将为传递给 Replace() 调用的项目发送“替换”事件。当为 false 时，将发送 `Sync` 事件。
        EmitDeltaTypeReplaced: true,
    })
 
}
func InitStore() cache.Store {
    return cache.NewStore(cache.MetaNamespaceKeyFunc)
}
 
func main() {
    clientSet, err := InitClientSet()
    Must(err)
    // 用于在processfunc中获取
    store := InitStore()
    // queue
    DeleteFIFOQueue := InitDeltaQueue(store)
    // 生成podReflector
    podReflector := InitPodsReflector(clientSet, DeleteFIFOQueue)
 
    stopCh := make(chan struct{})
    defer close(stopCh)
    go podReflector.Run(stopCh)
    //启动
    ProcessFunc := func(obj interface{}) error {
        // 最先收到的事件会被最先处理
        for _, d := range obj.(cache.Deltas) {
            switch d.Type {
            case cache.Sync, cache.Replaced, cache.Added, cache.Updated:
                if _, exists, err := store.Get(d.Object); err == nil && exists {
                    if err := store.Update(d.Object); err != nil {
                        return err
                    }
                } else {
                    if err := store.Add(d.Object); err != nil {
                        return err
                    }
                }
            case cache.Deleted:
                if err := store.Delete(d.Object); err != nil {
                    return err
                }
            }
            pods, ok := d.Object.(*corev1.Pod)
            if !ok {
                return fmt.Errorf("not config: %T", d.Object)
            }
 
            fmt.Printf("Type:%s: Name:%s\n", d.Type, pods.Name)
        }
        return nil
    }
 
    fmt.Println("Start syncing...")
 
    wait.Until(func() {
        for {
            _, err := DeleteFIFOQueue.Pop(ProcessFunc)
            Must(err)
        }
    }, time.Second, stopCh)
}
```
