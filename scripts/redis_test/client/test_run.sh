#!/bin/bash

# Check if the test and mode parameters are provided
if [[ $# -ne 5 ]]; then
    echo "Usage: $0 <test> <mode> <trials> <host ip> <vm ip>"
    echo "Example: $0 set baseline 1 0.0.0.0 1.1.1.1"
    exit 1
fi

# Define the Redis server address and port
REDIS_PORT="6379"
OUTPUT_DIR="output"

# Get the test and mode parameters from the command line arguments
TEST=$1
MODE=$2
TRIALS=$3
HOST_IP=$4
REDIS_HOST=$5

launch_vm() {
    json_payload=$(jq -n --arg cn "4" --arg m "$MODE" --arg w "workload${workload}" '{core_number: $cn, mode: $m, workload: $w}')

    # Call the API with POST request to launch the VM
    response=$(curl --http0.9 -s -X POST "http://$HOST_IP:8080/launch_vm" -H "Content-Type: application/json" -d "$json_payload")

    # Print the response for the launch_vm API call
    echo "Response for mode: $mode, cores: $core -> $response"
}

launch_vm

timer=0
while true; do
    if redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} ping | grep -q "PONG"; then
        echo "Server responded with PONG"
        break
    else
        ((timer++))
        if [ $timer -ge 60 ]; then
            launch_vm
            timer=0
        fi
        echo "Waiting for server response..."
        sleep 1
    fi
done

sleep 5

# start_record_response=$(curl --http0.9 -s -X POST "http://$IP:8080/start_record")
# echo "Response for start_record API call -> $start_record_response"

# if [ $? -eq 0 ]; then
#   echo "Load succeeded."
# else
#   exit 1
# fi

while true; do
    in_record_response=$(curl --http0.9 -s -X GET "http://$HOST_IP:8080/in_record")
    exists=$(echo "$in_record_response" | jq -r '.exists')

    if [ "$exists" == "true" ]; then
        echo "Recording exists. Proceeding the test."
        break
    else
        echo "Recording not yet started. Checking again in 1 second..."
        sleep 1
    fi
done

bash test.sh $TEST $MODE $TRIALS

end_record_response=$(curl --http0.9 -s -X POST "http://$HOST_IP:8080/end_record")
echo "Response for end_record API call -> $end_record_response"

echo "$TEST benchmarks completed."
sleep 5
