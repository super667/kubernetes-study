[toc]

# go

## 常见问题

### go有哪些数据类型

+ 布尔类型 bool

+ 数字类型 unit、int、float32、float64、byte、rune

+ 字符串类型 string

+ 复合类型array，slice，map，channel，struct

+ 指针类型 pointer

+ 接口类型 interface

+ 函数类型 func

+ 方法类型method

### go语言接受者的选取

#### 何时使用值类型

+ 如果接收者是一个map，func或chan,使用值类型（因为他们本身就是引用类型）

+ 如果接收者是一个slice，并且方法不执行reslice操作，也不重新分配内存给slice，使用值类型

+ 如果接受者是一个小的数组或者原生的值类型结构体类型（比如time.Time类型），而且没有可修改的字段和指针，又或者接受者是一个简单地基本数据类型，像是int，string，使用值类型就好了。

  一个值类型的接受者可以减少一定数量的垃圾生成，如果一个值被传入一个值类型接受者的方法，一个栈上的拷贝会替代在堆上分配内存(但不是保证一定成功)，所以在没搞明白代码想干什么之前，别因为这个原因而选择值类型接受者。

#### 何时使用指针类型

+ 如果方法需要修改接受者，接受者必须是指针类型。
+ 如果接受者是一个包含了 `sync.Mutex` 或者类似同步字段的结构体，接受者必须是指针，这样可以避免拷贝。
+ 如果接受者是一个大的结构体或者数组，那么指针类型接受者更有效率。(多大算大呢？假设把接受者的所有元素作为参数传给方法，如果你觉得参数有点多，那么它就是大)。
+ 从此方法中并发的调用函数和方法时，接受者可以被修改吗？一个值类型的接受者当方法调用时会创建一份拷贝，所以外部的修改不能作用到这个接受者上。如果修改必须被原始的接受者可见，那么接受者必须是指针类型。
+ 如果接受者是一个结构体，数组或者 `slice`，它们中任意一个元素是指针类型而且可能被修改，建议使用指针类型接受者，这样会增加程序的可读性

### 方法与函数的区别

  在go语言中，函数和方法不太一样，有明确的概念区分；函数是指不属于任何结构体、类型的方法，也就是说函数是没有接收者的；而方法是有接收者的。

### 方法·值接受者·和·指针接收者·的区别

+ 如果方法的接受者是指针类型，无论调用者是对象还是对象指针，修改的都是对象本身，会影响调用者；

+ 如何方法的接收者是值类型，无论调用者是对象还是对象 指针，修改的都是对象副本，不影响调用者；

### 函数返回局部变量的指针是否安全

  一般来说局部变量会在函数返回后被销毁，因此被返回的引用就成为了无所指的引用，程序会进入未知状态。但是这在go中是安全的，go编译器将会对每个局部变量进行逃逸分析。如果发现局部变量的作用域超出该函数，则不会将内存分配在站上，而是分配在堆上，因为他们不在栈区，即使释放函数，其内容也不会受影响。

### 函数参数传递是值传递还是引用传递

go语言中所有的传参都是值传递，都是一个副本一个拷贝。

参数如果是非引用类型（int，string，struct等这些），这样在函数中就无法修改原内容数据；如果是引用类型（指针，map，slice，chan等这些），这样就可以修改原内容数据

### defer关键字的实现原理

defer关键字的实现跟go关键字实现类似，不同的是他调用的是runtime.deferproc而不是runtime.newproc。在defer出现的地方，插入了指令call runtime.deferproc,然后再函数返回之前的地方，插入指令call runtime.deferreturn

### 内置函数make和new区别

变量初始化，一般包括2步，变量声明和变量内存分配，var关键字就是用来声明变量的，new和make函数只要是用来分配内存的；

make只能用来分配及初始化类型为slice，map，chan的数据，并且返回类型本身；

new可以分配任意类型的数据，并且置零，返回一个执行该类型内存地址的指针。

### slice原理

切片是基于数组实现的，他的底层是数组，他自己本身非常小，可以理解为底层数组的抽象。因为基于数组的实现，所以他的底层的内存是连续分配的，效率非常高，还可以通过索引获得数据

切片本身并不是动态数组或者数组指针。他内部实现的数据结构通过指针引用底层数组，设定相关属性向数据读写操作权限限定在指定的区域内。切片本身是一个只读对象，其工作机制类型数组指针的一种封装。

