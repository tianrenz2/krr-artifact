#!/bin/bash

# Check if the test and mode parameters are provided
if [[ $# -ne 6 ]]; then
    echo "Usage: $0 <test> <mode> <trials> <count>"
    echo "Example: $0 set baseline 5"
    exit 1
fi

#THREADS_LIST=(32)

# Define the Redis server address and port
REDIS_PORT="6379"
OUTPUT_DIR="output"

# Get the test and mode parameters from the command line arguments
TEST=$1
MODE=$2
CORES=$3
SIZE=$4
HOST_IP=$5
VM_IP=$6

DURATION=10
CONN=1024
THREADS=32

launch_vm() {
    json_payload=$(jq -n --arg cn "$CORES" --arg m "$MODE" --arg w "$TEST-$CORES-$SIZE" '{core_number: $cn, mode: $m, workload: $w}')

    # Call the API with POST request to launch the VM
    response=$(curl --http0.9 -s -X POST "http://$HOST_IP:8080/launch_vm" -H "Content-Type: application/json" -d "$json_payload")

    # Print the response for the launch_vm API call
    echo "Response for mode: $MODE, cores: $CORES -> $response"
    sleep 1
}

launch_vm

timer=0
while true; do
    if curl -s -o /dev/null -w "%{http_code}" http://$VM_IP/index.html | grep -q "200"; then
        echo "Server responded with 200"
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

wrk_output_file="wrkoutput-$MODE-$CORES-$SIZE.txt"
rm -f ${wrk_output_file}
wrk -t${THREADS} -c${CONN} -d${DURATION}s --latency http://${VM_IP}/${SIZE}.html > "$wrk_output_file"
echo "wrk output saved to $wrk_output_file"

end_record_response=$(curl --http0.9 -s -X POST "http://$HOST_IP:8080/end_record")
echo "Response for end_record API call -> $end_record_response"

python3 parse.py ${wrk_output_file} ${MODE} ${CORES} nginx-test-${SIZE}.csv
