import os
import psutil
import subprocess
import platform
from cpuinfo import get_cpu_info
from cgroup_monitor import CGroupMonitor

def get_system_data(db_path):
    '''
    Function to get the system data
    
    Parameters:
    - db_path (str): The path of database
    
    Returns:
    - brand_raw_value (str): The CPU model name
    - memory_total (int): The total memory
    - swap (int): The swap memory
    - total_disk_size (int): The total disk size
    - device (str): The device name
    '''
    cgroup_monitor = CGroupMonitor()
    try:
        cpu_count = os.getenv("CPU_COUNT", str(cgroup_monitor.get_cpu_limit()))
        mem_max = os.getenv("MEMORY_MAX", str(cgroup_monitor.get_memory_limit()))

        # gets the CPU op-modes
        system_info = platform.uname()
        cpu_op_modes = system_info.processor

        # gets the CPU model name
        cpu_model = platform.processor()

        # get all the CPU cache sizes
        cpu_info = get_cpu_info()
        brand_raw_value = cpu_count + " cores of " + cpu_info['brand_raw']

        l1_data_cache_size = cpu_info.get('l1_data_cache_size', 'N/A')
        l1_instruction_cache_size = cpu_info.get(
            'l1_instruction_cache_size', 'N/A')
        l2_cache_size = cpu_info.get('l2_cache_size', 'N/A')
        l3_cache_size = cpu_info.get('l3_cache_size', 'N/A')

        # get the total memory
        # memory_total = psutil.virtual_memory().total
        memory_total = float(mem_max)

        # gets the percentage of RAM used
        memory_used = psutil.virtual_memory().percent

        # gets the percentage of RAM available
        memeory_remaining = psutil.virtual_memory().available * 100 / \
            psutil.virtual_memory().total

        # gets the disk information
        # partitions = psutil.disk_partitions(all=True)

        swap = psutil.swap_memory()

        partitions = psutil.disk_partitions(all=False)
        path = os.path.dirname(db_path)
        total_disk_size = -1
        device = ""
        all_devices = check_drive_type()
        data_directory = path[:5]
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            if (partition.mountpoint[:5] == data_directory):
                total_disk_size = usage.total
                if (partition.device.split('/')[-1] in all_devices):
                    device = all_devices[partition.device.split('/')[-1]]
                elif (partition.device.split('/')[-1][:-1] in all_devices):
                    device = all_devices[partition.device.split('/')[-1][:-1]]

        # returns all the system data required
        return brand_raw_value, memory_total, swap, total_disk_size, device

    except Exception as e:
        print(f"[SYS] Error in fetching system data: {e}")
        return None

# Check drive type
def check_drive_type():
    '''
    Function to check the drive type
    
    Returns:
    - drive_types (dict): A dictionary containing the drive types
    '''
    # Path where the drive information is stored
    sys_block_path = "/sys/block"
    # Check if the path exists
    if os.path.exists(sys_block_path):
        # List of all devices
        devices = os.listdir(sys_block_path)
        drive_types = {}
        # Iterate through each device
        for device in devices:
            try:
                with open(f"{sys_block_path}/{device}/queue/rotational", "r") as file:
                    rotational = file.read().strip()
                    if rotational == "0":
                        drive_types[device] = "SSD"
                    else:
                        drive_types[device] = "HDD"
            except IOError:
                # Unable to read the rotational file for this device
                pass
        return drive_types
    else:
        return "System block path does not exist."

def system_info(db_path, fio_result):
    '''
    Fetch system data for further runs 

    Parameters:
    - db_path (str): The path of database
    - fio_result (str): The result of fio benchmark
    '''
    system_data = get_system_data(db_path)
    data = (f"{system_data[0]} with {system_data[1]}GiB of Memory and {system_data[1]}GiB of Swap space."
            f"{system_data[4]} size : {system_data[3]/(1024 ** 4):.2f}T. A single instance of RocksDB is the always going to be the only process running. "
            f"{fio_result}")
    return data
