import re
from difflib import Differ
from options_files.ops_options_file import cleanup_options_file
from gpt.gpt_request import request_gpt
from utils.utils import log_update
from dotenv import load_dotenv
import utils.constants as constants

load_dotenv()

def generate_system_content(device_information, rocksdb_version):
    """
    Function to generate the system content with device info and rocksDB version.
    
    Parameters:
        device_information (str): Information about the device.
        
    Returns:
        str: A prompt for configuring RocksDB for enhanced performance.
    """

    content = (
        "You are a RocksDB Expert. "
        "You are being consulted by a company to help improve their RocksDB configuration "
        "by optimizing their options file based on their System information and benchmark output."
        f"Only provide option files for rocksdb version {rocksdb_version}. Also, Direct IO will always be used for both flush and compaction."
        "Additionally, compression type is set to none always."
        "First Explain the reasoning, only change 10 options, then show the option file in original format."
        f"The Device information is: {device_information}"
    )
    return content

def generate_default_user_content(chunk_string, previous_option_files, average_cpu_used=-1.0, average_mem_used=-1.0, test_name="fillrandom"):
    user_contents = []
    for _, benchmark_result, reasoning, _ in previous_option_files[1: -1]:
        benchmark_line = generate_benchmark_info(test_name, benchmark_result, average_cpu_used, average_mem_used)
        user_content = f"The option file changes were:\n```\n{reasoning}\n```\nThe benchmark results are: {benchmark_line}"
        user_contents.append(user_content)

    _, benchmark_result, _, _ = previous_option_files[-1]
    benchmark_line = generate_benchmark_info(test_name, benchmark_result, average_cpu_used, average_mem_used)
    user_content = f"Part of the current option file is:\n```\n{chunk_string}\n```\nThe benchmark results are: {benchmark_line}"
    user_contents.append(user_content)
    user_contents.append("Based on these information generate a new file in same format as the options_file to improve my database performance. Enclose the new options file in ```.")
    return user_contents

def generate_user_content_with_difference(previous_option_files, average_cpu_used=-1.0, average_mem_used=-1.0, test_name="fillrandom"):
    result =" "
    user_content = []

    if len(previous_option_files) == 1:
        m1_file, m1_benchmark_result, _, _ = previous_option_files[-1]
        benchmark_line = generate_benchmark_info(test_name, m1_benchmark_result, average_cpu_used, average_mem_used)
        user_content = f"The original file is:\n```\n{m1_file}\n```\nThe benchmark results for the original file are: {benchmark_line}"
    
    elif len(previous_option_files) > 1:
        previous_option_file1, _, _, _ = previous_option_files[-1]
        previous_option_file2, _, _, _ = previous_option_files[-2]

        pattern = re.compile(r'\s*([^=\s]+)\s*=\s*([^=\s]+)\s*')

        file1_lines = pattern.findall(previous_option_file1)
        file2_lines = pattern.findall(previous_option_file2)

        file1_lines = ["{} = {}".format(k, v) for k, v in file1_lines]
        file2_lines = ["{} = {}".format(k, v) for k, v in file2_lines]
        differ = Differ()
        diff = list(differ.compare(file1_lines, file2_lines))
        lst= []
        for line in diff:
            if line.startswith('+'):
                lst.append(line)
        result = '\n'.join(line[2:] for line in lst)
        m2_file, m2_benchmark_result, _, _ = previous_option_files[-2]
        benchmark_line = generate_benchmark_info(test_name, m2_benchmark_result, average_cpu_used, average_mem_used)
        user_content = (
            f"The original file is:\n```\n{m2_file}\n```\n"
            f"The benchmark results for the original file are: {benchmark_line}\n"
            f"The previous file modifications are:\n```\n{result}\n```\n"
        )
    
    else:
        _, benchmark_result, _, _ = previous_option_files[-1]
        benchmark_line = generate_benchmark_info(test_name, benchmark_result, average_cpu_used, average_mem_used)

        user_content = ("The previous file modifications are: "
                         f"\n```\n{result}\n```\n"
                         f"The benchmark results for the previous file are: {benchmark_line}")
    
    
    user_contents = [user_content, "Based on these information generate a new file in the same format as the options_file to improve my database performance. Enclose the new options file in ```."]
    return user_contents

