# KRR (Kernel RR)

KRR is record-replay tool targeting Linux kernel and it's implemented based on QEMU(7.0.0) & KVM (5.17.5) tool, compared with other record-replay tools, KRR supports recording with hardware-assisted virtualization (KVM) and multi-core.

## Hardware Requirement
KRR only supports Intel processor now.

Supported Disk Emulation:
| Disk Type | Description |
| ------------- | ------------- |
| IDE | Supported  |
| NVMe(not including multi namespace) | Supported  |
| Virtio  | TODO  |

Supported Networ Emulation:
| Network Type | Description |
| ------------- | ------------- |
| E1000 | Supported  |
| virtio-net | TODO  |
| vhost-net  | TODO  |


## Record

### Install KRR KVM
1. Download the KRR's KVM hypervisor source code linux:
```
git clone -b rr-para https://github.com/tianrenz2/kernel-rr-linux.git
```

2. Generate the .config file:
```
cp kernel_rr_config .config
```

3. Compile:
```
make -j16
make modules_install
make install
```

4. Reboot machine to use the KRR KVM.


### Compile KRR QEMU
1. First, go to kernel RR QEMU code:
```
cd qemu-tcg-kvm
mkdir build
cd build
../configure --target-list=x86_64-softmmu
make -j
```

3. Get the kernel you want to test, here is a prepared [Linux kernel image & vmlinux package](https://drive.google.com/file/d/1cO0qMsqkReSKdHDZ1XC8r3-lT-ixJqfW/view?usp=drive_link)(6.1.0), if you want to build on your own, here is a [guide](#make-your-own-recordable-kernel) to help compile your recordable guest kernel image.

4. Get the root disk image you want to boot, [here](https://github.com/google/syzkaller/blob/master/tools/create-image.sh) is a script from syzkaller that helps you create a simple rootfs image.

5. Launch the guest, for the guest below, it takes 2GB for the guest RAM, additionally, it also takes 4GB for the event trace as the recording needs, so make sure you have this much memory on your machine:
```
cd qemu-tcg-kvm/build
../build/qemu-system-x86_64 -smp 1 -kernel <your kernel image> -accel kvm -cpu host -no-hpet -m 2G -append  "root=/dev/sda rw init=/lib/systemd/systemd tsc=reliable console=ttyS0" -hda <your root disk image> -object memory-backend-file,size=4096M,share,mem-path=/dev/shm/ivshmem,id=hostmem -device ivshmem-plain,memdev=hostmem -nographic
```

6. After getting into the system, click `ctrl+A` and `C` to enter the QEMU monitor command, and enter:
```
rr_record test1
```
Note that "test1" is the name of your record, it could be other names.

This will output things below:
```
(qemu) rr_record test1
enabled in ivshmem
Paused VM, start taking snapshot
Snapshotted for test1
Snapshot taken, start recording...
Removing existing log files: kernel_rr.log
Reset dma sg buffer
Initial queue header enabled=1
```

7. Execute things you want to record;

8. To finish the record session, get into the QEMU monitor command again, and enter:
```
rr_end_record
```
This will have the output below that summarizes the record data, like the number of each type of events:
```
root@wintermute:~# (qemu) rr_end_record
disabled in ivshmem
event number = 0
current pos 10872, rotated_bytes 0, current_bytes 597999, total_bytes 597999
Getting result
Result buffer 0x0
=== Event Stats ===
Interrupt: 151
Syscall: 295
Exception: 163
CFU: 139
GFU: 411
IO Input: 753
RDTSC: 7587
RDSEED: 0
PTE: 1353
Inst Sync: 0
DMA Buf Size: 442368
Total Replay Events: 10872
Time(s): 3.81
synced queue header, current_pos=10872
writing queue header with 10872, pos=48
Start persisted event
[kernel_rr_dma-9.log] Logged entry number 20
[kernel_rr_dma-40.log] No dma entry generated
Total dma buf cnt 107 size 442368
[kernel_rr_network.log] No dma entry generated
network entry number 0, total net buf 0
```

9. After finishing the record session, you get the files below, which are necessary to get it replayed:
```
kernel_rr.log: stores the event trace.
kernel_rr_dma-<number>.log: stores the disk DMA data, <number> means the disk device id.
kernel_rr_network.log: stores the network data.
test1: initial snapshot file of your system, its name is the same as the record session name you give in step 6.
```

## Replay
Using KRR for replay doesn't need KVM's support since it's purely userspace (QEMU TCG), what you need is just an initial snapshot and event trace.

1. Replay prepare:
As an example, my replay snapshot is named as "test1".

First, make sure you have these 4 files under your `build` directory from last step:
- test1: the snapshot file storing VM's initial memory state;
- kernel_rr.log: main event trace;
- kernel_rr_dma-<number>.log: Disk DMA data.
- kernel_rr_network.log: Network device data.

You also need the original disk image file you used for record, it's not going to be actually read in replay, it's just for consistent hardware configuration between record and replay.


2. Generate kernel symbols:
```
cd qemu-tcg-kvm/kernel_rr
bash generate_symbol.sh <absolute path to your vmlinux> <absolute path of your KRR QEMU directory>
```
KRR replayer needs some kernel symbol information to trap certain kernel code.

After executing, it has the output below:
```
[root@tianren kernel_rr]# bash generate_symbol.sh /home/projects/linux-6.1.0/vmlinux /home/projects/qemu-tcg-kvm/
GNU gdb (GDB) Fedora 12.1-2.fc36
Copyright (C) 2022 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-redhat-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<https://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from /home/projects/linux-6.1.0/vmlinux...
{sysname = "Linux", '\000' <repeats 59 times>, nodename = "(none)", '\000' <repeats 58 times>, release = "6.1.0-rc7-ga9bf5136035e-dirty", '\000' <repeats 35 times>, version = "#787 SMP PREEMPT_DYNAMIC Sat Dec 28 04:23:24 EST 2024", '\000' <repeats 11 times>, machine = "x86_64", '\000' <repeats 58 times>, domainname = "(none)", '\000' <repeats 58 times>}
Symbol generation finished, please recompile the KRR QEMU
```

3. After generating the symbols, recompile the KRR QEMU:
```
cd qemu-tcg-kvm/build/
make -j
```

4. Replay:
Execute basic command:
```
../build/qemu-system-x86_64 -accel tcg -smp 1 -cpu Broadwell -no-hpet -m 2G -hda <disk image> -device ivshmem-plain,memdev=hostmem -object memory-backend-file,size=4096M,share,mem-path=/dev/shm/ivshmem,id=hostmem -kernel-replay test1 -singlestep -D rec.log -replay-log-bound start=0 -monitor stdio -vnc :0
```
And it will automatically start replaying.

In the command: `-kernel-replay` is the name of your snapshot file;

At the end, it displays something below as a summary of the replay:
```
Replay executed in 8.308527 seconds
=== Event Stats ===
Interrupt: 1207
Syscall: 2196
Exception: 392
CFU: 1103
GFU: 502
Random: 0
IO Input: 75672
RDTSC: 35249
Strnlen: 0
RDSEED: 0
PTE: 4349
Inst Sync: 0
DMA Buf Size: 0
Total Replay Events: 120681
Time(s): 0.00
```
**Remember, apart from the parameters specifically for replay, the other VM configuration should be exactly the same as record.**

### Use gdb to debug replay:
If you wanna debug it using gdb, you should firstly have the `vmlinux` of the same kernel used by the guest.

1. Simply add `-S -s` options into the QEMU replay commandline above, this will start a gdb-server insdie QEMU.
2. In another command line, execute 
```
gdb vmlinux
```
3. In gdb console, execute:
```
target remote :1234
```
This will connect to the gdb-server.

4. Then you can just use gdb commands just like debugging a regular program.

### Log out instructions
Using following parameter could log out instructions & associated registers from N1th to N2th instruction.
```
-replay-log-bound start=N1,end=N2
```
The log file is specified by `-D logfile`.


### Reverse Debugging
KRR's replay also supports reverse debugging using gdb, the mechanism is based on snapshotting(similar to QEMU's native record & replay). So to really enable the reverse debugging, you firstly need to be able to replay successfully the target execution, during the replay, periodic snapshots need to be taken, repay it with the following command:
```
../build/qemu-system-x86_64 -accel tcg -smp 1 -cpu Broadwell -no-hpet -m 2G -hda <disk image> -device ivshmem-plain,memdev=hostmem -object memory-backend-file,size=4096M,share,mem-path=/dev/shm/ivshmem,id=hostmem -kernel-replay test1 -singlestep -D rec.log -snapshot-period 100000
```
Note that at the end we added `-snapshot-period 100000` parameter, which means a snapshot is taken on every 100000 instructions. After the snapshots are taken, you have the "checkpoints" for the execution to travel back.

Then run the replay again with gdb console and remove the parameter `-snapshot-period 100000`, you can make use of the reverse debugging, for example, in gdb I hit the following breakpoint and want to reverse back by 1 instruction, execute reverse-stepi:
```
Breakpoint 2, do_syscall_64 (regs=0xffffc90000273f58, nr=1) at arch/x86/entry/common.c:75
75		rr_handle_syscall(regs);
(gdb) reverse-stepi
```

The replayer would have the following output indicating the latest snapshot is restored:
```
restoring snapshot 1
loading snapshot
... done.
Found node with id 1
[CPU-0]Restored snapshot, event number=110, CPU inst=100000
```
And continue to replay until one instruction before my last breakpoint:
```
(gdb) reverse-stepi
entry_SYSCALL_64 () at arch/x86/entry/entry_64.S:120
120		call	do_syscall_64		/* returns with IRQs disabled */
(gdb)
```

## Make your own recordable kernel
Due to its split-recorder design, KRR requires some modifications to the guest linux kernel. The full changes refers to this [repo](https://github.com/tianrenz2/linux-6.1.0/tree/smp-rr), but here is a single [patch file](kernel_rr/Support-for-KRR-guest-recorder-patch) that contains all the changes. To apply the changes, mv the file to your kernel source code directory and execute:
```
mv Support-for-KRR-guest-recorder-patch Support-for-KRR-guest-recorder.patch
git apply Support-for-KRR-guest-recorder-patch
```
Note that this patch file is based on Linux 6.1.0, different version of source code may encounter some conflicts to resolve.

To compile, we can refer to a sample [.config](kernel_rr/rr_guest_config) file, note that this config file is also based on linux 6.1.0, so depending on your own linux kernel version, it might be somehow different.


## Removed features for kernel RR

1. Since we replay in TCG now, temporarily disabled xsaves and xsavec (which are not supported in TCG) features in KVM for compatibility of TCG, so the guest would use xsaveopt;

2. Disabled kvmclock device in QEMU;

3. Disabled KVM pvclock, by removing KVM_FEATURE_CLOCKSOURCE and KVM_FEATURE_CLOCKSOURCE2 features exposed to guest in KVM, so that the KVM won't update the guest memory, this is for us to do memory verification;
