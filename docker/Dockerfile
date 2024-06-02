FROM ubuntu:20.04

ARG TARGETPLATFORM
ARG DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgflags-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev \
    libzstd-dev \
    cmake \
    git \
    python3 \
    python3-pip \
    wget \
    fio \
    libjemalloc2

# Setup RocksDB
RUN wget https://github.com/facebook/rocksdb/archive/refs/tags/v8.8.1.tar.gz && \
    tar -xzf v8.8.1.tar.gz && \
    cd rocksdb-8.8.1 && \
    make -j48 static_lib db_bench

# Setup GPT Repo's requirements
ADD gpt-assisted-rocksdb-config/requirements.txt /requirements.txt

# Setup Python requirments
RUN pip3 install -r requirements.txt

# Setup GPT Repo
ADD gpt-assisted-rocksdb-config /gpt-assisted-rocksdb-config

WORKDIR /gpt-assisted-rocksdb-config
CMD ["python3", "main.py"]
