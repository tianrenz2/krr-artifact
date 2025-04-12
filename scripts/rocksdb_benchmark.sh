#!/bin/bash

basedir=${1}
test=${2}
QEMU_DIR="qemu-tcg-kvm"

cd ${QEMU_DIR}/kernel_rr

if [ $test == "rocksdb" ];then
    bash all-test.sh ${test} ${basedir} 1 
else
     bash all-test-spdk.sh ${test} ${basedir} 1 
fi

