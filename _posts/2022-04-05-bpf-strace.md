---
title: System-wide syscalls tracing and monitoring in Linux using bpftrace 
published: true
---
If you are from Computer Science background probably you might have heard of "system calls" (also referred as "syscalls" to keep it short), if you haven't then you can read [this](https://www.javatpoint.com/system-calls-in-operating-system) interesting beginner friendly article on system calls. In general, system calls are the glue between Operating System kernel and User applications. System Calls are required for everything, without system calls the user application cannot do anything, because user applications need kernel support for memory management activities, reading and writing from/to disk, display, network interface, audio devices etc. In general, the user application becomes virtually useless if it cannot make system calls. Let us write and compile a simple C program that reads a file from the disk and outputs it, once we compile the program, we will use `strace` to see how many system calls our program makes to get the job done. (I will be using [Ubuntu 21.04](https://ubuntu.com/blog/ubuntu-21-04-is-here) for all the experiments in this article).

So this is our C program, it is simple and straightforward, we are just opening the file called `text.txt` (assume that it is present) using `fopen()`, reading the first line using `fscanf` and printing it to the terminal using `printf`.

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
We should be able to run the binary `read_file`, now let's trace what all system calls this program made. We will use [strace](https://man7.org/linux/man-pages/man1/strace.1.html) to count the number of system calls made by this program when executed. Let's run:
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
As expected, we have have `openat`, `read` and `write` system calls present in the table, but why are there so many other system calls? And also, `openat` is called thrice but we are opening the file only once - Well, these are expected, because C compiler is going to add some wrapper functions and bootstrap code, some of the core libraries are also dynamically opened and loaded, thus we have lot of other system calls which are unknown to us.

### strace
`strace` (as we saw in the above section) provides lot of other capabilities as well, for example we can also attach it to a PID and trace all the system calls made by that process (We can use `strace -p <PID>`). We can also configure `strace` to suite many use-cases by using one or more options provided by it, just run `strace -h` to list available options. But we have a problem with `strace` - i.e the overhead of tracing. To understand the problems of `strace` we need to look at `ptrace` - the underlying system call used by `strace`.

