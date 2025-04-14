#!/bin/bash

# Check if the test and mode parameters are provided
if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <test> <mode> <trials>"
    echo "Example: $0 set baseline 5"
    exit 1
fi

THREADS_LIST=(1 2 4 8 16 32 64)

# Define the Redis server address and port
REDIS_HOST="10.10.1.1"
REDIS_PORT="6379"
OUTPUT_FILE="redis_output.csv"

# Get the test and mode parameters from the command line arguments
TEST=$1
MODE=$2
TRIALS=$3

# Run the benchmark the specified number of trials
for (( i=1; i<=TRIALS; i++ )); do
    for THREADS in "${THREADS_LIST[@]}"; do
        while true; do
            redis-cli -h $REDIS_HOST -p $REDIS_PORT flushall
            echo "Running benchmark with $THREADS threads for test type: $TEST and mode: $MODE..."
            redis-benchmark -h $REDIS_HOST -p $REDIS_PORT -t $TEST -n 5000000 --threads $THREADS --csv > $OUTPUT_FILE

            # Check if the command was successful
            if [ $? -eq 0 ]; then
                echo "Benchmark completed successfully for $THREADS threads."

                # Call the parse script with threads and mode
                python3 parse.py $THREADS $MODE
                
                # Sleep for 1 second
                sleep 1
                break
            else
                echo "Benchmark failed for $THREADS threads."
                exit 1
            fi
        done
    done
    echo "Finished trial ${i}"
done

echo "All benchmarks completed."
