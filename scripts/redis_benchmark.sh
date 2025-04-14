#!/bin/bash

basedir=${1}
test=${2}
CUR_DIR=$(pwd)
QEMU_DIR="qemu-tcg-kvm"
RES_DIR="$test-data"
GRAPH_SCRIPT="draw_rocksdb_graph.py"

rm -f "${CUR_DIR}/test.sock"
python -c "import socket as s; sock = s.socket(s.AF_UNIX); sock.bind('"${CUR_DIR}"/test.sock')"

cd scripts/redis_test/server
python3 server.py --basedir ${CUR_DIR}
