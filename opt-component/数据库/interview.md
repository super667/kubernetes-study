# 数据库

## 数据库分库分表

什么情况下需要分库分表

### 利用一致性Hash解决MySQL分库扩容

面对的挑战：

+ 分布的Hash算法需要自己实现，或者使用三方组件如Google CityHash

+ 没有现成的迁移组件，需要自己写程序实现迁移规则

+ 需要开发数据校对程序，确保数据完整成功转移

+ 集群节点不固定，要求增加前置代理，屏蔽数据访问细节，且路由规则灵活调整

## 隔离级别如何实现的

## mysql的主从复制

​
一、MySQL主备基本原理
1.如下图所示是基本的主备切换流程

![](/images/mysql_master_slave.png)

MySQL主备切换流程

在状态1中，客户端的读写都直接访问节点A，而节点B是A的备库，只是将A的更新都同步过来，到本地执行。这样可以保持节点B和A的数据是相同的。
当需要切换的时候，就切成状态2。这时候客户端读写访问的都是节点B，而节点A是B的备库。
在状态1中，虽然节点B没有被直接访问，但是依然建议把节点B（也就是备库）设置成只读 （readonly）模式。这样做，有以下几个考虑：
有时候一些运营类的查询语句会被放到备库上去查，设置为只读可以防止误操作；
防止切换逻辑有bug，比如切换过程中出现双写，造成主备不一致；
可以用readonly状态，来判断节点的角色。
**把备库设置成只读了，还怎么跟主库保持同步更新呢？**
因为readonly设置对超级(super)权限用户是无效的，而用于同步更新的 线程，就拥有超级权限。
2.节点A到节点B这条线的内部流程是什么样的？
如下图所示就是执行一个update语句在节点A执行，然后同步到节点B的完整流程图。
![](/images/mysql_master_slave2.png)
主备流程图
备库B跟主库A之间维持了一个长连接。主库A内部有一个线程，专门用于服务备库B的这个长连接。一个事务日志同步的完整过程是这样的：
在备库B上通过change master命令，设置主库A的IP、端口、用户名、密码，以及要从哪个位置开始请求binlog，这个位置包含文件名和日志偏移量
在备库B上执行start slave命令，这时候备库会启动两个线程，就是图中的io_thread和 sql_thread。其中io_thread负责与主库建立连接。
主库A校验完用户名、密码后，开始按照备库B传过来的位置，从本地读取binlog，发给B。
备库B拿到binlog后，写到本地文件，称为中转日志（relay log）。
sql_thread读取中转日志，解析出日志里的命令，并执行。
这里需要说明，后来由于多线程复制方案的引入，sql_thread演化成为了多个线程。

二、配置主从同步的基本步骤
有很多种配置主从同步的方法，可以总结为如下的步骤：

1. 在主服务器上，必须开启二进制日志机制和配置一个独立的ID
2. 在每一个从服务器上，配置一个唯一的ID，创建一个用来专门复制主服务器数据的账号
3. 在开始复制进程前，在主服务器上记录二进制文件的位置信息
4. 如果在开始复制之前，数据库中已经有数据，就必须先创建一个数据快照（可以使用mysqldump导出数据库，或者直接复制数据文件）
5. 配置从服务器要连接的主服务器的IP地址和登陆授权，二进制日志文件名和位置
三、详细配置主从同步的方法
环境准备

CentOS7

mysql安装包：mysql8.0.12_bin_centos7.tar.gz

安装前主备，执行后重启系统：

```bash
[root@hdss7-11 ~]# systemctl stop firewalld
[root@hdss7-11 ~]# systemctl disable firewalld
[root@hdss7-11 ~]# setenforce 0
[root@hdss7-11 ~]# sed -ir '/^SELINUX=/s/=.+/=disabled/' /etc/selinux/config
```

3.1备份主服务器原有数据到从服务器

```bash
mysqldump -uroot -p --all-databases --lock-all-tables > ~/master_db.sql
```