### array和slice的区别

1）数组长度不同
2）函数传参不同
3）计算数组长度方式不同

### slice深拷贝和浅拷贝

深拷贝：拷贝的是数据本身，创造一个新对象，新创建的对象与原创建的对象不共享内存，新创建的对象在内存中开辟一个新的内存地址，新对象值修改时不会影响原对象值。

浅拷贝：拷贝的是数据地址，只复制对象的指针，此时新对象和老对象指向的内存地址是一样的，新对象值修改时老对象也会变化

### slice扩容机制

扩容会发生在slice append的时候，当slice的cap不足以容纳新元素，就会进行扩容，扩容规则如下：

+ 如果新申请的容量比两倍原有容量大，那么扩容后容量大小为新申请容量

+ 如果原有slice长度小于1024，那么每次扩容为原来的2倍

+ 如果原slice长度大于1024，那么扩容为原来的1.25倍

+ 如果最凶容量计算值溢出，则最终容量就是新申请容量

### slice为什么不是线程安全的

slice底层结构并没有使用加锁等方式，不支持并发读写，所以并不是线程安全的，使用多个goroutine对类型为slice的变量进行操作，每次输出的值大概率都会不一样，与预期值不一致；slice在并发中不会报错，但是数据会丢失。

### map底层原理

Go中的map是一个指针，占用8个字节，指向hmap结构体

源码包中src/runtime/map.go定义了hmap的数据结构，hmap包含若干个结构为bmap的数组，每个bmap底层都采用链表结构，bmap通常叫其bucket

### map遍历为什么是无序的

只要有两点：

+ map在遍历时，并不是固定的0号bucket开始遍历，每次遍历，都会从一个随机值序号的bucket，再从其中随机的cell开始
+ map遍历时，是按遍历的bucket，同时按需遍历bucket中

map本身是无序的，且遍历顺序还会被随机化，如果想顺序遍历map，需要对map key先排序，再按照key的顺序遍历map

### map为什么是非线程安全的

map默认是并发不安全的，同时对map进行并发读写时，程序会panic

### map如何查找

### map冲突的解决方式

比较常用的Hash冲突解决方案有链地址法和开放寻址法

**链地址法:** 当哈希发生冲突时，创建新单元，并将新单元添加到冲突单元所在链表的尾部

**开放寻址法：**当哈希冲突发生时，从发生冲突的那个单元其，按照一定的次序，从哈希表中寻找一个空闲的单元，然后把发生冲突的元素存入到该单元。开放寻址法需要的表长度要大于等于所需要存放的元素数量

### 什么是负载因子？map的负载因子为什么是6.5?

负载因子（load factor），用于衡量当前哈希表中空间占用率的核心指标，也就是每个bucket桶存储的平均元素个数。

Go官方发现：装载因子越大，填入的元素越多，空间利用率也就越高，但是发生哈希冲突的几率就变大。反之装载因子越小，填入的元素越少，冲突发生的几率越小，但是空间浪费也会变得更多，而且还会提供扩容的次数。根据这份测试结果和讨论，Go官方取了一个相对适中的值。把Go中的map的负载因子硬编码为6.5，这就是6.5的选择缘由，这意味着在go语言中，当map存储的元素格式大于等于6.5个桶个数时，就会出发扩容行为。

### map如何扩容

**双倍扩容：** 扩容采取了一种称为渐进式的方式，原有的key并不会一次性搬迁完毕，每次最多只会搬迁2个bucket。

**等量扩容：** 重新排列，极端情况下，重新排列也解决不了，map存储就会蜕变成链表，性能大大降低，此时哈希因子hash0的设置，可以降低此类极端场景的发生。

### map和sync.Map谁的性能更好，为什么？

和原始map+RWLock的方式实现并发的方式比，减少了加锁对性能的影响。他做了一些优化：可以无锁访问read map，而且会优先操作read map，倘若只操作read map就可以满足要求，那么就不用去操作write map，所以在某些特定场景中他发生锁竞争的频率会远远小于map+RWLock的实现方式，适合读多写少的场景。写多的场景会导致read map缓存失效，需要加锁，冲突变多，性能急剧下降。

### channel有什么特点

### channel的底层实现原理

