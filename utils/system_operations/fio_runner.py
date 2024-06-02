import subprocess
import re
import os


def fio_run(test_type, file_path):
    '''
    Function to run fio benchmark

    Parameters:
    - test_type: string containing the type of test to run

    Returns:
    - parsed_res: string containing the parsed result of the fio test
    '''
    command = [
        "fio",
        "--name=test",
        "--ioengine=posixaio",
        f"--rw={test_type}",
        "--bs=4k",
        "--numjobs=1",
        "--size=10G",
        "--runtime=60",
        "--time_based"
    ]

    print("[FIO] running fio test now", test_type + "\n")
    proc = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = proc.stdout.decode()
    print("[FIO] output :", output)

    parsed_res = parse_fio_output(output, test_type)

    with open(file_path, "a") as file:
        file.write(parsed_res + '\n')

    return parsed_res


def get_fio_result(file_path):
    '''
    Function to get the fio result

    Parameters:
    - file_path: string containing the path to the fio result file

    Returns:
    - content: string containing the content of the fio result
    '''
    if (os.path.exists(file_path) and os.path.getsize(file_path) != 0):
        print("[FIO] File exists and is not empty. Reading file.")
        with open(file_path, 'r') as file:
            content = file.read()
        return content

     # List of test types
    test_types = ["randwrite", "randread", "read", "write"]
    for test_type in test_types:
        fio_result = fio_run(test_type, file_path)
        combined_result = '\n'.join(fio_result)

    print(f"[FIO] result : \n {combined_result}")
    delete_test_file()
    return combined_result


def parse_fio_output(fio_result, test_type):
    '''
    Function to parse the fio output

    Parameters:
    - fio_result: string containing the fio result
    - test_type: string containing the type of test to run

    Returns:
    - result_string: string containing the parsed result of the fio test
    '''
    if test_type in ["randwrite", "write"]:
        pattern = re.compile(r'WRITE: bw=(.*?)\s\(.*?\),\s(.*?)\s\(.*?\)')
    elif test_type in ["randread", "read"]:
        pattern = re.compile(r'READ: bw=(.*?)\s\(.*?\),\s(.*?)\s\(.*?\)')
    else:
        print(f"[FIO] Unsupported test type: {test_type}")

    match = pattern.search(fio_result)
    if match:
        values_list = [match.group(1), match.group(2)]
        result_string = f"{test_type} bandwidth is {values_list[0]} ({values_list[1]})"
        print(f"[FIO] result string : {result_string}")
    else:
        print("[FIO] Pattern not found in the fio result.")

    return result_string


def delete_test_file():
    '''
    Function to delete the test file
    '''
    proc = subprocess.run(
        f'rm test.0.0',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True
    )