>说明：
>-u ：用户名
>-p ：示密码
>--all-databases ：导出所有数据库
>--lock-all-tables ：执行操作时锁住所有表，防止操作时有数据修改
>~/master_db.sql :导出的备份数据（sql文件）位置，可自己指定

3.2 在从服务器上进行数据还原

```bash
mysql> source /root/master_db.sql;
Query OK, 0 rows affected (0.00 sec)

Query OK, 0 rows affected (0.00 sec)
...
Query OK, 0 rows affected (0.00 sec)

Query OK, 0 rows affected (0.00 sec)
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| seckilling         |
| sys                |
| test               |
+--------------------+
6 rows in set (0.00 sec)

mysql> use test;
Database changed
mysql>
mysql> show tables;
+----------------+
| Tables_in_test |
+----------------+
| t1             |
| t2             |
+----------------+
2 rows in set (0.00 sec)
```

3.3主服务器配置
3.3.1 在配置文件/data/mysql/conf/my.cnf中，修改如下几个字段

```bash
[mysqld]
server_id                       = 1  #服务器 id ，主从机器在同一局域网内必须全局唯一，不能相同
log-bin                         = /data/mysql/binlog/binlog
log_bin_index                   = /data/mysql/binlog/binlog.index
binlog-do-db                    =palan-dev    #待同步的数据库，如果有多个以空格隔开db1 db2 db3 ....
binlog-ignore-db                =mysql  #不同步的数据  如果有多个以空格隔开db1 db2 db3 ....
```

3.3.2查看主服务器是否开启binlog日志，如果没有开启则开启

```bash
mysql> show variables like '%log_bin%';
+---------------------------------+---------------------------------+
| Variable_name                   | Value                           |
+---------------------------------+---------------------------------+
| log_bin                         | ON                              |
| log_bin_basename                | /data/mysql/binlog/binlog       |
| log_bin_index                   | /data/mysql/binlog/binlog.index |
| log_bin_trust_function_creators | OFF                             |
| log_bin_use_v1_row_events       | OFF                             |
| sql_log_bin                     | ON                              |
+---------------------------------+---------------------------------+
6 rows in set (0.00 sec)
```

查看生成的binlog日志文件

```bash
[root@wxc wxc]# ls /data/mysql/binlog/ -al
total 2388
drwxr-xr-x. 2 mysql mysql     194 Nov 15 19:16 .
drwxr-xr-x. 7 mysql mysql      66 Nov 15 16:09 ..
-rw-r-----. 1 mysql mysql     156 Nov 15 17:18 binlog.000001
-rw-r-----. 1 mysql mysql     170 Nov 15 17:18 binlog.000002
-rw-r-----. 1 mysql mysql    1775 Nov 15 17:40 binlog.000003
-rw-r-----. 1 mysql mysql    1122 Nov 15 18:25 binlog.000004
-rw-r-----. 1 mysql mysql 2409901 Nov 15 19:10 binlog.000005
-rw-r-----. 1 mysql mysql     231 Nov 15 19:10 binlog.000006
-rw-r-----. 1 mysql mysql     210 Nov 15 19:10 binlog.000007
-rw-r-----  1 mysql mysql     191 Nov 15 19:16 binlog.000008
-rw-r-----  1 mysql mysql     264 Nov 15 19:16 binlog.index
```

3.3.3给从库授权账号，让从库可以复制

```bash
mysql> CREATE USER 'rootslave'@'10.4.7.139' IDENTIFIED WITH mysql_native_password BY 'qazWSX123+++';
mysql> grant replication slave on *.* to 'rootslave'@'10.4.7.139';
mysql> FLUSH PRIVILEGES;
```

重新启动MySQL

3.3.4查看主库状态

```bash
mysql> show master status\g;
+---------------+----------+--------------+------------------+--------------------------------------------+
| File          | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set                          |
+---------------+----------+--------------+------------------+--------------------------------------------+
| binlog.000008 |      191 |              |                  | 7fe7893e-2723-11eb-bd3b-000c2957e9b2:1-150 |
+---------------+----------+--------------+------------------+--------------------------------------------+
1 row in set (0.01 sec)

ERROR: 
No query specified
```

