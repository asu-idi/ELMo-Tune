import os
from dotenv import load_dotenv
import argparse
from datetime import datetime

load_dotenv()

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
    output_folder_dir = f"output/output_{DEVICE}/output_{date_time_string}"

    os.makedirs(output_folder_dir, exist_ok=True)
    print(f"[UTL] Using output folder: {output_folder_dir}")

    return output_folder_dir

# Check the environement variables, set to default if not found
env_DEVICE = os.getenv("DEVICE", None)
env_TEST_NAME = os.getenv("TEST_NAME", None)
env_CASE_NUMBER = os.getenv("CASE_NUMBER", 1)
env_VERSION = os.getenv("VERSION", "8.8.1")
env_OUTPUT_PATH = os.getenv("OUTPUT_PATH", None)
env_NUM_ENTRIES = os.getenv("NUM_ENTRIES", 3000000000)
env_SIDE_CHECKER = os.getenv("SIDE_CHECKER", True)

# Parse the arguments. They replace the environment variables if they are set
parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument('-c', '--case', type=int, default=env_CASE_NUMBER, help='Specify the case number')
parser.add_argument('-d', '--device', type=str, default=env_DEVICE, help='Specify the device')
parser.add_argument('-t', '--workload', type=str, default=env_TEST_NAME, help='Specify the test name')
parser.add_argument('-v', '--version', type=str, default=env_VERSION, help='Specify the version of RocksDB')
parser.add_argument('-o', '--output', type=str, default=env_OUTPUT_PATH, help='Specify the output path')
parser.add_argument('-n', '--num_entries', type=int, default=env_NUM_ENTRIES, help='Specify the number of entries')
parser.add_argument('-s', '--side_checker', type=bool, default=env_SIDE_CHECKER, help='Specify if side checker is enabled')

args = parser.parse_args()
CASE_NUMBER = args.case
DEVICE = args.device
TEST_NAME = args.workload
VERSION = args.version
OUTPUT_PATH = args.output if args.output else path_of_output_folder()
NUM_ENTRIES = args.num_entries
SIDE_CHECKER = args.side_checker

# Constants
# DB_BENCH_PATH = f"/data/gpt_project/rocksdb-{VERSION}/db_bench"
DB_BENCH_PATH = f"/rocksdb-{VERSION}/db_bench"
DB_PATH = f"/{DEVICE}/gpt_project/db"
FIO_RESULT_PATH = f"/data/gpt_project/gpt-assisted-rocksdb-config/data/fio/fio_output_{DEVICE}.txt"
DEFAULT_OPTION_FILE_DIR = "options_files/default_options_files"
INITIAL_OPTIONS_FILE_NAME = f"dbbench_default_options-{VERSION}.ini"
OPTIONS_FILE_DIR = f"{OUTPUT_PATH}/options_file.ini"
