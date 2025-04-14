#!/bin/bash

basedir=${1}
test=${2}
CUR_DIR=$(pwd)
QEMU_DIR="qemu-tcg-kvm"

rm -f "${CUR_DIR}/test.sock"
python -c "import socket as s; sock = s.socket(s.AF_UNIX); sock.bind('"${CUR_DIR}"/test.sock')"

cd scripts/nginx_test/server
python3 server.py --basedir ${CUR_DIR}
