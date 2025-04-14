#!/bin/bash

SIZES=("1k" "4k" "16k" "64k")

# Get the test and mode parameters from the command line arguments
MODE=$1
TRIALS=$2
HOST_IP=$3
VM_IP=$4
# Run the benchmark the specified number of trials
for size in "${SIZES[@]}"; do
    for core in 1 2 4 8 16 32; do
        echo "Trying workload cores=${core} size=${size}"

        for (( i=1; i<=TRIALS; i++ )); do
            bash test_run.sh nginx $MODE $core $size $HOST_IP $VM_IP
            sleep 20
        done
    done
done