go中的channel是一个队列，遵循先进先出的原则，负责协程之间的通信（go语言提倡不要通过共享内存实现通信，而是通过通信实现内存共享，CSP并发模型，就是通过goroutine和channel来实现的）

通过var声明或者通过make函数创建的channel变量是一个存储在函数栈帧上的指针，占用8个字节，指向堆上的chan结构体

### channel有无缓冲的区别

不带缓冲的channel是同步的，带缓冲的channel是异步的。

不带缓冲的channel中，每一个发送者与接收者都会阻塞当前进程，只有当接收者和发送者都准备就绪了，channel才能正常使用。

带缓冲的channel并不能无限的接收数据而不造成阻塞，能够接收的数据的个数取决于channel定义时设定的缓冲的大小，只有在这个缓冲范围之内，channel的发送才不会造成阻塞。

### channel为什么是线程安全的

不同协程通过channel进行通信，本身的使用场景就是多线程，为了保证数据的一致性，必须实现线程安全。

因此channel的底层实现中，chan结构体中采用Mutex锁来保证数据读写安全。在循环数组buf中的数据进行入队和出队操作时，必须先获取互斥锁，才能操作channel数据。

### channel如何控制goroutine并发执行程序

使用channel进行通信通知，用channel去传递信息，从而控制并发执行顺序

### channel共享内存有什么优劣势

Go引入了channel和goroutine实现了CSP模型将生产者和消费者进行了解耦，channel其实和消息队列很相似。

**优点：**使用channel可以帮助我们解耦生产者和消费者，可以降低并发当中的耦合

**缺点：** 容易死锁

### channel发送和接收什么情况下会死锁

**死锁：** 

+ 单个协程永久阻塞
+ 两个或者两个以上的协程的执行过程中，由于竞争资源或由于彼此通信而造成的一种阻塞现象

channel死锁场景：

+ 非缓存channel只写不读
+ 非缓存channel读在写后面
+ 缓存channel写入超过缓冲区数量
+ 空读
+ 多个协程互相等待

### go互斥锁的实现原理

Go sync包提供了两种锁类型：互斥锁sync.Mutex和读写互斥锁sync.RWMutex，都属于悲观锁

概念：Mutex是互斥锁，当一个goroutine获得了锁后，其他goroutine不能获取锁（只能存在一个读者或写者，不能同时读和写）互斥锁对应的底层结构是sync.Mutex结构体

```go
type Mutex struct {
	state int32
	sema  uint32
}
```

state表示锁的状态，有锁定，被唤醒，饥饿模式等，并且是state的二级制位来标识的，不同模式下会有不同的处理方式

sema表示信号量，mutex阻塞队列的定位是通过这个变量实现的，从而实现goroutine和阻塞和唤醒

### 互斥锁正常模式和饥饿模式的区别

#### 正常模式（非公平锁）

在刚开始的时候，处于正常模式，也就是G1持有着一个锁的时候，G2会自旋的去尝试获取这个锁，当自旋超过四次还没有能获取到锁的时候，这个G2就会被加入到获取锁的等待队列里边，并阻塞等待唤醒

正常模式下，所有等待锁的goroutine按照先入先出的顺序等待。唤醒的goroutine不会直接拥有锁，而是会和新请求锁的goroutine竞争锁。新请求锁的goroutine具有优势：它正在CPU上执行，而且可能有好几个，所以刚刚唤醒的gouroutine有很大可能在锁竞争中失败，长时间获取不到锁，就会切换到饥饿模式。

#### 饥饿模式（公平锁）

当一个goroutine等待锁时间超过1ms时，它可能就会遇到饥饿问题。在版本1.19中，这种场景下GO Mutex切换到饥饿模式，解决饥饿问题。

```go
starving = runtime_nanotime()-waitStartTime > 1e6
```

饥饿模式下直接把锁交给等待队列中排在第一位的goroutine（队头），同时饥饿模式下，新进来的goroutine不会参与抢锁，也不会进入自旋状态，会直接进入等待队列的尾部，这样很好的解决了老的goroutine一直抢不到锁的场景。

那么也不可能说永远的保持一个饥饿的状态，总归有吃饱的时候，也就是总有那么一刻Mutex回到正常模式，那么回归到正常模式必须具备的条件有一下几种：

1.G的执行时间小于1ms