3.4从服务器配置
3.4.1 在配置文件/data/mysql/conf/my.cnf中，修改如下几个字段

```bash
server_id                       = 2  # 这里的id一定不要和主库id相同
```

```bash
systemctl restart mysqld             # 重新启动数据库
```

3.4.2 登录数据库

```bash
mysql> change master to master_host='10.4.7.138',master_user='rootslave',master_password='qazWSX123+++',master_log_file='binlog.000005',master_log_pos=191;
mysql> start slave;
```

3.4.3查看从库状态

```bash
mysql> show slave status\G;
*************************** 1. row ***************************
               Slave_IO_State: Waiting for master to send event
                  Master_Host: 10.4.7.138
                  Master_User: rootslave
                  Master_Port: 3306
                Connect_Retry: 60
              Master_Log_File: binlog.000008
          Read_Master_Log_Pos: 191
               Relay_Log_File: wxc-relay-bin.000011
                Relay_Log_Pos: 391
        Relay_Master_Log_File: binlog.000008
             Slave_IO_Running: Yes
            Slave_SQL_Running: Yes
              Replicate_Do_DB: 
          Replicate_Ignore_DB: 
           Replicate_Do_Table: 
       Replicate_Ignore_Table: 
      Replicate_Wild_Do_Table: 
  Replicate_Wild_Ignore_Table: 
                   Last_Errno: 0
                   Last_Error: 
                 Skip_Counter: 0
          Exec_Master_Log_Pos: 191
              Relay_Log_Space: 829
              Until_Condition: None
               Until_Log_File: 
                Until_Log_Pos: 0
           Master_SSL_Allowed: No
           Master_SSL_CA_File: 
           Master_SSL_CA_Path: 
              Master_SSL_Cert: 
            Master_SSL_Cipher: 
               Master_SSL_Key: 
        Seconds_Behind_Master: 0
Master_SSL_Verify_Server_Cert: No
                Last_IO_Errno: 0
                Last_IO_Error: 
               Last_SQL_Errno: 0
               Last_SQL_Error: 
  Replicate_Ignore_Server_Ids: 
             Master_Server_Id: 1
                  Master_UUID: 7fe7893e-2723-11eb-bd3b-000c2957e9b2
             Master_Info_File: mysql.slave_master_info
                    SQL_Delay: 0
          SQL_Remaining_Delay: NULL
      Slave_SQL_Running_State: Slave has read all relay log; waiting for more updates
           Master_Retry_Count: 86400
                  Master_Bind: 
      Last_IO_Error_Timestamp: 
     Last_SQL_Error_Timestamp: 
               Master_SSL_Crl: 
           Master_SSL_Crlpath: 
           Retrieved_Gtid_Set: 7fe7893e-2723-11eb-bd3b-000c2957e9b2:10-150
            Executed_Gtid_Set: 7fe7893e-2723-11eb-bd3b-000c2957e9b2:1-7:10-150
                Auto_Position: 0
         Replicate_Rewrite_DB: 
                 Channel_Name: 
           Master_TLS_Version: 
       Master_public_key_path: 
        Get_master_public_key: 0
1 row in set (0.10 sec)
```

其中Slave_IO_Running和Slave_SQL_Running表示两个线程的状态，这两个线程必须都为YES，如果有一个为no都不会进行主从同步

## msyql默认隔离级别为什么是可重复读

在读提交的隔离级别下开启两个会话：按上面的顺序执行命令。最后得到的数据库中有一条记录。

![sql](/images/sql_rc.png)

