import docker
import os

client = docker.from_env()

def main():
    '''
    Main function to run multiple docker containers one after the other. All containers mount a volume to the host machine.
    Additionally, before mounting, the environment variables are updated to reflect the current iteration number and the status 
    of the for loop which is controlling the memory and cpus. 
    '''

    cpu_list = [2, 4]
    memory_list = [4, 8]
    devices = ["nvme", "data"]
    tests = ["fillrandom", "readrandom", "readrandomwriterandom"]
    base_output_path = f"/data/gpt_project/gpt-assisted-rocksdb-config/output/output"
    base_db_path = f"gpt_project/dbr"

    for memory_cap in memory_list:
        for cpu_cap in cpu_list:
            for test in tests:
                print("-" * 50)
                print(f"Running Iteration for CPU: {cpu_cap} Memory: {memory_cap} on /{devices[0]} and /{devices[1]} for {test}")

                # Run docker container with mount and environment variables as in cpu and memory
                container = client.containers.run(
                    "gptproject:latest", 
                    detach=True, 
                    name=f"gpt_project_c{cpu_cap}_m{memory_cap}_{devices[0]}_{test}",
                    environment=[f"ITERATION=c{cpu_cap}m{memory_cap}", f"CPU_COUNT={cpu_cap}", f"MEMORY_MAX={memory_cap}",
                                f"OUTPUT_PATH={base_output_path}_{devices[0]}/c{cpu_cap}_m{memory_cap}_{test}", 
                                f"DEVICE={devices[0]}", f"TEST_NAME={test}", f"DB_PATH=/{devices[0]}/{base_db_path}/{cpu_cap}_{test}"],
                    cpu_count=cpu_cap,
                    mem_limit=f"{memory_cap}g", 
                    volumes={"/nvme/gpt_project": {'bind': '/nvme/gpt_project', 'mode': 'rw'},
                                "/data/gpt_project": {'bind': '/data/gpt_project', 'mode': 'rw'}}
                )

                # Run docker container with mount and environment variables as in cpu and memory
                container2 = client.containers.run(
                    "gptproject:latest", 
                    detach=True, 
                    name=f"gpt_project_c{cpu_cap}_m{memory_cap}_{devices[1]}_{test}",
                    environment=[f"ITERATION=c{cpu_cap}m{memory_cap}", f"CPU_COUNT={cpu_cap}", f"MEMORY_MAX={memory_cap}",
                                f"OUTPUT_PATH={base_output_path}_{devices[1]}/c{cpu_cap}_m{memory_cap}_{test}",
                                f"DEVICE={devices[1]}", f"TEST_NAME={test}", f"DB_PATH=/{devices[1]}/{base_db_path}/{cpu_cap}_{test}"],
                    cpu_count=cpu_cap,
                    mem_limit=f"{memory_cap}g", 
                    volumes={"/nvme/gpt_project": {'bind': '/nvme/gpt_project', 'mode': 'rw'},
                                "/data/gpt_project": {'bind': '/data/gpt_project', 'mode': 'rw'}}
                )

            # Wait for the container to finish
            container.wait()
            container2.wait()

if __name__ == "__main__":
    main()