# ELMo-Tune

## Features
This project will run a series of tests using the db_bench tool.  The tests will be run using the default configuration and a series of configurations that will be determined by the research.  The results of the tests will be compared to determine the best configuration for RocksDB when using GPT Assisted RocksDB.

## Prerequisites
This project requires Python 3.6 or higher.  The following dependencies are required:
```
# Instructions for Ubuntu 20.04
# Install dependencies
apt-get update && apt-get install -y build-essential libgflags-dev libsnappy-dev zlib1g-dev libbz2-dev liblz4-dev libzstd-dev git python3 python3-pip wget fio 

# Install and Build RocksDB 8.8.1
wget https://github.com/facebook/rocksdb/archive/refs/tags/v8.8.1.tar.gz
tar -xzf v8.8.1.tar.gz
cd rocksdb-8.8.1
make -j static_lib db_bench

git clone <repo url>
cd gpt-assisted-rocksdb-config

# Install requirements
pip install -r requirements.txt
```

## How to use
To run the tests, run the following command:
```
# Make sure the paths in main.py are correctly set for your system
python3 main.py

# You can explore the options using the --help command (or using the constants.py file)
```

> You can alternatively also use the Docker environment that can be built using the Dockerfile in the docker folder. 