#### About ptrace() system call:
`strace` and most of the tracing tools like [GDB](https://cs.baylor.edu/~donahoo/tools/gdb/tutorial.html) make use of `ptrace` system call provided by Linux Kernel. Any program can use `ptrace` system call with various options to get itself attached to another process and set breakpoints to examine the internal state of that process. In our case, `strace` starts as the parent process and calls `ptrace` initially passing `PTRACE_ATTACH` and the PID of the child process that needs to be traced - in our case it is `read_file` built from `read_file.c`, the kernel then makes some checks and privilege verifications before allowing `strace` to get attached to the child process, if passed the kernel initializes some internal data structures required for tracing and notifications. Next, `strace` calls `ptrace` again, but this time it passes `PTRACE_SYSCALL` flag, which makes the kernel to write `TIF_SYSCALL_TRACE` flag into the child processes's internal thread state, which is like an indication that tracing is enabled for that process. After this, the child process is allowed to execute and `strace` waits for the child to make system calls. If child makes any system call, the `TIF_SYSCALL_TRACE` will be seen by the kernel's system call entry level function, which will force the child process to trap (halt) by sending `SIGTRAP` signal. Now that the child process is halted, kernel collects and passes the architecture specific and architecture independent state data of the halted child process to the parent, i.e to our `strace` process. `strace` can now parse this information and use it to display the tracing information. After this, child process is allowed to execute the system call, once system call is complete, another trap is generated by passing `SIGTERM` to the child and parent is notified about the completion of system call again by passing all the architecture specific and architecture independent state data, then the child process is allowed to continue. This cycle repeats for all the system calls made by the child process. So the tracer i.e the parent (`strace`) is notified twice per system call - one at system call entry and another one at exit. 

 Now that we know about `ptrace` system call and the tool `strace` built on top of it, we can look at the disadvantages of this approach:
1. `ptrace` cannot be used for system wide tracing - this is because we need to attach tracing to all the available processes on the system which is not recommended. In general `ptrace` is process specific.
2. This method involves lot of interactions between kernel and user-space because `ptrace` passes the entire information to the tracer tool via a signal, this information can be huge and it needs to be copied into a buffer in the user-space.
3. Child process needs to be interrupted upon system call - `ptrace` sets `TIF_SYSCALL_TRACE` in the thread state information of the child process which makes the kernel to pause the process's execution upon entry and exit of the system call, this can be a bottleneck for a process that heavily depends on system calls. (Example: Disk or Network intensive applications)

All these drawbacks doesn't mean `ptrace` is bad, tools written using `ptrace` can be used for low level debugging and tracing, but these tools are not suitable for continuous system-wide tracing.

### eBPF and bpftrace
Recently, starting from Linux kernel 4.x, the community introduced a new functionality called [Extended Berkeley Packet Filters (eBPF)](https://ebpf.io/), eBPF is a small sandboxed virtual machine that executes BPF byte-code (BPF is a simple filtering and data crunching language, before eBPF, BPF was used to filter and analyze network traffic by directly attaching it to data-link layer, read more about BPF [here](https://en.wikipedia.org/wiki/Berkeley_Packet_Filter).) completely in the kernel space, eBPF scripts can be attached to many event triggers within the kernel (like interrupts, system calls, breakpoints, function calls etc), kernel maintains the mapping of these event triggers and attached eBPF scripts, then it automatically executes these scripts whenever any of such events occur. This is a very powerful kernel feature, because it allows developers to extend the functionality of the kernel in a event driven way without writing and loading complex [kernel modules](https://linux-kernel-labs.github.io/refs/heads/master/labs/kernel_modules.html). It is also possible to dynamically attach/remove these scripts and receive the outputs back in the user-space. Let's see how this can be helpful for monitoring and tracing:
1. Completely Event Driven: We don't have to anymore stop the execution of the child process (like we did when using `ptrace`), these eBPF scripts are executed automatically when the event occurs.
2. Data Crunching in the kernel: If our analysis involves lots of data, we can filter and aggregate them in the kernel itself without transferring it to the user-space - this is because eBPF VM runs in kernel space.
3. Can monitor system-wide events: eBPF is not restricted to one process or thread, it is system-wide because it runs in the kernel. 

This solves some of the issues we had with `ptrace` based implementations. Recently [iovisor project](https://www.iovisor.org/) came up with a tool called `bpftrace` which can be used as an alternative to `strace` with more number of additional features. `bpftrace` uses `eBPF` for core tracing and provides user-space tools to harvest the tracing data. To understand more about `bpftrace` read this [reference guide](https://github.com/iovisor/bpftrace/blob/master/docs/reference_guide.md). `bpftrace` is not restricted just to system calls tracing, we can also use it to trace Disk I/O operations, network operations, CPU utilization etc. Since `bpftrace` supports `eBPF` at it's core, we can use `BPF` scripts to write our own tracing scripts easily. If you are interested, have a look at some of the [cool tracing scripts](https://github.com/iovisor/bpftrace/tree/master/tools) built using BPF, all these scripts can be readily used with `bpftrace`. 

### Let's experiment!
To try out `bpftrace`, make sure you are using the latest kernel, this is the kernel I am using right now (`uname -r`) on my Ubuntu 21.04 Linux machine.
```
5.11.0-49-generic
```
You can get the latest binary of `bpftrace` from their [GitHub releases](https://github.com/iovisor/bpftrace/releases) page. Once downloaded, check the version. This is the version I am using (just run `./bpftrace --version`)
```
bpftrace v0.14.1
```
Now, let's run a simple BPF script with `bpftrace` that emits the count of system calls made by each process running on the system every 5 seconds. We need the output in JSON format so other applications can consume it, we can tell `bpftrace` to emit JSON output by passing `-f json` flag. Note that `bpftrace` needs to be executed as `sudo`. Here is the command we will execute: 
```
sudo ./bin/bpftrace -f json -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); } interval:s:5 { print(@); clear(@); }'
```
This script should make `bpftrace` emit the system call count of all the processes every 5 seconds. Here is the output:
```
{"type": "attached_probes", "data": {"probes": 2}}
{"type": "map", "data": {"@": {"dockerd": 1, "packagekitd": 1, "epmd": 1, "ibus-engine-sim": 2, "gosecrets": 2, "terminator thre": 2, "ibus-extension-": 2, "pipewire-media-": 3, "GUsbEventThread": 3, "rtkit-daemon": 4, "gvfs-afc-volume": 5, "runsvdir": 6, "Chrome_ChildIOT": 6, "Netlink Monitor": 6, "uml_switch": 6, "docker": 7, "gsd-sharing": 8, "thermald": 8, "MemoryPoller": 9, "containerd": 9, "mc:worker_00": 10, "mc:worker_02": 10, "sh": 10, "Cache2 I/O": 10, "apache2": 15, "dbus-daemon": 16, "ibus-daemon": 17, "mc:worker_03": 18, "avahi-daemon": 20, "systemd": 21, "ThreadPoolForeg": 24, "civetweb-master": 25, "memsup": 30, "memcached": 30, "JS Watchdog": 32, "Socket Thread": 34, "ThreadPoolServi": 35, "NetworkManager": 37, "systemd-resolve": 39, "DOM Worker": 40, "gmain": 44, "pulseaudio": 47, "TaskCon~ller #0": 49, "0_poller": 50, "TaskCon~ller #3": 51, "IPDL Background": 62, "inet_gethost": 65, "threaded-ml": 66, "gnome-terminal-": 75, "goport": 82, "GeckoMain": 84, "TaskCon~ller #2": 93, "4_scheduler": 96, "mc:worker_01": 99, "8_dirty_io_sche": 103, "LS Thread": 132, "gdbus": 146, "JS Helper": 148, "IPC I/O Parent": 151, "IPC I/O Child": 155, "dnsmasq": 170, "df": 202, "bpftrace": 207, "aux": 228, "4_dirty_cpu_sch": 313, "code": 325, "2_dirty_io_sche": 413, "Timer": 422, "gnome-shell": 427, "TaskCon~ller #1": 466, "goxdcr": 661, "3_scheduler": 792, "2_scheduler": 956, "NonIoPool0": 1057, "NonIoPool1": 1063, "godu": 1116, "Isolated Web Co": 1119, "prometheus": 1266, "cbq-engine": 1306, "1_scheduler": 1674, "projector": 2138, "SchedulerPool0": 2278, "alsa-sink-ALC89": 3142, "3_dirty_io_sche": 3208, "indexer": 20237}}}
{"type": "map", "data": {"@": {"wpa_supplicant": 1, "snap-store": 1, "epmd": 1, "CacheThread_Blo": 1, "mc:executor": 2, "ibus-engine-sim": 2, "ibus-extension-": 2, "saslauthd-port": 2, "GUsbEventThread": 2, "thermald": 4, "Compositor": 4, "pool-/usr/libex": 4, "GpuWatchdog": 5, "gvfs-afc-volume": 5, "runsvdir": 6, "Chrome_ChildIOT": 6, "docker": 8, "dockerd": 8, "ibus-daemon": 9, "MemoryPoller": 9, "uml_switch": 9, "jemalloc_bg_thd": 10, "mc:worker_00": 10, "containerd": 14, "apache2": 15, "mc:worker_03": 16, "MediaTrackGrph": 17, "civetweb-worker": 24, "inet_gethost": 26, "JS Watchdog": 30, "memcached": 31, "mc:worker_02": 40, "irqbalance": 40, "civetweb-master": 40, "gmain": 40, "0_poller": 45, "pulseaudio": 64, "systemd-resolve": 69, "GeckoMain": 69, "gnome-terminal-": 73, "gdbus": 74, "TaskCon~ller #1": 83, "threaded-ml": 88, "IPDL Background": 89, "mc:worker_01": 100, "6_dirty_io_sche": 103, "TaskCon~ller #3": 122, "aux": 138, "sigar_port": 148, "bpftrace": 193, "4_dirty_cpu_sch": 210, "IPC I/O Child": 213, "IPC I/O Parent": 215, "TaskCon~ller #2": 222, "goport": 250, "TaskCon~ller #0": 275, "4_scheduler": 313, "gnome-shell": 362, "code": 500, "Timer": 530, "goxdcr": 692, "8_dirty_io_sche": 716, "3_scheduler": 797, "2_dirty_io_sche": 875, "2_scheduler": 956, "NonIoPool0": 1031, "NonIoPool1": 1056, "prometheus": 1144, "3_dirty_io_sche": 1307, "cbq-engine": 1328, "1_scheduler": 1787, "projector": 2034, "Isolated Web Co": 2052, "godu": 2228, "SchedulerPool0": 2293, "alsa-sink-ALC89": 3144, "indexer": 19889}}}
```
We ran `bpftrace` for 10 seconds and thus we have two output logs in JSON format (at first we receive attach event).

#### Let's build a simple dashboard in python to display the live data
Now that we are receiving the system call counts every 5 seconds, let's use it to build a live dashboard. There are hundreds of tools and libraries available for building dashboards these days, I decided to go with [streamlit](https://streamlit.io/) - this python framework will allow us to spin up a dashboard with less code (I wanted to keep it as simple as possible). To get started with `streamlit`, make sure you have [python 3.0+](https://www.python.org/downloads/) (usually this will be installed by default on many Linux distributions). We will install `streamlit` using [pip](https://pypi.org/project/pip/).
```
pip install streamlit==1.8.1
```  
We will create a subprocess that runs `bpftrace` and collects the streamed content on `stdout` line by line, we can use `yield` for this task. We iterate over the outputs as and when they are emitted and update our `streamlit` table view. Here is the python code which does that, name it `dashboard.py`:

```python
import subprocess
import os
import shlex
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

SCRIPT = "tracepoint:raw_syscalls:sys_enter { @[comm] = count(); } interval:s:5 { print(@); clear(@); }"

def exec(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def execute_and_listen_for_updates():

    st.title("Real-time syscalls counter")
    table_placeholder = st.empty()
    total_placeholder = st.empty()

    try:
        command = shlex.split("./bin/bpftrace -f json -e '{}'".format(SCRIPT))
        for entry in exec(command):
            entry = json.loads(entry)
            if entry["type"] == "map":
                data_dict = entry["data"]["@"]
                proc_names, counts = [], []
                total = 0
                for k, v in data_dict.items():
                    proc_names.append(k)
                    counts.append(v) 
                    total += v

                df = pd.DataFrame(
                    {"counts": counts},
                    index=proc_names
                )

                table_placeholder.table(df)
                total_placeholder.text("total system calls: " + str(total))
                
    except Exception as e:
        print('internal error:', e)
        os._exit(0)


if __name__ == "__main__":
    execute_and_listen_for_updates()
```  
Thanks to streamlit because we could create a dashboard in less than 55 lines of code. Now let's run the streamlit app:
```
sudo streamlit run dashboard.py
```
This should spin up the webserver on port `8501` by default
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.0.106:8501
```
We can open the dashboard at `http://localhost:8501` or `http://<your-lan-device-ip>:8501` to see the live system call table which updates every 5 seconds. Here is a screenshot of the dashboard from my computer:
<div style="text-align: center">
    <img src="./assets/syscall-dashboard/dashboard.png" alt="drawing"/>
</div>

If you are interested to explore more, you can explore many other streamlit charts. The code I wrote above is not so optimal and many things can be improved, I just wrote that to demonstrate how `bpftrace` can be integrated with other applications. There is a tool called [pixie](https://newrelic.com/platform/kubernetes-pixie) which provides observability for kubernetes clusters using `eBPF` underneath, if you are interested you can also have a look at it as well.