2. 等待队列已经全部清空了

### 互斥锁允许自旋的条件

**线程没有获取到锁时常见有2种处理方式：**

+ 一种是没有获取到锁的线程就一直循环等待判断该资源是否已经释放锁，这种锁也叫自旋锁，他不用将线程阻塞起来，适用于并发低且执行时间短的场景，缺点是cpu占用较高
+ 另一种处理方式就是把自己阻塞起来，会释放cpu给其他线程，内核会将线程置为【睡眠】状态，等到锁释放后，内核会在合适的时机唤醒该线程，适用于高并发场景，缺点是有线程上下文切换的开销

**允许自旋的条件：**

+ 锁已被占用，并且不处于饥饿模式
+ 积累的自旋次数小于最大自旋次数
+ cpu核数大于1
+ 有空闲的P
+ 当前goroutine所挂载的P下，本地待运行队列为空

### go读写锁的实现原理

### go原子操作有哪些？

原子操作仅会由一个对立的CPU指令代表和完成。原子操作时无锁的，常常通过CPU指令直接实现。事实上，其他同步技术的实现常常依赖于原子操作。

当我们想要对某个变量并发安全的修改，除了使用官方提供的mutex，还可以使用sync/atomic包的原子操作，它能够保证对变量的读取或修改期间不被其他协程影响。

aomic包提供的原子操作能够确保任一时刻只有一个goroutine对变量进行操作，善用atomic能够避免程序中出现大量的锁操作。

**常见操作：** 

+ 增减Add
+ 载入Load
+ 比较并交换CompareAndSwap
+ 交换Swap
+ 存储Store

### 原子操作和锁的区别

原子操作由底层硬件支持，而锁是基于原子操作+信号量完成的。若实现相同的功能，前者通常会更有效率

原子操作时单个指令的互斥操作；互斥锁、读写锁是一种数据结构，可以完成临界区（多个指令)的互斥操作，扩大原子操作的范围

原子操作时无锁操作，属于乐观锁；说起锁的时候，一般属于悲观锁

原子操作存在于各个指令/语言层级，比如“机器层级的原子操作”，“汇编指令层级的原子操作”，“go语言层级的原子操作”等。

锁也存在于各个指令、语言层级，比如说：机器指令层级的锁“，汇编指令层级的锁”，“go语言层级的锁”等

### goroutine的底层实现原理

### goroutine和线程的区别

|            | goroutine                                                    | 线程                                                         |
| ---------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 内存占用   | 创建一个goroutine的栈内存消耗2KB，实际运行过程中，如果栈的空间不够用，会自动进行扩容 | 创建一个线程的栈内存消耗为1MB                                |
| 创建和销毁 | goroutine因为是go runtime负责管理的，创建和销毁的消耗非常小，是用户级 | 线程创建和销毁都会有巨大的消耗，因为要和操作系统打交道，是内核级的，通常解决的方法是线程池 |
| 切换       | goroutine切换只需要保存三个寄存器：PC，SP，BP；goroutine的切换约为200ns，相当于2400-3600条指令 | 当线程切换时，需要保存各种寄存器以便回复现场。线程切换会消耗1000-1500ns相当于12000-18000条指令 |

### goroutine泄露的场景

#### 泄露原因

+ goroutine内进行channel/mutex等读写操作被一直阻塞
+ goroutine内的业务逻辑进入死循环，资源一直无法释放
+ goroutine内的业务逻辑近视长时间等待，并不断新增的goroutine进入等待

#### 泄露场景

+ 如果输出的goroutine数量是不断增加的，就说明存在泄露

### 如何查看正在执行的goroutine数量

在程序中引入pprof package并开启HTTP监听服务

```go
package main

import (
	"net/http"
    _ "net/http/pprof"
)

func main() {
    for i := 0; i< 100;i++ {
        go func() {
            select {}
        }
    }
    go func() {
        http.ListenAndServer("localhost:6060", nil)
    }()
    select{}
}
```

在命令行下执行：

```bash
go tool pprof -http=:1248 http://127.0.0.1:6060/debug/pprof/goroutine
```

### 如何控制并发的goroutine数量

在开发过程中，如果不对goroutine加以控制而进行滥用的话，可能会导致服务整体崩溃。比如耗尽系统资源导致程序崩溃，或者CPU使用过高导致系统忙不过来。因此，我们需要控制goroutine数量。

