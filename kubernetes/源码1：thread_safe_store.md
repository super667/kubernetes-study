# ThreadSafeStore Interface接口

```bash
//k8s.io/client-go/tools/cache/thread_safe_store.go
type ThreadSafeStore interface {
  Add(key string, obj interface{})
  Update(key string, obj interface{})
  Delete(key string)
  Get(key string) (item interface{}, exists bool)
  List() []interface{}
  ListKeys() []string
  Replace(map[string]interface{}, string)
  Index(indexName string, obj interface{}) ([]interface{}, error)
  IndexKeys(indexName, indexKey string) ([]string, error)
  ListIndexFuncValues(name string) []string
  ByIndex(indexName, indexKey string) ([]interface{}, error)
  GetIndexers() Indexers
 
 
  // AddIndexers adds more indexers to this store.  If you call this after you already have data
  // in the store, the results are undefined.
  AddIndexers(newIndexers Indexers) error
  // Resync is a no-op and is deprecated
  Resync() error
}
```

+ 该接口定义了对资源增删改查的方法，例如Add/Update/Delete/Get/List等操作
+ 该接口定义了对资源进行索引的相关方法， 例如 Index/IndexKeys/ByIndex等操作

threadSafeStoreMap是一个机构体，该结构实现了上面介绍的接口ThreadSafeStore

```bash
// threadSafeMap implements ThreadSafeStore
type threadSafeMap struct {
    lock  sync.RWMutex
    items map[string]interface{}

    // indexers maps a name to an IndexFunc
    indexers Indexers
    // indices maps a name to an Index
    indices Indices
}
```

+ 该结构体中有名为items的map属性，其中存储了资源对象的key和资源本身。
+ Indexer对象存储了对应的索引命名函数。
+ indices对象存储了对应的索引数据。
+ 该结构体有Mutex操作，是并发安全的。
