#!/bin/bash
until python -m broccoli_bot >/dev/null; do
    sleep 5
done
