import subprocess
import os
import time 

from cgroup_monitor import CGroupMonitor

from utils.utils import log_update, path_of_db
from utils.constants import TEST_NAME, DB_BENCH_PATH, OPTIONS_FILE_DIR, NUM_ENTRIES, SIDE_CHECKER, FIO_RESULT_PATH
from rocksdb.parse_db_bench_output import parse_db_bench_output
from utils.utils import store_db_bench_output
from utils.graph import plot_2axis
from gpt.prompts_generator import midway_options_file_generation
from utils.system_operations.fio_runner import get_fio_result
from utils.system_operations.get_sys_info import system_info


def pre_tasks(database_path, run_count):
    '''
    Function to perform the pre-tasks before running the db_bench
    Parameters:
    - database_path (str): The path to the database
    - run_count (str): The current iteration of the benchmark

    Returns:
    - None
    '''

    # Try to delete the database if path exists 
    proc = subprocess.run(
        f'rm -rf {database_path}',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        check=False
    )

    log_update("[SPM] Flushing the cache")
    print("[SPM] Flushing the cache")
    # Delay for all the current memory to be freed
    proc = subprocess.run(
        f'sync; echo 3 > /proc/sys/vm/drop_caches',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        check=False
    )

    # update_log_file("[SPM] Waiting for 90 seconds to free up memory, IO and other resources")
    print("[SPM] Waiting for 30 seconds to free up memory, IO and other resources")
    # Give a 1.5 min delay for all the current memory/IO/etc to be freed
    time.sleep(30)


