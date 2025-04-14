import csv
import re
import os
import sys

def parse_wrk_output(wrk_output):
    req_per_sec = None
    requests_sec = None
    avg_latency = None
    p99_latency = None

    for line in wrk_output.splitlines():
        if "Req/Sec" in line:
            req_per_sec = float(re.search(r"([\d\.]+)k", line).group(1)) * 1000  # Convert from k
        elif "Requests/sec" in line:
            requests_sec = float(re.search(r"([\d\.]+)", line).group(1))
        elif "Latency" in line:
            # Check for both us and ms
            match = re.search(r"Latency\s+([\d\.]+)(us|ms)", line)
            if match:
                latency_value = float(match.group(1))
                latency_unit = match.group(2)
                if latency_unit == 'us':
                    avg_latency = latency_value  # Already in microseconds
                elif latency_unit == 'ms':
                    avg_latency = latency_value * 1000  # Convert to microseconds
        elif "99%" in line:
            match = re.search(r"99%\s+([\d\.]+)(ms|us)", line)
            if match:
                p99_value = float(match.group(1))
                p99_unit = match.group(2)
                if p99_unit == 'ms':
                    p99_latency = p99_value * 1000  # Convert to microseconds
                elif p99_unit == 'us':
                    p99_latency = p99_value

    return req_per_sec, requests_sec, avg_latency, p99_latency

def append_to_csv(mode, cores, req_per_sec, requests_sec, avg_latency, p99_latency, csv_file):
    data = {
        'mode': mode,
        'cores': cores,
        'req/sec': requests_sec,
        'thread_req/sec': req_per_sec,
        'thread_avg_latency': avg_latency,
        'thread_p99_latency': p99_latency,
        'trial': 1
    }
    rows = []

    # Check if the CSV file exists and read existing data
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        # Check for existing mode and cores
        max_trial = 0
        for row in rows:
            if row['mode'] == mode and row['cores'] == str(cores):
                max_trial = max(max_trial, int(row['trial']))  # Find maximum trial
        if max_trial > 0:
            data['trial'] = max_trial + 1  # Increment trial based on maximum found

    # Append new row to the CSV file
    with open(csv_file, mode='a', newline='') as file:
        fieldnames = ['mode', 'cores', 'req/sec', 'thread_req/sec', 'thread_avg_latency', 'thread_p99_latency', 'trial']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header if file is new
        if not rows:
            writer.writeheader()

        writer.writerow(data)

def main(wrk_output_file, mode, cores, csv_file):
    # Read wrk output from the file
    with open(wrk_output_file, 'r') as file:
        wrk_output = file.read()

    req_per_sec, requests_sec, avg_latency, p99_latency = parse_wrk_output(wrk_output)
    append_to_csv(mode, cores, req_per_sec, requests_sec, avg_latency, p99_latency, csv_file)
    print(f"Data appended to {csv_file} for mode: {mode}, cores: {cores}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <wrk_output_file> <mode> <cores> <csv_file>")
        sys.exit(1)

    wrk_output_file = sys.argv[1]
    mode = sys.argv[2]
    cores = sys.argv[3]
    csv_file = sys.argv[4]

    main(wrk_output_file, mode, cores, csv_file)