def generate_benchmark_info(test_name, benchmark_result, average_cpu_used, average_mem_used):
    """
    Function to create a formatted string with benchmark information.

    Parameters:
    - test_name: Name of the test.
    - benchmark_result: Dictionary with benchmark results.
    - average_cpu_used: Average CPU usage.
    - average_mem_used: Average Memory usage.

    Returns:
    - A formatted string with all benchmark information.
    """
    benchmark_line = (f"The use case for the database is perfectly simulated by the {test_name} test. "
                      f"The db_bench benchmark results for {test_name} are: Write/Read speed: {benchmark_result['data_speed']} "
                      f"{benchmark_result['data_speed_unit']}, Operations per second: {benchmark_result['ops_per_sec']}.")
    
    if average_cpu_used != -1 and average_mem_used != -1:
        benchmark_line += f" CPU used: {average_cpu_used}%, Memory used: {average_mem_used}% during test."
    
    return benchmark_line

def midway_options_file_generation(options, avg_cpu_used, avg_mem_used, last_throughput, device_information, options_file):
    """
    Function to generate a prompt for the midway options file generation.
    
    Returns:
    - str: A prompt for the midway options file generation.
    """

    sys_content = (
        "You are a RocksDB Expert being consulted by a company to help improve their RocksDB performance "
        "by optimizing the options configured for a particular scenario they face."
        f"Only provide option files for rocksdb version {constants.VERSION}. Direct IO will always be used. "
        "Additionally, compression type is set to none always. "
        "Respond with the the reasoning first, then show the option file in original format."
        f"The Device information is: {device_information}"
    )

    user_content = []
    content = "Can you generate a new options file for RocksDB based on the following information?\n"
    content += "The previous options file is:\n"

    content += "```\n"
    content += options_file[-1][0]
    content += "```\n"

    content += (
        f"The throughput results for the above options file are: {options_file[-1][1]['ops_per_sec']}. "
    )

    user_content.append(content)
    content = ""

    content += "We then made the following changes to the options file:\n"

    pattern = re.compile(r'\s*([^=\s]+)\s*=\s*([^=\s]+)\s*')

    file1_lines = pattern.findall(options)
    file2_lines = pattern.findall(options_file[-1][0])

    file1_lines = ["{} = {}".format(k, v) for k, v in file1_lines]
    file2_lines = ["{} = {}".format(k, v) for k, v in file2_lines]
    differ = Differ()
    diff = list(differ.compare(file1_lines, file2_lines))
    lst= []
    for line in diff:
        if line.startswith('+'):
            lst.append(line)
    result = '\n'.join(line[2:] for line in lst)

    content += "```\n"
    content += result
    content += "```\n"

    content += f"\nThe updated file has a throughput of: {last_throughput}. \n\n"
    user_content.append(content)
    content = ""
    content += "Based on this information generate a new file. Enclose the new options in ```. Feel free to use upto 100% of the CPU and Memory."
    user_content.append(content)

    log_update("[OG] Generating options file with differences")
    log_update("[OG] Prompt for midway options file generation")
    log_update(content)

    matches = request_gpt(sys_content, user_content, 0.4)

    if matches is not None:
        clean_options_file = cleanup_options_file(matches[1])
        reasoning = matches[0] + matches[2]

    return clean_options_file, reasoning, ""

