# KRR: Efficient and Scalable Kernel Record Replay

KRR is a kernel record replay tool supporting multi-core, it can record the guest kernel execution in KVM(hardware-assist virtualization) and replay it exactly in TCG(full emulation).


## Getting Started
To use KRR for record and replay, please follow this [tutorial](tutorial/README.md).


## Run Experiments

### Hardware Requirements
Intel with at least 32 cores and 64GB memory, we recommend `c6420` on [Cloudlab](https://docs.cloudlab.us/hardware.html#(part._hardware)) which is used in the experiments.

### Guest Kernel
We use our pre-built kernel image for both native and KRR's kernel, the native is based on this [source code version](https://github.com/tianrenz2/linux-6.1.0/tree/native) which is an unmodified 6.1.0 version except some extra modules used by DPDK. [Here](https://github.com/tianrenz2/linux-6.1.0/tree/smp-rr) is the KRR's kernel source code version.

### Environment
KRR's hypervisor is built upon Linux 5.17.5, and Ubuntu 22.04 is assumed to be used.

1. Clone the repo, since this will download some large files, make sure it's executed on a disk with more than 100G space (we used the `sdb` on the recommended machine):
```
git clone https://github.com/tianrenz2/krr-artifact.git
```

1. Go to the project directory, prepare environment and tools:
```
make build
```

If all goes well, you should see the message:
```
Setup finished, please reboot your machine to launch KRR kernel
```
Then reboot the machine to launch the KRR host kernel, its version should be `5.17.5+`

### Run RocksDB benchmarks 
1. Run benchmark RocksDB [estimated time 3 ~ 3.5h]:
```
make run/rocksdb schemes=baseline,kernel_rr,whole_system_rr
```
Note: the baseline is the mode without record, kernel_rr is KRR record and whole_system_rr is the VM-RR record. If whole_system_rr is enabled, then the whole test time will be much longer(to ~3.5 hr).

After test is succesfully finished, the graph is generated as `graph/rocksdb-throughput.pdf`.

2. Run benchmark RocksDB SPDK benchmarks [estimated time 1.5 ~ 2h]:
```
make run/rocksdb_spdk
```
After test is succesfully finished, the graph is generated as `graph/spdk-study.pdf`.

### Run DPDK benchmarks
#### Hardware Requirement:
Two machines are used, server and client, recommend to set up two `c6420` machines.

#### Setup
Two servers are connected via a 1Gbps control link (Dell D3048 switches) and a 10Gbps experimental link (Dell S5048 switches). The server machine runs the testing vm with the dpdk app server and client machine runs the client. On the server machine, the 10Gbps NIC is passthrough to the VM, and it's ip is configured as `10.10.1.1`(hardcoded in the VM disk image yet), this is also the default ip when configuring with the [recommended machines](#hardware-requirement).

On server machine, Create the vfio device for the passthrough NIC:

List the interfaces, choose the interface for passthrough, it needs to be the one that connects the client machine:
```
lspci -nn | grep -i ethernet
18:00.0 Ethernet controller [0200]: Intel Corporation Ethernet Controller X710 for 10GbE SFP+ [8086:1572] (rev 02)
18:00.1 Ethernet controller [0200]: Intel Corporation Ethernet Controller X710 for 10GbE SFP+ [8086:1572] (rev 02)
lo:
```
For example, if choose `18:00.1`, then execute following:
```
echo "0000:18:00.1" > /sys/bus/pci/devices/0000\:18\:00.1/driver/unbind
modprobe vfio-pci
echo "8086 1572" > /sys/bus/pci/drivers/vfio-pci/new_id
```

#### Prepare server
If you already executed `make build` on the server host, then skip this step.

#### Prepare client environment
On the client machine, clone this repo and execute:
```
make build/client
```

#### Redis benchmark  [estimated time 0.5 ~ 1h]
On server machine, run the server:
```
make run/redis_server
```

On client machine, execute:
```
make run/redis_client host_ip=<the server host ip> vm_ip=10.10.1.1
```

After test is succesfully finished, the raw data is under `redis-data/` and graph is `garph/redis_dpdk_performance.pdf` on the client machine.

#### Nginx benchmark [estimated time 0.5 ~ 1h]
On server machine, run the server:
```
make run/nginx_server
```

On client machine, execute:
```
make run/nginx_client host_ip=<the server host ip> vm_ip=10.10.1.1
```

After test is succesfully finished, the raw data is under `nginx-data/` and graph is `garph/nginx-dpdk-<file size>.pdf` on the client machine.
