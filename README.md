# KRR: Efficient and Scalable Kernel Record Replay

This is a central repo for kernel-rr project, the code is distributed in 3 parts (QEMU, KVM and guest linux). The are present as submodules in this repo.

## Pre-requirement

### Hardware
Generally KRR is suitable to x86_64 processors, but Intel processor is recommended.

### Environment
KRR's hypervisor is built upon Linux 5.17.5, Ubuntu 22.04 is recommended.

## KRR Tutorial
To use KRR for record and replay, please follow this [tutorial](https://github.com/rssys/qemu-tcg-kvm?tab=readme-ov-file#krr-kernel-rr).

## Run Experiments

Hardware Requirements: Intel with at least 32 cores, or refer c6420 on [Cloudlab](https://docs.cloudlab.us/hardware.html#(part._hardware)).

1. Clone the repo:
```
git clone https://github.com/rssys/kernelonly-rr-dev.git
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
make test_rocksdb
```

1. Run benchmark RocksDB SPDK benchmarks:
```
make test_rocksdb_spdk
```
