---
title: System-wide syscalls tracing and monitoring in Linux using bpftrace 
published: true
---
If you are from Computer Science background probably you might have heard of "system-calls" (also referred as "syscalls" to keep it short), if you haven't then you can read [this](https://www.javatpoint.com/system-calls-in-operating-system) interesting beginner friendly article on system-calls. In general, system-calls are the glue between Operating System kernel and User applications. System Calls are required for everything, without system-calls the user application cannot do anything, because user applications need kernel support for memory management, reading and writing from/to disk, display, network interface, audio devices etc, in general, the user application becomes virtually useless if it cannot make system calls. Let us write and compile a simple C program that reads a file from the disk and outputs it, once we compile the program, we will use `strace` to see how many system-calls our program makes to get the job done. (I will be using `Ubuntu 21.04` for all the experiments in this article).

So this is our C program, it's simple and straightforward, we are just opening the file called `text.txt` (assume that it is present) using `fopen()`, reading the first line using `fscanf` and printing it to the terminal using `printf`.

```C
#include <stdio.h>

int main(int argc, char **argv) {
    char buffer[1024];
    FILE *fptr = fopen("text.txt", "r");
    if (fptr == NULL) {
            printf("failed to open text.txt");
    }
    fscanf(fptr, "%[^\n]", buffer);
    printf("Read data: %s\n", buffer);
}
```
Let's compile this:
```
gcc read_file.c -o read_file
```
We should be able to run the binary `read_file` which works because the `text.txt` is present, now let's trace what all system calls this program made, to know this we can use [strace](https://man7.org/linux/man-pages/man1/strace.1.html) (this tool will be installed by default on most of the linux distributions). We will use `strace`to count the number of system calls made by this program when executed. Let's run:
```
strace -C ./read_file
```
This should print a table showing some basic statistics of the system calls made during the program execution.
```
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 49.67    0.000301         301         1           execve
 14.69    0.000089          11         8           mmap
  6.44    0.000039          13         3           openat
  4.46    0.000027           9         3           mprotect
  4.46    0.000027           6         4           newfstatat
  3.47    0.000021           5         4           pread64
  3.14    0.000019          19         1           munmap
  2.81    0.000017           8         2           close
  2.64    0.000016           5         3           brk
  2.15    0.000013           6         2           read
  2.15    0.000013          13         1         1 access
  1.65    0.000010          10         1           write
  1.65    0.000010           5         2         1 arch_prctl
  0.66    0.000004           4         1           lseek
------ ----------- ----------- --------- --------- ----------------
100.00    0.000606          16        36         2 total
```
As expected, we have have `openat`, `read` and `write` system calls present in the table, but why are there so many other system calls? And also, `openat` is called thrice but we are opening the file only once - Well, these are expected, because C compiler is going to add some wrapper functions that are going to wrap our main function to execute it conveniently to bootstrap our code in an environment suitable for execution, in this process, some of the core libraries are also dynamically opened and loaded, thus we have lot of other system calls which we did not call.

### strace
`strace` provides lot of other capabilities as well, for example we can also attach it to a PID and trace all the system calls made by that process (We can use `strace -p <PID>`) we can also configure `strace` to suite many use-cases by using one or more options provided by it, just run `strace -h` to list available options. But we have a problem with `strace` - i.e the overhead of tracing. To understand the problems of `strace` we need to look at `ptrace` - the underlying system call used by `strace`.

