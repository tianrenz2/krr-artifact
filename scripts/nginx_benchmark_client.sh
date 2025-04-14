#!/bin/bash
BASEDIR=${1}
SERVER_HOST_IP=${2}
REDIS_SERVER_IP=${3}
CUR_DIR=$(pwd)

CLIENT_DIR="scripts/nginx_test/client"
rm -rf nginx-data
mkdir nginx-data
cd ${CLIENT_DIR}
rm -f nginx-dpdk*.csv

# Run the benchmark the specified number of trials
for mode in native krr; do
    echo "Trying mode ${mode}"
    bash test_run_all.sh $mode 1 $SERVER_HOST_IP $REDIS_SERVER_IP
    sleep 5
done
echo "All benchmarks completed."

mv nginx-test*.csv ${CUR_DIR}/nginx-data/
cd ${CUR_DIR}/graph
python3 draw_nginx_dpdk.py
