#!/bin/bash
# Company A Backend Startup Script

cd "$(dirname "$0")"
export COMPANY_CODE=COMP_A
export BACKEND_PORT=5001
source ../../.venv/bin/activate
export PYTHONPATH=../notification-engine
python unified_app.py
