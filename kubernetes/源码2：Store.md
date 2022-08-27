# Store Interface

## Store Interface

```go
type Store interface {

    // Add adds the given object to the accumulator associated with the given object's key
    Add(obj interface{}) error

    // Update updates the given object in the accumulator associated with the given object's key
    Update(obj interface{}) error

    // Delete deletes the given object from the accumulator associated with the given object's key
    Delete(obj interface{}) error

    // List returns a list of all the currently non-empty accumulators
    List() []interface{}

    // ListKeys returns a list of all the keys currently associated with non-empty accumulators
    ListKeys() []string

    // Get returns the accumulator associated with the given object's key
    Get(obj interface{}) (item interface{}, exists bool, err error)

    // GetByKey returns the accumulator associated with the given key
    GetByKey(key string) (item interface{}, exists bool, err error)

    // Replace will delete the contents of the store, using instead the
    // given list. Store takes ownership of the list, you should not reference
    // it after calling this function.
    Replace([]interface{}, string) error

    // Resync is meaningless in the terms appearing here but has
    // meaning in some implementations that have non-trivial
    // additional behavior (e.g., DeltaFIFO).
    Resync() error
}
```

Store接口是一个通用的存储和处理资源对象的接口，
Indexer接口在Store接口的基础上增加了几个关于index的方法，可以通过namespae和其他标签进行索引。