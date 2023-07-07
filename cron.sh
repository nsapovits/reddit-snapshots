#!/bin/sh
logger -t reddit-snapshot Starting scheduled reddit-snapshot job
cd /reddit-snapshots/
python3 reddit-snapshots.py
logger -t reddit-snapshot Finished scheduled reddit-snapshot job
