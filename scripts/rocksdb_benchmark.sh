#!/bin/bash

basedir=${1}
test=${2}
schemes=${3}
CUR_DIR=$(pwd)
QEMU_DIR="qemu-tcg-kvm"
RES_DIR="$test-data"
GRAPH_SCRIPT="draw_rocksdb_graph.py"

mkdir -p ${RES_DIR}
rm -f ${RES_DIR}/*
rm -f ${QEMU_DIR}/kernel_rr/test_data/*
echo "Cleaned data in ${QEMU_DIR}/kernel_rr/test_data ${RES_DIR}"

cd ${QEMU_DIR}/kernel_rr

if [ $test == "rocksdb" ];then
    bash all-test.sh ${test} ${basedir} 1 ${schemes}
else
     bash all-test-spdk.sh ${test} ${basedir} 1 ${schemes}
     GRAPH_SCRIPT="draw_spdk_rocksdb_graph.py"
fi

cd ${CUR_DIR}
mv ${QEMU_DIR}/kernel_rr/test_data/*.csv $RES_DIR/
echo "Results are under $RES_DIR/"
cd graph/; python3 ${GRAPH_SCRIPT}
