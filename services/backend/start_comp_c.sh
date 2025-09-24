#!/bin/bash
# Company C Backend Startup Script

cd "$(dirname "$0")"
export COMPANY_CODE=COMP_C
export BACKEND_PORT=5003
source ../../.venv/bin/activate
export PYTHONPATH=../notification-engine
python unified_app.py
