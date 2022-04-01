---
title: Building a secondary index of 1.5 million words for search and auto-complete using Redis cache
published: true
---
Recently I was playing around with building a [secondary index](https://practice.geeksforgeeks.org/problems/what-is-secondary-indices) for some documents to make them easily searchable using a search interface with auto-complete suggestions. I was interested to explore [Redis](https://redis.io/) for this task because it stores data completely in-memory. Though it is a simple Key-Value store with `O(1)` `GET` and `SET` operations, it provides many additional data-structures like Sorted Set, Hash Set, FIFO Queue etc. Moreover, it provides a simple protocol for communication over raw TCP (and UNIX) sockets - all these factors makes Redis a suitable candidate for building secondary indexes that reside completely in memory and can be used for retrieving results really quickly (with microsecond latencies). In this post, I will explain how we can exploit Redis to store large indexes for search and auto-complete and how we can further optimize it to scale the solution.

### The problem of prefix-search
The problem here is simple, given a list of N words, how will you search for a given word in that list quickly? Extending this problem further, how will get a list of M words that start with the given prefix? (example: If I have words - `[banana, bayer, bay]` then the prefix `bay` should return `[bay, bayer]`, similarly the prefix `ba` should return `[banana, bayer, bay]`) - In Computer Science, this is called "Prefix Search", because in a large search space of N strings, you are finding a set of M strings that start with the given prefix (M <= N), the naive way to solve this problem is to iterate over all the string one at a time and checking if it has the given substring as it's prefix, for that we can use [strcmp()](https://www.programiz.com/c-programming/library-function/string.h/strcmp) or [memcmp()](https://www.cplusplus.com/reference/cstring/memcmp/) - this solution is trivial, it works the best if we have a smaller search space, but this solution doesn't scale well if we have larger search spaces (like 1 million words) because this is a `O(N)` solution, as `N` increases the time taken to search also increases, to scale the solution well, we need a data-structure that takes less than O(N) time. The most efficient way to tell if a string is present in the given set is to use hash-table, we hash the string, if that hash is present in the set, then it exists - this is an ideal way of search where the time-complexity is almost O(1) in most of the cases, this solution scales well, but it fails to solve our problem, our problem here is to obtain a subset of strings that start with the same prefix in a given large set of strings. 

### Trie - a naive prefix search tree:
In the previous section we looked at O(n) solution which actually solved the problem, but not scalable, we also saw O(1) solution that is scalable but didn't actually solve the problem. One of the possible solutions that is slower than hash-table and faster than linear search is to use a trie. [Trie](https://en.wikipedia.org/wiki/Trie) data-structure is also known as prefix-tree. In simple words, every parent in the prefix tree is a prefix of the child. (i.e if we have two words `ban` and `bay` then the tree has a structure `b->a->(n, y)`, `b` is the prefix of `a` and `ba` is the prefix of `n` and `y`, so all the parents in that path is a prefix of the upcoming children in the same path). Here is a representation of prefix tree:

<div style="text-align: center">
    <img src="./assets/redis-auto/naive-trie.png" alt="drawing" width="400" height="400"/>
</div>

The above trie can be used for efficient prefix search on words `[cart, car, cat, cod, coin, cold]`. Once we have a prefix, we can traverse one node at a time based on each character in the prefix (if it exists in the trie), once our prefix ends we can do depth-first-search (or [DFS](https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/)) traversal over all the children starting from the node where our prefix ended to obtain all the possible strings that has the given prefix. This solution has time-complexity `O(M) + O(P + E)`, where `M` is the length of the prefix, `P` is the number of nodes that are in the sub-tree starting from the last prefix node and `E` is the number of edges involved in the sub-tree on which DFS is applied. (Note: Here the time-complexity of DFS is `O(P + E)` which has been added to `O(M)`, if we ignore the edges, then the time complexity is `O(M) + O(P)`), if you consider the time-complexity only to search the prefix then it is `O(M)`. This looks fine the time-complexity is far better than `O(N)`, but this is not always better, because most of the prefix search problems have smaller `M` value (i.e smaller prefix length), for example if I have 10000 strings in a set all starting with prefix `b->a`, then using `ba` as the prefix will lead to negligible `O(M)` and higher `O(P + E)`, but this is far better solution than linear search solution. This problem can be avoided by using an additional hash-table that stores list of all prefixes as keys and each key has a list of strings that starts with the given prefix as value, by this way we can avoid `O(P + E)` component in our prefix search, a similar approach has been suggested [here](https://prefixy.github.io/#prefix-hash-tree), this data-structure is called Prefix-Hash tree. The diagram below shows how a prefix-hash tree looks like for the set of six words - `[cart, car, cat, cod, coin, cold]`

<div style="text-align: center">
    <img src="./assets/redis-auto/naive-hash-tree.png" alt="drawing" width="400" height="400"/>
</div>

While this data-structure is highly efficient than a naive trie (time-complexity: `O(M) + O(1)`), it consumes lot of memory - it can be noted from the above diagram, we are duplicating the strings across multiple locations in the hash-table. (Imagine the size of this table for 10000 strings). In the coming sections, we will see how Redis Sorted sets can be used for solving this problem with some compromise on the time complexity.

### Redis sorted sets
We looked at various approaches for prefix-search in previous sections, now let us implement one using Redis. As mentioned earlier, Redis is a key-value store that redis provides [many data-structures](https://redis.io/docs/manual/data-types/) like Sorted set, FIFO Queue, Hash set etc. A simple solution is to insert each string as a key with some dummy value (for example `banana:1`, `apple:1`, `applied:1`) into the key-value store (we can use `SET` command), this solution has `O(1)` time complexity for checking whether the given string exists or not, this is done by hashing the string and checking it against the key-value store, which is implemented using a hash-table (using `GET` command), but this method cannot be used for prefix search, for this we need to scan the entire key-value store using `<prefix>*` regular-expression, this can be done using [SCAN](https://redis.io/commands/scan/) command, the time complexity is `O(N)` because this approach is nothing but a linear search performed on all the keys in the hash-table. What we actually need is a data-structure that provides time-complexity lesser than `O(N)`, fortunately Redis provides [Sorted Set](https://redis.com/ebook/part-2-core-concepts/chapter-3-commands-in-redis/3-5-sorted-sets/), which provides `O(logN)` time-complexity insertion, deletion and retrievals. Sorted sets also called as `zsets` are built using combinations of two vanilla data structures - Hash Tables and [Skip-Lists](https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf). Skip-Lists improve the efficiency of linear linked list traversal by allowing us to skip unnecessary nodes in between and start from a point where the element we are looking for is more likely to be present, this is made possible by having another metadata linked list that contains nodes storing pointers to convenient nodes in the main linked list from where we can start traversal to find a given element, by this way it reduces the search space by avoiding a linear search over all the nodes. Here is an example:
<div style="text-align: center">
    <img src="./assets/redis-auto/skip.png" alt="drawing" width="600" height="300"/>
</div>

In order to search `56` in the given linked list, we can traverse the `Express Line` first , the `Express line` also called as `Metadata List` contains pointers intermediate locations on the main list. Since nodes are sorted in increasing order on the main list, we can be sure that node `40` is the probable starting point because `40 < 56 < 60` so we skip to node `40` directly on the main list instead of starting from `10`, by this way we can avoid unnecessary traversal from `10` to `40` on the main list. The efficiency of skip-list varies based on the number of nodes we have in express line, if there are no nodes in express line, then the time complexity is `O(N)` as more and more nodes are added to the express line, the efficiency improves, we can also have multiple levels express lines with pointers tp multiple locations to improve the speed (read [this](https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf) paper to understand the concept behind skip-lists completely). Skip-list can be approximated to a completely balanced binary search tree ([BST](https://www.geeksforgeeks.org/binary-search-tree-data-structure/)) in it's best case. In general it is a balanced tree with `O(logN)` as the time-complexity for search (traversal). 

Redis sorted set is implemented on top of skip-list, so it provides `O(logN)` insertion and search capabilities. To understand how Sorted Sets are implemented, check out the source code - [t_zset.c](https://github.com/redis/redis/blob/unstable/src/t_zset.c).

### Scores and Lexicographic ordering in Sorted Sets:
Sorted sets in Redis are sorted based on a number called `Score` or also called as `Rank`, for example if I insert three strings `[banana, bay, bayer]` with ranks `[2, 0, 1]`, then they are automatically sorted as `[bay:0, bayer:1, banana:2]`. Let's check this out by creating a sorted set by name `test` (we can insert elements into sorted set using [ZADD](https://redis.io/commands/zadd/) command and use [ZRANGEBYSCORE](https://redis.io/commands/zrangebyscore/) command to query the sorted set by scores between 0 and 2).
```
127.0.0.1:6379> ZADD "test" 2 "banana"
(integer) 1
127.0.0.1:6379> ZADD "test" 0 "bay"
(integer) 1
127.0.0.1:6379> ZADD "test" 1 "bayer"
(integer) 1
127.0.0.1:6379> ZRANGEBYSCORE test 0 2
1) "bay"
2) "bayer"
3) "banana"
``` 
But can we have multiple entries with same score? Yes, Redis allows that too, when we insert multiple entries to the sorted set with the same score, they are sorted lexicographically. This ordering is performed at bytes-level so any data type can be sorted lexicographically by comparing their raw bytes representation (using `memcmp()`). For example, let us try inserting `[pickle, pineapple, poet, pot, pen]` to a sorted set called "test2" with same score 0.
```
127.0.0.1:6379> ZADD "test2" 0 "pickle"
(integer) 1
127.0.0.1:6379> ZADD "test2" 0 "pineapple"
(integer) 1
127.0.0.1:6379> ZADD "test2" 0 "poet"
(integer) 1
127.0.0.1:6379> ZADD "test2" 0 "pot"
(integer) 1
127.0.0.1:6379> ZADD "test2" 0 "pen"
(integer) 1
127.0.0.1:6379> ZRANGEBYSCORE test2 0 0
1) "pen"
2) "pickle"
3) "pineapple"
4) "poet"
5) "pot"
```
If you see the above example, though elements were inserted in a different order, they appeared in a lexicographically sorted order. We can use the command [ZRANGEBYLEX](https://redis.io/commands/zrangebylex/). 