def generate_db_bench_command(db_bench_path, database_path, options, run_count, test_name):
    '''
    Generate the DB bench command

    Parameters:
    - db_bench_path (str): The path to the db_bench executable
    - database_path (str): The path to the database
    - option_file (dict): The options file to be used
    - run_count (str): The current iteration of the benchmark
    - test_name (str): The name of the test

    Returns:
    - list: The db_bench command
    '''

    db_bench_command = [
        db_bench_path,
        f"--db={database_path}",
        f"--options_file={OPTIONS_FILE_DIR}",
        "--use_direct_io_for_flush_and_compaction",
        "--use_direct_reads", "--compression_type=none",
        "--stats_interval_seconds=1", "--histogram", 
        f"--num={NUM_ENTRIES}", "--duration=1000"
    ]


    if test_name == "fillrandom":
        db_bench_command.append("--benchmarks=fillrandom")
    elif test_name == "readrandomwriterandom":
        db_bench_command.append("--benchmarks=readrandomwriterandom")
    elif test_name == "readrandom":
        tmp_runner = db_bench_command[:-2] + ["--num=25000000", "--benchmarks=fillrandom"]
        tmp_proc = subprocess.run(tmp_runner, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        new_db_bench = db_bench_command[:-2] + ["--benchmarks=readrandom", "--use_existing_db", "--num=25000000", "--duration=1000"]
        db_bench_command = new_db_bench
    elif test_name == "mixgraph":
        tmp_runner = db_bench_command[:-2] + ["--num=25000000", "--benchmarks=fillrandom"]
        tmp_proc = subprocess.run(tmp_runner, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        new_db_bench = db_bench_command[:-1] + ["--benchmarks=mixgraph", "--use_existing_db", "--duration=1000", "--mix_get_ratio=0.5", "--mix_put_ratio=0.5", "--mix_seek_ratio=0.0", "--mix_get_ratio=0.5"]
        db_bench_command = new_db_bench
    elif test_name == "readwhilewriting":
        db_bench_command.append("--benchmarks=readwhilewriting")
    else:
        print(f"[SPM] Test name {test_name} not recognized")
        exit(1)

    log_update(f"[SPM] Command: {db_bench_command}")
    return db_bench_command


def db_bench(db_bench_path, database_path, options, run_count, test_name, previous_throughput, options_files, bm_iter=0):
    '''
    Store the options in a file
    Do the benchmark

    Parameters:
    - db_bench_path (str): The path to the db_bench executable
    - database_path (str): The path to the database
    - option_file (dict): The options file to be used
    - run_count (str): The current iteration of the benchmark

    Returns:
    - None
    '''
    global proc_out
    with open(f"{OPTIONS_FILE_DIR}", "w") as f:
        f.write(options)

    # Perform pre-tasks to reset the environment
    pre_tasks(database_path, run_count)
    command = generate_db_bench_command(db_bench_path, database_path, options, run_count, test_name)

    log_update(f"[SPM] Executing db_bench with command: {command}")
    print("[SPM] Executing db_bench")


    if SIDE_CHECKER and previous_throughput != None:
        cgroup_monitor = CGroupMonitor()
        cgroup_monitor.start_monitor()
        start_time = time.time()

        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as proc_out:
            output = ""
            check_interval = 30
            for line in proc_out.stdout:
                output += line
                if time.time() - start_time <= check_interval:
                    continue

                start_time = time.time()
                if "ops/second" in line:
                    current_avg_throughput = float(line.split("(")[2].split(",")[1].split(")")[0])

                    if (current_avg_throughput < 0.9 * float(previous_throughput)) and (bm_iter < 3):
                        print("[SQU] Throughput decreased, resetting the benchmark")
                        log_update(f"[SQU] Throughput decreased {previous_throughput}->{current_avg_throughput}, resetting the benchmark")
                        avg_cpu_used, avg_mem_used = cgroup_monitor.stop_monitor()
                        proc_out.kill()

                        db_path = path_of_db()
                        fio_result = get_fio_result(FIO_RESULT_PATH)
                        device_info = system_info(db_path, fio_result)

                        new_options, _, _ = midway_options_file_generation(options, avg_cpu_used, avg_mem_used, current_avg_throughput, device_info, options_files)
                        output, avg_cpu_used, avg_mem_used, options = db_bench(db_bench_path, database_path, new_options, run_count, test_name, previous_throughput, options_files, bm_iter+1)

                        log_update("[SPM] Finished running db_bench")
                        return output, avg_cpu_used, avg_mem_used, options
                else:
                    print("[SQU] No throughput found in the output")
                    log_update("[SQU] No throughput found in the output")
                    # exit(1)

        print("[SPM] Finished running db_bench")
        print("----------------------------------------------------------------------------")
        print("[SPM] Output: ", output)
        avg_cpu_used, avg_mem_used = cgroup_monitor.stop_monitor()
        return output, avg_cpu_used, avg_mem_used, options
    else:
        cgroup_monitor = CGroupMonitor()
        cgroup_monitor.start_monitor()
        proc_out = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False
        )
        avg_cpu_used, avg_mem_used = cgroup_monitor.stop_monitor()
        return proc_out.stdout.decode(), avg_cpu_used, avg_mem_used, options


def benchmark(db_path, options, output_file_dir, reasoning, iteration_count, previous_results, options_files):
    '''
    Function to run db_bench with the given options file and store the output in a file

    Parameters:
    - db_path (str): The path of database
    - options (dict): The options to be used
    - output_file_dir (str): the output directory
    - reasoning (str): The reasoning of the benchmark

    Returns:
    - is_error (bool): 
    - benchmark_results (dict):
    '''
    if previous_results is None:
        output, average_cpu_usage, average_memory_usage, options = db_bench(
            DB_BENCH_PATH, db_path, options, iteration_count, TEST_NAME, None, options_files)
    else:
        output, average_cpu_usage, average_memory_usage, options = db_bench(
            DB_BENCH_PATH, db_path, options, iteration_count, TEST_NAME, previous_results['ops_per_sec'], options_files)

    # log_update(f"[SPM] Output: {output}")
    benchmark_results = parse_db_bench_output(output)

    contents = os.listdir(output_file_dir)
    ini_file_count = len([f for f in contents if f.endswith(".ini")])

    if benchmark_results.get("error") is not None:
        is_error = True
        log_update(f"[SPM] Benchmark failed, the error is: {benchmark_results.get('error')}")
        print("[SPM] Benchmark failed, the error is: ",
              benchmark_results.get("error"))
        # Save incorrect options in a file
        store_db_bench_output(output_file_dir,
                              f"{ini_file_count}-incorrect_options.ini",
                              benchmark_results, options, reasoning)
    elif benchmark_results['data_speed'] is None:
        is_error = True
        log_update(f"[SPM] Benchmark failed, the error is: Data speed is None. Check DB save path")
        print("[SPM] Benchmark failed, the error is: ",
              "Data speed is None. Check DB save path")
        # Save incorrect options in a file
        store_db_bench_output(output_file_dir,
                              f"{ini_file_count}-incorrect_options.ini",
                              benchmark_results, options, reasoning)
    else:
        is_error = False
        # Store the output of db_bench in a file
        store_db_bench_output(output_file_dir, f"{ini_file_count}.ini",
                              benchmark_results, options, reasoning)
        plot_2axis(*benchmark_results["ops_per_second_graph"],
                   "Ops Per Second",
                   f"{output_file_dir}/ops_per_sec_{ini_file_count}.png")
        log_update(f"[SPM] Latest result: {benchmark_results['data_speed']}"
                        f"{benchmark_results['data_speed_unit']} and {benchmark_results['ops_per_sec']} ops/sec.")
        log_update(f"[SPM] Avg CPU and Memory usage: {average_cpu_usage}% and {average_memory_usage}%")
        print(
            f"[SPM] Latest result: {benchmark_results['data_speed']}",
            f"{benchmark_results['data_speed_unit']} and {benchmark_results['ops_per_sec']} ops/sec.\n",
            f"[SPM] Avg CPU and Memory usage: {average_cpu_usage}% and {average_memory_usage}%"
        )

    return is_error, benchmark_results, average_cpu_usage, average_memory_usage, options
