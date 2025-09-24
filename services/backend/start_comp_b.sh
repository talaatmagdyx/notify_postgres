#!/bin/bash
# Company B Backend Startup Script

cd "$(dirname "$0")"
export COMPANY_CODE=COMP_B
export BACKEND_PORT=5002
source ../../.venv/bin/activate
export PYTHONPATH=../notification-engine
python unified_app.py
