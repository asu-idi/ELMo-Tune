import re
import os
from utils.utils import log_update

def parse_db_bench_output(output):
    
    if re.match("Unable to load options file.*", output) is not None:
        return {
            "error": "Invalid options file"
        }

    # Regular expression to find and extract the number of Entries
    # Searches for the pattern "Entries:" followed by one or more digits
    entries_match = re.search(r"Entries:\s+(\d+)", output)
    # If a match is found, convert the captured digits to an integer
    entries = int(entries_match.group(1)) if entries_match else None

    # Regular expression to parse the output line
    # Captures various performance metrics and their units
    test_name = None

    if "readrandomwriterandom" in output:
        op_line = output.split("readrandomwriterandom")[1].split("\n")[0]
        test_name = "readrandomwriterandom"
        test_pattern = r"readrandomwriterandom\s+:\s+(\d+\.\d+)\s+micros/op\s+(\d+)\s+ops/sec\s+(\d+\.\d+)\s+seconds\s+(\d+)\s+operations;"
    elif "fillrandom" in output:
        op_line = output.split("fillrandom")[1].split("\n")[0]
        test_name = "fillrandom"
        test_pattern = r"fillrandom\s+:\s+(\d+\.\d+)\s+micros/op\s+(\d+)\s+ops/sec\s+(\d+\.\d+)\s+seconds\s+(\d+)\s+operations;\s+(\d+\.\d+)\s+(\w+/s)\nMicroseconds per write:\nCount:\s+(\d+)\s+Average:\s+(\d+\.\d+)\s+StdDev:\s+(\d+\.\d+)\nMin:\s+(\d+)\s+Median:\s+(\d+\.\d+)\s+Max:\s+(\d+)\nPercentiles:\s+P50:\s+(\d+\.\d+)\s+P75:\s+(\d+\.\d+)\s+P99:\s+(\d+\.\d+)\s+P99\.9:\s+(\d+\.\d+)\s+P99\.99:\s+(\d+\.\d+)\n-{50}"
    elif "readrandom" in output:
        op_line = output.split("readrandom")[1].split("\n")[0]
        test_name = "readrandom"
        test_pattern = r"readrandom\s+:\s+(\d+\.\d+)\s+micros/op\s+(\d+)\s+ops/sec\s+(\d+\.\d+)\s+seconds\s+(\d+)\s+operations;\s+(\d+\.\d+)\s+(\w+/s)\s+\((\d+)\s+of\s+(\d+)\s+found\)\n\nMicroseconds per read:\nCount:\s+(\d+)\s+Average:\s+(\d+\.\d+)\s+StdDev:\s+(\d+\.\d+)\nMin:\s+(\d+)\s+Median:\s+(\d+\.\d+)\s+Max:\s+(\d+)\nPercentiles:\s+P50:\s+(\d+\.\d+)\s+P75:\s+(\d+\.\d+)\s+P99:\s+(\d+\.\d+)\s+P99\.9:\s+(\d+\.\d+)\s+P99\.99:\s+(\d+\.\d+)\n-{50}"
    elif "mixgraph" in output:
        op_line = output.split("mixgraph     :")[1].split("\n")[0]
        test_name = "mixgraph"
        test_pattern = r"mixgraph\s+:\s+(\d+\.\d+)\s+micros/op\s+(\d+)\s+ops/sec\s+(\d+\.\d+)\s+seconds\s+(\d+)\s+operations;"
        # test_pattern = r"mixgraph\s+:\s+(\d+\.\d+)\s+micros/op\s+(\d+)\s+ops/sec\s+(\d+\.\d+)\s+seconds\s+(\d+)\s+operations;\s+\(\s+Gets:+(\d+)\s+Puts:+(\d+)\s+Seek:(\d+),\s+reads\s+(\d+)\s+in\s+(\d+)\s+found,\s+avg\s+size:\s+\d+\s+value,\s+-nan\s+scan\)\n\nMicroseconds per read:\nCount:\s+(\d+)\s+Average:\s+(\d+\.\d+)\s+StdDev:\s+(\d+\.\d+)\nMin:\s+(\d+)\s+Median:\s+(\d+\.\d+)\s+Max:\s+(\d+)\nPercentiles:\s+P50:\s+(\d+\.\d+)\s+P75:\s+(\d+\.\d+)\s+P99:\s+(\d+\.\d+)\s+P99\.9:\s+(\d+\.\d+)\s+P99\.99:\s+(\d+\.\d+)\n-{50}"
    elif "readwhilewriting" in output:
        op_line = output.split("readwhilewriting")[1].split("\n")[0]
        test_name = "readwhilewriting"
        test_pattern = r"readwhilewriting\s+:\s+(\d+\.\d+)\s+micros/op\s+(\d+)\s+ops/sec\s+(\d+\.\d+)\s+seconds\s+(\d+)\s+operations;"
    else:
        log_update(f"[PDB] Test name not found in output: {output}")
        op_line = "unknown test"
        test_name = "unknown"
        test_pattern = r"(\d+\.\d+)\s+micros/op\s+(\d+)\s+ops/sec\s+(\d+\.\d+)\s+seconds\s+(\d+)\s+operations;(\s+\(.*found:\d+\))?\nMicroseconds per (read|write):\nCount: (\d+) Average: (\d+\.\d+)  StdDev: (\d+\.\d+)\nMin: (\d+)  Median: (\d+\.\d+)  Max: (\d+)\nPercentiles: P50: (\d+\.\d+) P75: (\d+\.\d+) P99: (\d+\.\d+) P99.9: (\d+\.\d+) P99.99: (\d+\.\d+)"

    pattern_matches = re.findall(test_pattern, output)
    log_update(f"[PDB] Test name: {test_name}")
    log_update(f"[PDB] Matches: {pattern_matches}")
    log_update(f"[PDB] Output line: {op_line}")
    # Set all values to None if the pattern is not found
    micros_per_op = ops_per_sec = total_seconds = total_operations = data_speed = data_speed_unit = None

    # Extract the performance metrics if the pattern is found
    for pattern_match in pattern_matches:
        # Convert each captured group to the appropriate type (float or int)
        micros_per_op = float(pattern_match[0])
        ops_per_sec = int(pattern_match[1])
        total_seconds = float(pattern_match[2])
        total_operations = int(pattern_match[3])
         # Check for specific workloads to handle additional data
        if "readrandomwriterandom" in output:
            data_speed = ops_per_sec
            data_speed_unit = "ops/sec"
            reads_found = None
        elif "fillrandom" in output:
            data_speed = float(pattern_match[4])
            data_speed_unit = pattern_match[5]
            writes_data = {
                "count": int(pattern_match[6]),
                "average": float(pattern_match[7]),
                "std_dev": float(pattern_match[8]),
                "min": int(pattern_match[9]),
                "median": float(pattern_match[10]),
                "max": int(pattern_match[11]),
                "percentiles": {
                    "P50": float(pattern_match[12]),
                    "P75": float(pattern_match[13]),
                    "P99": float(pattern_match[14]),
                    "P99.9": float(pattern_match[15]),
                    "P99.99": float(pattern_match[16])
                }
            }
        elif "readrandom" in output:
            data_speed = float(pattern_match[4])
            data_speed_unit = pattern_match[5]
            reads_found = {
                "count": int(pattern_match[6]),
                "total": int(pattern_match[7])
            }
            reads_data = {
                "count": int(pattern_match[8]),
                "average": float(pattern_match[9]),
                "std_dev": float(pattern_match[10]),
                "min": int(pattern_match[11]),
                "median": float(pattern_match[12]),
                "max": int(pattern_match[13]),
                "percentiles": {
                    "P50": float(pattern_match[14]),
                    "P75": float(pattern_match[15]),
                    "P99": float(pattern_match[16]),
                    "P99.9": float(pattern_match[17]),
                    "P99.99": float(pattern_match[18])
                }
            }
        elif "readwhilewriting" in output:
            data_speed = float(pattern_match[4])
            data_speed_unit = pattern_match[5]
            # reads_found = {
            #     "count": int(pattern_match[6]),
            #     "total": int(pattern_match[7])
            # }
            # reads_data = {
            #     "count": int(pattern_match[8]),
            #     "average": float(pattern_match[9]),
            #     "std_dev": float(pattern_match[10]),
            #     "min": int(pattern_match[11]),
            #     "median": float(pattern_match[12]),
            #     "max": int(pattern_match[13]),
            #     "percentiles": {
            #         "P50": float(pattern_match[14]),
            #         "P75": float(pattern_match[15]),
            #         "P99": float(pattern_match[16]),
            #         "P99.9": float(pattern_match[17]),
            #         "P99.99": float(pattern_match[18])
            #     }
            # }
        elif "mixgraph" in output:
            data_speed = ops_per_sec
            data_speed_unit = "ops/sec"
        else:
            log_update(f"[PDB] Test name not found in output: {output}")
            data_speed = ops_per_sec
            data_speed_unit = "ops/sec"
   
        log_update(f"[PDB] Ops per sec: {ops_per_sec} Total seconds: {total_seconds} Total operations: {total_operations} Data speed: {data_speed} {data_speed_unit}")

    ops_per_sec_points = re.findall("and \((.*),.*\) ops\/second in \(.*,(.*)\)", output)

    # Store all extracted values in a dictionary
    parsed_data = {
        "entries": entries,
        "micros_per_op": micros_per_op,
        "ops_per_sec": ops_per_sec,
        "total_seconds": total_seconds,
        "total_operations": total_operations,
        "data_speed": data_speed,
        "data_speed_unit": data_speed_unit,
        "ops_per_second_graph": [
            [float(a[1]) for a in ops_per_sec_points],
            [float(a[0]) for a in ops_per_sec_points],
        ]
    }

    # Grab the latency and push into the output logs file
    latency = re.findall("Percentiles:.*", output)
    for i in latency:
        log_update("[PDB] " + i)

    # Return the dictionary with the parsed data
    return parsed_data