def generate_option_file_with_gpt(case, previous_option_files, device_information, temperature=0.4, average_cpu_used=-1.0, average_mem_used=-1.0, test_name="fillrandom", version="8.8.1"):
    """
    Function that generates an options file for RocksDB based on specified parameters and case scenarios.
    - This function selects one of three different approaches to generate a RocksDB configuration options file. 
    
    Parameters:
    - case (int): Determines the approach to use for generating the options file. Valid values are 1, 2, or 3.
    - previous_option_files (list): A list of tuples containing past options file configurations and other relevant data.
    - device_information (str): Information about the device/system on which RocksDB is running.
    - temperature (float, optional): Controls the randomness/creativity of the generated output. Default is 0.4.
    - average_cpu_used (float, optional): Average CPU usage, used for tuning the configuration. Default is -1.0, indicating not specified.
    - average_mem_used (float, optional): Average memory usage, used for tuning the configuration. Default is -1.0, indicating not specified.
    - test_name (str, optional): Identifier for the type of test or configuration scenario. Default is "fillrandom".

    Returns:
    - tuple: A tuple containing the generated options file, reasoning behind the options, and an empty string as a placeholder.

    Raises:
    - ValueError: If the `case` parameter is not 1, 2, or 3.
    """
    def case_1(previous_option_files, device_information, temperature,average_cpu_used, average_mem_used, test_name, version):
        log_update("[OG] Generating options file with long option changes")
        print("[OG] Generating options file with long option changes")
        system_content = generate_system_content(device_information, version)
        previous_option_file, _, _, _ = previous_option_files[-1]
        user_contents = generate_default_user_content(previous_option_file, previous_option_files, average_cpu_used, average_mem_used, test_name)
        matches = request_gpt(system_content, user_contents, temperature)
        # Process the GPT-generated response 
        if matches is not None:
            clean_options_file = cleanup_options_file(matches[1])
            reasoning = matches[0] + matches[2]

        return clean_options_file, reasoning, ""

    def case_2(previous_option_files, device_information, temperature,average_cpu_used, average_mem_used, test_name, version):
        log_update("[OG] Generating options file with short option changes")
        print("[OG] Generating options file with short option changes")
        system_content = (
            "You are a RocksDB Expert. "
            "You are being consulted by a company to help improve their RocksDB configuration "
            "by optimizing their options file based on their System information and benchmark output."
            f"Only provide option files for rocksdb version {version}. Also, Direct IO will always be used for both flush and compaction."
            "Additionally, compression type is set to none always."
            "First Explain the reasoning, only change the options I provided, then show the option file in original format."
            f"The Device information is: {device_information}")
        previous_option_file, _, _, _ = previous_option_files[-1]

        # Define a regular expression pattern to match key-value pairs
        pattern = re.compile(r'\s*([^=\s]+)\s*=\s*([^=\s]+)\s*')

        # Extract key-value pairs from the string
        key_value_pairs = {match.group(1): match.group(
            2) for match in pattern.finditer(previous_option_file)}

        # Remove key-value pairs where the key is "xxx" (case-insensitive)
        key_value_pairs = {key: value for key, value in key_value_pairs.items(
        ) if key.lower() not in {'rocksdb_version', 'options_file_version'}}

        # Split key-value pairs into chunks of 5 pairs each
        pairs_per_chunk = 20
        chunks = [list(key_value_pairs.items())[i:i + pairs_per_chunk]
                for i in range(0, len(key_value_pairs), pairs_per_chunk)]

        # Create strings for each chunk
        chunk_strings = [
            '\n'.join([f"{key}: {value}" for key, value in chunk]) for chunk in chunks]

        clean_options_file = ""
        reasoning = ""

        # Loop through each part and make API calls
        for chunk_string in chunk_strings:
            user_contents = generate_default_user_content(chunk_string, previous_option_files, average_cpu_used, average_mem_used, test_name)
            matches = request_gpt(system_content, user_contents, temperature)
            if matches is not None:
                clean_options_file = cleanup_options_file(matches[1])
                reasoning += matches[0] + matches[2]

        return clean_options_file, reasoning, ""


    def case_3(previous_option_files, device_information, temperature,average_cpu_used, average_mem_used, test_name, version):
        
        log_update("[OG] Generating options file with differences")
        print("[OG] Generating options file with differences")
        system_content = generate_system_content(device_information, version)
        # Request GPT to generate new option
        user_contents = generate_user_content_with_difference(previous_option_files, average_cpu_used, average_mem_used, test_name)
        matches = request_gpt(system_content, user_contents, temperature)
        # Process the GPT response
        if matches is not None:
            clean_options_file = cleanup_options_file(matches[1])
            reasoning = matches[0] + matches[2]

        return clean_options_file, reasoning, ""
    
    switch = {
        1: case_1,
        2: case_2,
        3: case_3,
    }
    func = switch.get(case)
    if func:
        return func(previous_option_files, device_information, temperature,average_cpu_used, average_mem_used, test_name, version)
    else:
        raise ValueError(f"No function defined for case {case}")