### About ptrace() system call:
`strace` and most of the tracing tools like [GDB](https://cs.baylor.edu/~donahoo/tools/gdb/tutorial.html) make use of `ptrace` system call provided by Linux Kernel. Any program can use `ptrace` system call with various options to get itself attached to another process and set breakpoints to examine the internal state of that process. In our case, `strace` starts as the parent process and calls `ptrace` initially passing `PTRACE_ATTACH` and the PID of the child process that needs to be traced - in our case it is `read_file` built from `read_file.c`, the kernel then makes some checks and privilege verifications before allowing `strace` to get attached to the child process, if passed the kernel initializes some internal data structures required for tracing and notifications. Next, `strace` calls `ptrace` again, but this time it passes `PTRACE_SYSCALL` flag, which makes the kernel to write `TIF_SYSCALL_TRACE` flag into the child processes's internal thread state, which is like an indication that tracing is enabled for that process. After this, the child process is allowed to execute and `strace` waits for the child to make system calls. If child makes any system call, the `TIF_SYSCALL_TRACE` will be seen by the kernel's system call entry level function, which will force the child process to trap (halt) by sending `SIGTRAP` signal. Now that the child process is halted, kernel collects and passes the architecture specific and architecture independent state data of the halted child process to the parent, i.e to our `strace` process. `strace` can now parse this information and use it to display the tracing information. After this, child process is allowed to execute the system call, once system call is complete, another trap is generated by passing `SIGTERM` to the child and parent is notified about the completion of system call again by passing all the architecture specific and architecture independent state data, then the child process is allowed to execute by resuming it. This cycle repeats for all the system calls made by the child process. So the tracer i.e the parent (`strace`) is notified twice per system call - one at system call entry and another one at exit. 

 Now that we know about `ptrace` system call and the tool `strace` built on top of it, we can look at the disadvantages of this approach:
1. `ptrace` cannot be used for system wide tracing - this is because we need to attach tracing to all the available processes on the system which is not recommended. In general `ptrace` is process specific.
2. This method involves lot of interactions between kernel and user-space because `ptrace` passes the entire information to the tracer tool via a signal, this information can be huge and it needs to be copied into a buffer in the user-space.
3. Child process needs to be interrupted upon system call - `ptrace` sets `TIF_SYSCALL_TRACE` in the thread state information of the child process which makes it to pause it's execution upon entry and exit of the system call, this can be a bottleneck for a process that heavily depends on system calls. (Example: Disk or Network intensive applications)

All these drawback doesn't mean `ptrace` is bad, tools written using `ptrace` can be used for low level debugging and tracing, but these tools are not suitable for continuous system-wide tracing.

### eBPF and bpftrace
Recently, starting from Linux kernel 4.x, the community introduced a new functionality called [Extended Berkeley Packet Filters (eBPF)](https://ebpf.io/), eBPF is a small virtual machine that executes a BPF byte-code (BPF is a simple filtering and data crunching language, before eBPF, BPF was used to filter and analyze network traffic by directly attaching it to data-link layer, read more about BPF [here](https://en.wikipedia.org/wiki/Berkeley_Packet_Filter).) completely in the kernel space, eBPF scripts can be attached to many event triggers within the kernel (like interrupts, system calls, breakpoints, function calls etc), kernel maintains the mapping of these event triggers and attached eBPF scripts then it automatically executes these scripts whenever any of such events occur. This is a very powerful kernel feature, because it allows developers to extend the functionality of the kernel in a event driven way without writing and loading complex [kernel modules](https://linux-kernel-labs.github.io/refs/heads/master/labs/kernel_modules.html). It is also possible to dynamically attach/remove these scripts and receive the outputs back in the user-space. Let's see how this can be helpful for monitoring and tracing:
1. Completely Event Driven: We don't have to anymore stop the execution of the child process (like we did when using `ptrace`), these eBPF scripts are executed automatically when the event occurs.
2. Data Crunching in the kernel: If our analysis involves lots of data, we can filter and aggregate them in the kernel itself without transferring it to the user-space - this is because eBPF VM runs in kernel-space.
3. Can monitor system-wide events: eBPF is not restricted to one process or thread, it is system-wide because it runs in the kernel. 

This solves some of the issues we had with `ptrace` implementation. Recently [iovisor project](https://www.iovisor.org/) came up with a tool called `bpftrace` which can be used as an alternative to `strace` with more number of additional features. `bpftrace` uses `eBPF` for core tracing and provides user-space tools to harvest the tracing data. To understand more about `bpftrace` read this [article](https://github.com/iovisor/bpftrace/blob/master/docs/reference_guide.md). `bpftrace` is not restricted just to system calls tracing, we can also use it to trace Disk I/O operations, network operation, CPU utilization etc. Since `bpftrace` supports `eBPF` at it's core, we can use `BPF` scripts to write our own tracing tools easily. If you are interested, have a look at some of the [cool tracing tools](https://github.com/iovisor/bpftrace/tree/master/tools) built using BPF, all these scripts can be readily used with `bpftrace`. 

### Let's experiment!
