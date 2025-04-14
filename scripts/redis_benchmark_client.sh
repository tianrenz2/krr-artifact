#!/bin/bash
BASEDIR=${1}
SERVER_HOST_IP=${2}
REDIS_SERVER_IP=${3}
CUR_DIR=$(pwd)

CLIENT_DIR="scripts/redis_test/client"
rm -rf redis-data
mkdir redis-data
cd ${CLIENT_DIR}

# Run the benchmark the specified number of trials
for mode in native krr; do
    for workload in GET SET; do
        echo "Trying workload ${workload}"

        bash test_run.sh ${workload} $mode 1 $SERVER_HOST_IP $REDIS_SERVER_IP

        # Call the end_record API
        sleep 20
    done
done

mv redis_dpdk*.csv ${CUR_DIR}/redis-data/
cd ${CUR_DIR}/graph
python3 draw_redis_graph_cps.py
