---
title: JIT (Just-in-time) compiled python
published: true
---
The official implementation of python known as CPython is [one of the oldest and still standing implementation of python (as per the statement by Guido Von Rossum himself)](https://www.youtube.com/watch?v=-DVyjdw4t9I), being popular among all the implementations, CPython still lacks many much needed features like JIT, multi-threading and generates the byte-code without much compile-time optimizations which makes it much slower to be used in many production environments that process workloads at scale.

(Incomplete)