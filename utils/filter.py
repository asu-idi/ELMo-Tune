def key_filter(key):
    if (key == 'wal_size_limit_mb'):
        key = 'WAL_size_limit_MB'
    if (key == 'wal_ttl_seconds'):
        key = 'WAL_ttl_seconds'
    return key

# Options that should not be changed
BLACKLIST = ['use_direct_io_for_flush_and_compaction',
                'use_direct_reads', 'compression_type']
