# ELMo-Tune ([HotStorage'24 Best Paper] Can Modern LLMs Tune and Configure LSM-based Key-Value Stores?)

🏆HotStorage'24 Best Paper - Can Modern LLMs Tune and Configure LSM-based Key-Value Stores?<br>
Paper URL: [https://doi.org/10.1145/3655038.3665954](https://doi.org/10.1145/3655038.3665954)

## Features
This project will run a series of tests using the db_bench tool. The tests will be run using the default configuration and a series of configurations that will be determined by the research. The results of the tests will be compared to determine the best configuration for RocksDB when using ELMo-Tune.

## Prerequisites
This project requires Python 3.6 or higher. The following dependencies are required:
```bash
# Instructions for Ubuntu 20.04
# Install dependencies
apt-get update && apt-get install -y build-essential libgflags-dev libsnappy-dev zlib1g-dev libbz2-dev liblz4-dev libzstd-dev git python3 python3-pip wget fio 

# Install and Build RocksDB 8.8.1
wget https://github.com/facebook/rocksdb/archive/refs/tags/v8.8.1.tar.gz
tar -xzf v8.8.1.tar.gz
cd rocksdb-8.8.1
make -j static_lib db_bench

git clone https://github.com/asu-idi/ELMo-Tune
cd ELMo-Tune

# Install requirements
pip install -r requirements.txt
```

## Setup
To run the tests sucessfully, some variables need to be defined.
```bash
# You need OpenAI's API to run the code sucessfully. 
export OPENAI_API_KEY=<api key>
```
Additionally, set the DB_BENCH_PATH in utils/constants.py along with any other paths required for your system setup. 

## How to use
To run the tests, run the following command:
```bash
# e.g. Run a random write (fillrandom) test with the db stored in the '/data/gpt_project/db' folder and with output in the './output' directory 
python3 main.py --workload=fillrandom --device=data --output=./output --num_entries=10000

# You can explore the options using the --help command (or using the constants.py file)
#  -c --case            CASE            Specify the case number
#  -d --device          DEVICE          Specify the device
#  -t --workload        WORKLOAD        Specify the test name
#  -v --version         VERSION         Specify the version of RocksDB
#  -o --output          OUTPUT          Specify the output path
#  -n --num_entries     NUM_ENTRIES     Specify the number of entries
#  -s --side_checker    SIDE_CHECKER    Specify if side checker is enabled
```

> You can alternatively also use the Docker environment that can be built using the Dockerfile in the docker folder. 
