#!/bin/bash
# Backend startup script

cd "$(dirname "$0")"
source ../../.venv/bin/activate
export PYTHONPATH=../notification-engine
python app.py
