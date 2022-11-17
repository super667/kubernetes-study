[toc]

## python有哪些特点和优点

作为一门编程语言，python主要有以下特点和优点：

+ 可解释
+ 具有动态特性
+ 面向对象
+ 简明简单
+ 开源
+ 具有强大的社区支持
+ 。。。

## 深拷贝和浅拷贝之间的区别是什么？

深拷贝就是将一个对象拷贝到另一个对象中，这意味着如果你对一个对象的拷贝做出改变时，不会影响原对象。在Python中，我们使用函数deepcopy()执行深拷贝，

```python
import copy
b = copy.deepcopy(a)
```



而浅拷贝则是将一个对象的引用拷贝到另一个对象上，所以如果我们在拷贝中改动，会影响到原对象。我们使用函数function()执行浅拷贝，使用如下所示：

```python
b = copy.copy(a)
```

## 列表和元组之间的区别是？

二者之间主要区别是列表是可变的，而元组是不可变的

## 在python中如何实现多线程

一个线程就是一个轻量级进程，多线程能让我们一次执行多个线程。我们都知道python是多线程语言，其内置多线程工具包。

Python中的GIL（全局解释器锁）确保一次执行单个线程。一个线程保存GIL并在将其传递给下个线程之前执行一些操作，这会让我们产生并行运行的错觉。但实际上，只是线程在CPU上轮流运行。当然，所有的传递会增加程序执行的内存压力。

## python中的继承

当一个类继承自另一个类，他就被称为一个子类/派生类，继承自父类/基类/超类。他会继承、获取所有类成员（属性和方法）。

继承能让我们重新使用代码，也能更容易的创建和维护应用。python支持如下种类的继承：

+ 单继承：一个类继承自单个基类
+ 多继承：一个类继承自多个基类
+ 多级继承：一个类继承自单个基类，后者则继承自另一个基类
+ 多个类继承自单个基类
+ 混合继承

## python中是如何管理内存的

python有一个私有堆空间来保存所有的对象和数据结构。作为开发者，我们无法访问它，是解释器在管理它。但有了核心API后，我们可以访问一些工具。python内存管理器控制内存分配。

另外内置垃圾回收器会回收使用所有未使用的内存，所以使其适用于堆空间。

## 解释python中的help函数和dir函数

help函数是一个内置函数，用于查看函数或模块用途的详细说明

dir函数是python内置函数，dir()函数不带参数时，返回当前范围内的变量、方法 和定义的类型列表；带参数时返回参数的属性、方法列表

## 当退出python时，是否释放全部内存？

No，循环引用其他对象或引用自全局命名空间的对象的模块，python退出时，并非完全释放

另外也不会释放C库保留的内存部分

## 什么是猴子补丁？

在运行期间动态修改一个类或模块

```python
>>> class A:
    def func(self):
        print("Hi")
>>> def monkey(self):
print "Hi, monkey"
>>> m.A.func = monkey
>>> a = m.A()
>>> a.func()

```

## 请写一个python逻辑，计算一个文件中的大写字母数量

```python
>>> import os

>>> os.chdir('C:\\Users\\lifei\\Desktop')
>>> with open('Today.txt') as today:
    count=0
    for i in today.read():
        if i.isupper():
            count+=1
print(count)

```

## 如何就地操作打乱一个列表的元素？

```python
>>> from random import shuffle
>>> shuffle(mylist)
>>> mylist

```

## 字符串提供的函数

```python
'Ayshi'.upper()
'Ayshi'.lower()
```

## python中！=和is not区别

is,is not比较的是两个对象的内存地址

==， ！=比较的是两个对象的值

## 为什么不建议以下划线作为标识符的头

因为Python并没有私有变量的概念，所以约定速成以下划线为开头来声明一个变量为私有。所以如果你不想让变量私有，就不要使用下划线开头。

## 声明多个变量并赋值

```python
>>> a,b,c=3,4,5 #This assigns 3, 4, and 5 to a, b, and c respectively
>>> a=b=c=3 #This assigns 3 to a, b, and c
```

## python为什么执行慢，我们该如何改进它？

为了提高python的速度，我们可以使用CPython，Numba，或者我们可以优化一下代码

+ 减少内存占用
+ 使用内置函数和库
+ 将计算移到循环外
+ 保持小的代码库
+ 避免不必要循环

### python有什么特点？

1. 易于编码
2. 免费和开源语言
3. 高级语言
4. 易于调试
5. OOPS支持
6. 大量的标准库和第三方模块
7. 可扩展性
8. 用户友好的数据结构

## 如何在Python中管理内存

## python中的可迭代对象和迭代器

python中for循环的原理就是调用可迭代对象的\_\_iter\_\_方法得到迭代器对象，然后调用__next__方法进行取值，直到对象抛出StopIteration异常。

```
class Range:
    def __init__(self, start, stop, step=2):
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        if self.start < self.stop:
            n = self.start
            self.start += self.step
            return n
        raise StopIteration

for i in Range(0, 100,):
    print(i)
```

## 问题点

1.优化点

2.难点

3.介绍项目的时候，背景，为什么这么做等。

blpop,sleep轮询

docker label问题



jwt相关

https://segmentfault.com/a/1190000039752568?utm_source=sf-hot-article













