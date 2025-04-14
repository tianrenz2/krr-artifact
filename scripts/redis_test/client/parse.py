import csv
import os
import sys

def get_output_filename(benchmark):
    return f"redis_dpdk-{benchmark}.csv"

def add_mode_column(file_path):
    # Read existing data
    existing_rows = []
    if os.path.exists(file_path):
        with open(file_path, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                # Add the new 'mode' column with default value 'baseline'
                row['mode'] = 'baseline'
                existing_rows.append(row)

    # Write updated data back to the CSV with the new column at the front
    with open(file_path, mode='w', newline='') as csv_file:
        fieldnames = ['mode', 'benchmark', 'threads', 'throughput', 'p99_latency', 'trial']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write all updated rows
        for row in existing_rows:
            writer.writerow(row)

    print(f"Added 'mode' column to {file_path} with value 'baseline'.")

def main(threads, mode):
    # Define the CSV file path based on the benchmark
    benchmark = None
    output_file_path = None

    # Read data from redis_output.csv
    with open('redis_output.csv', mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['test'] in ["SET", "GET"]:  # Change this based on your benchmark types
                benchmark = row['test']
                output_file_path = get_output_filename(benchmark)
                data = {
                    'mode': mode,
                    'benchmark': benchmark,
                    'threads': threads,
                    'throughput': row['rps'],
                    'p99_latency': row['p99_latency_ms'],
                    'trial': 1
                }
                break

    if benchmark is None:
        print("No matching benchmark found in the output.")
        return

    # Read existing data from the benchmark-specific output CSV
    existing_rows = []
    max_trial = 0  # Track max trial number for matching rows
    if os.path.exists(output_file_path):
        with open(output_file_path, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            existing_rows = list(reader)
            # Check for max trial for matching rows
            for row in existing_rows:
                if (row['mode'] == data['mode'] and
                    row['benchmark'] == data['benchmark'] and
                    row['threads'] == data['threads']):
                    max_trial = max(max_trial, int(row['trial']))

    # Set trial to max_trial + 1 for the new entry
    data['trial'] = max_trial + 1

    # Prepare the updated rows with the new mode column
    updated_rows = []
    for row in existing_rows:
        updated_rows.append({
            'mode': row['mode'],
            'benchmark': row['benchmark'],
            'threads': row['threads'],
            'throughput': row['throughput'],
            'p99_latency': row['p99_latency'],
            'trial': row['trial']
        })

    # Add the new entry
    updated_rows.append({
        'mode': data['mode'],
        'benchmark': data['benchmark'],
        'threads': data['threads'],
        'throughput': data['throughput'],
        'p99_latency': data['p99_latency'],
        'trial': data['trial']
    })

    # Write the updated data back to the CSV
    with open(output_file_path, mode='w', newline='') as csv_file:
        fieldnames = ['mode', 'benchmark', 'threads', 'throughput', 'p99_latency', 'trial']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write all updated rows
        for row in updated_rows:
            writer.writerow(row)

    print(f"Data has been written to {output_file_path} with trial number {data['trial']}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse.py <threads> <mode>")
        sys.exit(1)

    threads = sys.argv[1]
    mode = sys.argv[2]
    main(threads, mode)