在mysql5.1之前mysql的逻辑操作日志binlog默认的是statement模式，用于恢复和复制。主从复制的binlog采用的是statement模式。从库定时从主库的日志文件复制到本地日志，从库根据本地日志(继中日志)的变化执行sql语句。
根据上面的情况，当命令提交前，才会向日志文件中写入。所以日志文件中的sql顺序是先增加后删除，所以在从库中数据库是没有数据的。而主库中有数据，这就造成了主从不一致的情况。
mysql5.1的binlog又提供了两种格式row和fixed。mysql会根据情况选择优先使用那种格式。就算是这样也不能避免主从不一致的问题。将修改的语句串行化才能解决这个问题，将隔离离别提升为可重复读就能将写入的binlog语句串行化。然后从库根据binlog执行，binlog保证了主库相同的执行顺序，也就保证了主从的一致性。

当mysql的默认隔离级别调整为可重复读时，在该隔离级别下引入了间隙锁。当session1执行delete语句是，会锁住间隙。那么session2执行插入语句时就会阻塞住。只有session1提交之后，session2才能执行。实现了binlog的语句串行化，解决了主从不一致的问题。

## MySQL数据库索引b+树深度大概是多少?

这要从b+树的结构和数据库索引大小去分析问题，索引字段占内存多少，指针占内存大小

1. b+树结构

2. 计算

在mysql索引中，索引页默认大小为16k;

```bash
show variables like 'innodb_page_size'; # 数据库中查询数据页的大小
```

一个页可以理解为一个节点（非叶子节点或者叶子节点）
叶子节点只存储数据（索引值和链表指针不考虑）
非叶子节点存储（索引值+指针）=8b+6b=14b
假设一行数据=1kb，一个叶子节点可以存放16条数据
非叶子节点最多有叶子节点=非叶子节点容量/14b=16kb/14b = 16x1024/14=1170个索引值
如果树高度为2，可以存放的数据：
>    高度为2，根节点就一个节点，一个节点1170个指针，相当于有1170个叶子节点，一个叶子节点有16条数据，那么结果=1170x16=18724条数据

如果树高度为3，可以存放的数据：
> 每个节点都有1170个指针，那么3层就是二层中所有的指针各自对应1170个指针，那么结果=1170x1170x16=21902400条数据


### binlog

### redolog

### undolog

### Explain执行计划详解

Explain（执行计划），使用explain关键字可以模拟优化器执行sql查询语句，从而知道MySQL是如何处理sql语句。
explain主要用于分析查询语句或表结构的性能瓶颈。

#### Explain包含的信息

```bash
mysql> EXPLAIN
    -> SELECT * FROM t_custom t1
    -> LEFT JOIN t_custom_acounts t2 ON t1.custom_id = t2.custom_id
    -> LEFT JOIN t_ext_sign t3 ON t2.custom_id = t3.custom_id
    -> WHERE t1.custom_id = '02241EE988CD4955EF31DAC397844D77';
+----+-------------+-------+------------+-------+---------------+---------------+---------+-------+------+----------+----------------------------------------------------+
| id | select_type | table | partitions | type  | possible_keys | key           | key_len | ref   | rows | filtered | Extra                                              |
+----+-------------+-------+------------+-------+---------------+---------------+---------+-------+------+----------+----------------------------------------------------+
|  1 | SIMPLE      | t1    | NULL       | const | PRIMARY       | PRIMARY       | 386     | const |    1 |   100.00 | NULL                                               |
|  1 | SIMPLE      | t2    | NULL       | ref   | idx_custom_id | idx_custom_id | 386     | const |    1 |   100.00 | NULL                                               |
|  1 | SIMPLE      | t3    | NULL       | ALL   | NULL          | NULL          | NULL    | NULL  |    8 |   100.00 | Using where; Using join buffer (Block Nested Loop) |
+----+-------------+-------+------------+-------+---------------+---------------+---------+-------+------+----------+----------------------------------------------------+
3 rows in set, 1 warning (0.00 sec)
```
1. id：select查询的序列号，包含一组数字，表示查询中执行select子句或操作表的顺序，该字段通常与table字段搭配来分析。
+ id相同，执行顺序从上到下，搭配table列可知，执行顺序为t1->t3->t2
+ id不同，如果是子查询，id的序号会递增，id值越大越优先执行；
+ id相同不同同时存在，在所有组中，id值越大执行优先级越高

  **总结：id的值表示select子句或表的执行顺序，id相同，执行顺序从上到下，id不同，值越大的执行优先级越高。**

