#!/bin/bash
until python -m broccoli_bot 2>error_text; do
    sleep 5
done
