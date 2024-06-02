import os
import json
import getpass
from datetime import datetime
from collections import defaultdict
from deepdiff import DeepDiff
from utils.constants import OUTPUT_PATH, DEVICE, DB_PATH

# LOG UTILS
def log_update(update_string):
    '''
    Update the log file with the given string

    Parameters:
    - update_string (str): The string to be updated in the log file

    Returns:
    - None
    '''
    current_datetime = datetime.now()
    date_time_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    update_string = f"[{date_time_string}] {update_string}"
    
    if OUTPUT_PATH is None:
        with open(f"log.txt", "a+") as f:
            f.write(update_string + "\n")
    else:
        with open(f"{OUTPUT_PATH}/log.txt", "a+") as f:
            f.write(update_string + "\n")

# STORE FILE UTILS
def store_db_bench_output(output_folder_name, output_file_name,
                          benchmark_results, options_file, reasoning):
    '''
    Store the output of db_bench in a file

    Parameters:
    - output_folder_name (str): Name of the folder to store the output file
    - output_file_name (str): Name of the output file
    - benchmark_results (dict): Dictionary containing the benchmark results
    - options_file (str): The options file used to generate the benchmark results
    - reasoning (str): The reasoning behind the options file

    Returns:
    - None
    '''
    with open(f"{output_folder_name}/{output_file_name}", "a+") as f:
        f.write("# " + json.dumps(benchmark_results) + "\n\n")
        f.write(options_file + "\n")
        for line in reasoning.splitlines():
            f.write("# " + line + "\n")

def store_best_option_file(options_files, output_folder_dir):
    '''
    Save the best option file

    Parameters:
    - options_files (list): List of options files
    - output_folder_dir (str): The output directory
    '''
    best_result = max(options_files, key=lambda x: x[1]["ops_per_sec"])
    best_options = best_result[0]
    best_reasoning = best_result[2]
    with open(f"{output_folder_dir}/best_options.ini", "w") as f:
        f.write(best_options)
        for line in best_reasoning.splitlines():
            f.write("# " + line + "\n")

def store_diff_options_list(options_list, output_folder_dir):
    # Calculate differences between options_list
    differences = calculate_differences(options_list)
    changed_fields_frequency = defaultdict(lambda: 0)

    with open(f"{output_folder_dir}/diffOptions.txt", 'w') as f:
        for i, diff in enumerate(differences, start=1):
            f.write(f"[MFN] Differences between iteration {i} and iteration {i + 1}: \n")
            f.write(json.dumps(diff, indent=4))
            f.write("\n")
            f.write("=" * 50)
            f.write("\n\n")

            for key in diff["values_changed"]:
                changed_fields_frequency[key] += 1

        f.write("\n\n[MFN] Changed Fields Frequency:\n")
        f.write(json.dumps(changed_fields_frequency, indent=4))

# PATH UTILS
def path_of_db():
    '''
    Choose the database path

    Parameters:
    - None

    Returns:
    - db_path (str): The path of the database
    '''
    user_name = getpass.getuser()
    db_path_name = DB_PATH + user_name[0].lower()
    db_path = os.getenv("DB_PATH", db_path_name)
    # log_update(f"[UTL] Using database path: {db_path}")
    print(f"[UTL] Using database path: {db_path}")

    return db_path

def path_of_output_folder():
    '''
    Set the output folder directory

    Parameters:
    - None

    Returns:
    - output_folder_dir (str): The output folder directory
    '''
    current_datetime = datetime.now()
    date_time_string = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    if OUTPUT_PATH is None:
        output_folder_dir = f"output/output_{DEVICE}/output_{date_time_string}"
    else:
        output_folder_dir = OUTPUT_PATH

    os.makedirs(output_folder_dir, exist_ok=True)
    log_update(f"[UTL] Using output folder: {output_folder_dir}")
    print(f"[UTL] Using output folder: {output_folder_dir}")

    return output_folder_dir

# OTHER UTILS
def calculate_differences(iterations):
    '''
    Function to calculate the differences between the iterations

    Parameters:
    - iterations (list): A list of the iterations

    Returns:
    - differences (list): A list of the differences between the iterations
    '''
    differences = []
    for i in range(1, len(iterations)):
        diff = DeepDiff(iterations[i-1], iterations[i])
        differences.append(diff)
    return differences