2. **select_type:** 查询的类型，主要用于区别普通查询，联合查询，子查询等复杂的查询，值主要有六个：
+ SIMPLE： 简单的select查询，查询中不包含子查询或union查询
+ PRIMARY： 查询中若包含任何复杂的子查询，最外层查询为PRIMARY，也就是最后加载的是PRIMARY
+ SUBQUERY： 在select或where列表中包含了子查询，就标记为SUBQUERY
+ DERIVED 在from列表中包含的子查询就会标记为DERIVED（衍生），MySQL会递归执行这些子查询，将结果放在临时表中。
+ UNION： 若第二个select出现在union后，则被标记为UNION，若union包含在from子句的子查询中，外层的select被标记为DERIVED
+ UNION RESULT: 从union表获取的select

3. table： 显示sql操作那张表
4. partitions： 官方定义为The matching partitions，值为NULL表示表未被分区
5. type： 表示查询所使用的访问类型
> type的值分为8种，从好到差依次为： system>const>eq_ref>ref>range>index>ALL
ALL：Full Table Scan， MySQL将遍历全表以找到匹配的行
index：Full Index Scan，index与ALL区别为index类型只遍历索引树
range：只检索给定范围的行，使用一个索引来选择行
ref：表示表的连接匹配条件，即哪些列或常量被用于查找索引列上的值，查指定值，而不是范围
eq_ref：类似ref，区别就在使用的索引是唯一索引，对于每个索引键值，表中只有一条记录匹配，简单来说，就是多表连接中使用primary key或者 unique key作为关联条件
const、system：当MySQL对查询某部分进行优化，并转换为一个常量时，使用这些类型访问。如将主键置于where列表中，MySQL就能将该查询转换为一个常量，system是const类型的特例，当查询的表只有一行的情况下，使用system
NULL：MySQL在优化过程中分解语句，执行时甚至不用访问表或索引，例如从一个索引列里选取最小值可以通过单独索引查找完成。
6. possibles_keys: 显示可能应用在表中的索引，可能一个或多个。查询涉及到的字段若存在索引，则将该索引列出，不一定被实际查询使用。
7. key： 实际中使用到的索引，如为NULL表示未使用索引。若查询中使用了覆盖索引，则索引和查询的select字段重叠
8. key_len: 表示索引中所使用的字节数，可通过该列 查询中使用的索引长度。在不损失精确性的情况下，长度越短越好。
9. ref： 显示关联的字段。如果使用常数等值查询，则显示const，如果是连接查询，则会显示关联的字段。
10. rows： 根据表统计信息及索引选用情况大致估算找到所需记录所要读取的行数。当然该值越小越好。
11. filtered： 百分比值，
12. Extra：显示十分重要的额外信息
+ Using filesort表明mysql会对数据使用一个外部的索引排序，而不是按照表内的索引顺序进行读取，mysql中无法利用索引完成的排序称为文件排序
+ Using temporary：使用临时表保存中间结果，常见于排序order by和分组查询group by。非常危险，十死无生，急需优化
+ Using index: 表明相应的select操作中使用的覆盖索引，避免访问表的额外数据行，效率不错。如果同时出现了Using Where，表明索引被用来执行索引键值的查找；如果没有同时出现Using where,表明索引用来读取数据而非执行查找操作
+ Using where： 使用where过滤条件
+ Using join buffer： 该值强调了在获取连接条件是没有使用索引，而且需要再缓冲区来存储中间结果。如果出现了这个值，那应该注意根据查询的具体情况可以需要添加索引来改善性能
+ impossible whre： 这个值强调了where语句会导致没有符合条件的行
+ Select tables optimized away: 这个值意味着仅通过使用索引，优化器可能从聚合函数结果中返回一行
+ No table used： Query语句中使用from dual 或不含任何from子句

## 慢sql排查，解决方法

1. 数据量
2. 有没有建索引
3. 查询有没有使用索引
4. 查询执行计划
5. 