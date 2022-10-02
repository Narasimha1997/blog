---
title: Rate-limiting go-routines (concurrency) in Golang
published: true
---
Go routine is the basic uint of concurrent execution in go, go runtime comes with it's own userspace task scheduler which schedules go routines on top of operating system threads, in this blog we will implement a simple mechanism that can be used to rate-limit the number of go-routines that can be executed or running at any given point of time to avoid burts in resource utilization whenever there is a sudden spike in the number of tasks to be processed.

### The problem
Imagine a scenario where there is a go microservice or a process consuming inputs from an external queue like Redis/Kafka and spins up a goroutine for each input task consumed from the queue, in this model each task is processed concurrently and thus all the tasks are scheduled for execution immediately as soon as they are pushed into the queue from the other end by producer (ignoring the queue latency). This model scales up very well for tasks that don't need much compute/memory and the life-cycle of task processing is short lived, because we can keep on spinning up more and more go-routines to finish more and more tasks while the existing tasks are finished in the background, but this might result in self DoS if the tasks are CPU/memory intensive and have long life-cycle because the tasks will soon stack up and eat off all the available memory/compute while the process still keeps on creating more and more go-routines to process more and more tasks. 

### Solutions
To avoid the problem stated above, we need to have some mechanism that allows only N go-routines to be executing at any given point of time maintaining a determenistic resource utilization. There are two possible solutions for this.