我们可以通过WaitGroup启动指定数量的goroutine，监听channel的通知。发送者推送信息到channel，信息处理完了，关闭channel，等待goroutine依次退出。

```go
var (
	poolCount = 5
	goroutineCount = 10
)

func pool() {
	jobsChan := make(chan int, poolCount)
	var wg sync.WaitGroup
    for i := 0; i < goroutineCount; i++ {
        wg.Add(1)
        go func() {
            def wg.Done()
            for item := range jobsChan {
                fmt.Println(item)
            }
        }()
    }
    for i := 0; i < 1000; i++ {
        jobsChan <- i
    }
    close(jobsChan)
    wg.Wait()
}
```

### go线程实现模型

线程实现模型主要分为：内核级线程模型（1：1）、用户级线程模型（N:1)、两级线程模型（M:N）,他们的区别在于用户线程与内核线程之间的对应关系。

Go实现的是两级线程模型（M:N），准确的说是GMP模型，是对两级线程模型的改进实现，使它更加灵活地进行线程之间的调度。

### GMP模型和GM模型

### go调度原理

https://www.jianshu.com/p/7c0e3a173930

### go work stealing机制

### go hand off机制

### go抢占式调度



### go如何查看运行时调度信息

有两种方式可以查看一个程序GMP信息，分别是go tool trace和GODEBUG

### go内存分配机制

go语言内置运行时（runtime)，抛弃了传统的内存分配方式，改为自主管理。这样可以自主实现更好的内存使用模型，比如内存池，预分配等等。这样，不会每次内存分配都需要进行系统调用。

**设计思想：** 

+ 内存分配算法采用Google的TCMalloc算法，每个线程都会自行维护一个独立的内存池，进行内存分配时优先从该内存池中分配，当内存池不足时才会加锁向全局内存池申请，减少系统调用并且避免不同线程对全局内存出的锁竞争
+ 把内存切分的非常的细小，分为多级管理，以降低锁的粒度
+ 回收对象内存时，并没有真正释放掉，只是放回预先分配的大块内存中，以便复用。只有内存闲置过多的时候，才会尝试归还部分内存给操作系统，降低整体开销

### go内存逃逸机制

**概念：** 在一段程序中，每一个函数都会有自己的内存区域存放自己的局部变量、返回地址等、这些内存会有编译器在栈中进行分配，每一个函数都会分配一个栈帧，在函数运行结束后进行销毁，但是有些变量我们想在函数运行结束后仍然使用它，那么就需要把这个变量在堆上分配，这种从"栈"上逃逸到"堆"上的现象就成为内存逃逸。

在栈上分配的地址，一般由系统申请和释放，不会有额外性能的开销，比如函数的入参、局部变量、返回值等。在堆上分配的内存，如果要回收掉，需要进行 GC，那么GC 一定会带来额外的性能开销。编程语言不断优化GC算法，主要目的都是为了减少 GC带来的额外性能开销，变量一旦逃逸会导致性能开销变大。
**逃逸机制** 

编译器会根据变量是否被外部引用来决定是否逃逸：

+ 如果函数外部没有引用，则优先放到栈中；

+ 如果函数外部存在引用，则必定放到堆中;

+ 如果栈上放不下，则必定放到堆上;

总结

1. 栈上分配内存比在堆中分配内存效率更高

2. 栈上分配的内存不需要 GC 处理，而堆需要
3. 逃逸分析目的是决定内分配地址是栈还是堆
4. 逃逸分析在编译阶段完成

因为无论变量的大小，只要是指针变量都会在堆上分配，所以对于小变量我们还是使用传值效率（而不是传指针）更高一点。

### go内存对齐机制

为了能让CPU可以更快的存取到各个字段，Go编译器会帮你把struct结构体做数据的对齐。所谓的数据对齐，是指内存地址是所存储数据大小（按字节为单位）的整数倍，以便CPU可以一次将该数据从内存中读取出来。 编译器通过在结构体的各个字段之间填充一些空白已达到对齐的目的。

+ 结构体变量中成员的偏移量必须是成员大小的整数倍

+ 整个结构体的地址必须是最大字节的整数倍（结构体的内存占用是1/4/8/16byte…)

https://blog.csdn.net/qq_53267860/article/details/124881698


