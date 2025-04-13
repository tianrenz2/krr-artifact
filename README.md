# KRR: Efficient and Scalable Kernel Record Replay

KRR is a kernel record replay tool supporting multi-core, it can record the guest kernel execution in KVM(hardware-assist virtualization) and replay it exactly in TCG(full emulation).

## Pre-requirement

### Hardware
Generally KRR is suitable to x86_64 processors, but Intel processor is recommended.

### Environment
KRR's hypervisor is built upon Linux 5.17.5, Ubuntu 22.04 is recommended.

## Run Experiments

Hardware Requirements: Intel with at least 32 cores and 64GB memory, or refer c6420 on [Cloudlab](https://docs.cloudlab.us/hardware.html#(part._hardware)).

1. Clone the repo:
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

1. Run benchmark RocksDB:
```
make test_rocksdb schemes=baseline,kernel_rr,whole_system_rr
```
Note: the baseline is the mode without record, kernel_rr is KRR record and whole_system_rr is the VM-RR record. If whole_system_rr is enabled, then the whole test time will be extended a lot, as it's very slow on large number of vCPUs.

2. Run benchmark RocksDB SPDK benchmarks:
```
make test_rocksdb_spdk
```

## Play with KRR Record Replay
To use KRR for record and replay, please follow this [tutorial](tutorial/README.md).
