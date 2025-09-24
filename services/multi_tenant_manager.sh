#!/bin/bash
# Multi-Tenant Service Manager for PostgreSQL Notification System
# Manages services for multiple companies with separate ports and schemas

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Company configurations (using functions instead of associative arrays)
get_company_info() {
    local company_code=$1
    case $company_code in
        COMP_A) echo "Company Alpha:company_a:3001:5001" ;;
        COMP_B) echo "Company Beta:company_b:3002:5002" ;;
        COMP_C) echo "Company Gamma:company_c:3003:5003" ;;
        *) echo "" ;;
    esac
}

get_all_companies() {
    echo "COMP_A COMP_B COMP_C"
}

# Service directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/services/backend"
FRONTEND_DIR="$PROJECT_ROOT/services/frontend"
DATABASE_DIR="$PROJECT_ROOT/services/database"
ENGINE_DIR="$PROJECT_ROOT/services/notification-engine"

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local start_command=$3
    local port=$4
    
    if check_service $service_name $port; then
        print_warning "$service_name is already running on port $port"
        return 0
    fi
    
    cd $service_dir
    nohup $start_command > /tmp/${service_name}.log 2>&1 &
    local pid=$!
    echo $pid > /tmp/${service_name}.pid
    cd - > /dev/null
    
    # Wait for service to start
    sleep 3
    
    if check_service $service_name $port; then
        print_success "$service_name started successfully on port $port"
    else
        print_error "Failed to start $service_name"
        return 1
    fi
}

# Function to stop a service
stop_service() {
    local service_name=$1
    local port=$2
    
    if ! check_service $service_name $port; then
        print_warning "$service_name is not running"
        return 0
    fi
    
    # Find and kill the process
    if [ -f "/tmp/${service_name}.pid" ]; then
        local pid=$(cat /tmp/${service_name}.pid)
        kill $pid 2>/dev/null
        rm -f /tmp/${service_name}.pid
    fi
    
    # Also kill by port as backup
    local pid=$(lsof -t -i :$port)
    if [ ! -z "$pid" ]; then
        kill $pid 2>/dev/null
    fi
    
    print_success "$service_name stopped successfully"
}

# Function to restart a service
restart_service() {
    local service_name=$1
    local service_dir=$2
    local start_command=$3
    local port=$4
    
    print_info "Restarting $service_name..."
    stop_service $service_name $port
    sleep 2
    start_service $service_name $service_dir $start_command $port
}

# Function to start all services for a company
start_company_services() {
    local company_code=$1
    local company_info=$(get_company_info $company_code)
    
    if [ -z "$company_info" ]; then
        print_error "Unknown company: $company_code"
        return 1
    fi
    
    IFS=':' read -r company_name schema_name frontend_port backend_port <<< "$company_info"
    
    print_info "Starting services for $company_name ($company_code)..."
    
    # Start backend
    local script_name=""
    case $company_code in
        COMP_A) script_name="./start_comp_a.sh" ;;
        COMP_B) script_name="./start_comp_b.sh" ;;
        COMP_C) script_name="./start_comp_c.sh" ;;
    esac
    
    start_service "${company_code}_backend" "$BACKEND_DIR" \
        "$script_name" \
        $backend_port
    
    # Start frontend (if different frontend needed)
    # For now, we'll use the same frontend but with different configurations
    if [ ! -f "/tmp/${company_code}_frontend.pid" ]; then
        print_info "Frontend for $company_name will be available at http://localhost:$frontend_port"
        print_info "You can manually start the frontend with the appropriate App component"
    fi
}

# Function to stop all services for a company
stop_company_services() {
    local company_code=$1
    local company_info=$(get_company_info $company_code)
    
    if [ -z "$company_info" ]; then
        print_error "Unknown company: $company_code"
        return 1
    fi
    
    IFS=':' read -r company_name schema_name frontend_port backend_port <<< "$company_info"
    
    print_info "Stopping services for $company_name ($company_code)..."
    
    stop_service "${company_code}_backend" $backend_port
}

# Function to start all companies
start_all_companies() {
    print_info "Starting all company services..."
    
    # Start database first
    start_service "database" "$DATABASE_DIR" "python setup_db.py" 5432
    
    # Start notification engine
    start_service "notification-engine" "$ENGINE_DIR" \
        "bash -c 'source ../../.venv/bin/activate && python notification_system.py'" 5432
    
    # Start all company backends
    for company_code in $(get_all_companies); do
        start_company_services $company_code
    done
    
    print_success "All company services started!"
    show_status
}

# Function to stop all companies
stop_all_companies() {
    print_info "Stopping all company services..."
    
    for company_code in $(get_all_companies); do
        stop_company_services $company_code
    done
    
    stop_service "notification-engine" 5432
    stop_service "database" 5432
    
    print_success "All company services stopped!"
}

# Function to restart all companies
restart_all_companies() {
    print_info "Restarting all company services..."
    stop_all_companies
    sleep 3
    start_all_companies
}

# Function to show status of all services
show_status() {
    print_info "Multi-Tenant Service Status:"
    echo "=================================="
    
    # Database and notification engine
    if check_service "database" 5432; then
        print_success "Database: Running (port 5432)"
    else
        print_error "Database: Not running"
    fi
    
    if check_service "notification-engine" 5432; then
        print_success "Notification Engine: Running"
    else
        print_error "Notification Engine: Not running"
    fi
    
    echo ""
    
    # Company services
    for company_code in $(get_all_companies); do
        local company_info=$(get_company_info $company_code)
        IFS=':' read -r company_name schema_name frontend_port backend_port <<< "$company_info"
        
        if check_service "${company_code}_backend" $backend_port; then
            print_success "$company_name Backend: Running (port $backend_port)"
        else
            print_error "$company_name Backend: Not running"
        fi
    done
    
    echo ""
    print_info "Access Points:"
    for company_code in $(get_all_companies); do
        local company_info=$(get_company_info $company_code)
        IFS=':' read -r company_name schema_name frontend_port backend_port <<< "$company_info"
        echo "  $company_name: http://localhost:$frontend_port (Frontend) | http://localhost:$backend_port (Backend)"
    done
}

# Function to generate data for all companies
generate_all_data() {
    print_info "Generating data for all companies..."
    cd "$DATABASE_DIR"
    python multi_tenant_generator.py
    cd - > /dev/null
}

# Function to setup multi-tenant database
setup_multi_tenant_db() {
    print_info "Setting up multi-tenant database..."
    cd "$DATABASE_DIR"
    python -c "
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'notify_postgres'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '')
)

cursor = conn.cursor()

# Read and execute multi-tenant schema
with open('multi_tenant_schema.sql', 'r') as f:
    schema_sql = f.read()

cursor.execute(schema_sql)
conn.commit()

print('✅ Multi-tenant database schema created successfully!')

cursor.close()
conn.close()
"
    cd - > /dev/null
}

# Main script logic
case "$1" in
    start)
        case "$2" in
            comp_a|COMP_A)
                start_company_services "COMP_A"
                ;;
            comp_b|COMP_B)
                start_company_services "COMP_B"
                ;;
            comp_c|COMP_C)
                start_company_services "COMP_C"
                ;;
            all|"")
                start_all_companies
                ;;
            *)
                print_error "Unknown company: $2"
                print_info "Available companies: comp_a, comp_b, comp_c, all"
                exit 1
                ;;
        esac
        ;;
    stop)
        case "$2" in
            comp_a|COMP_A)
                stop_company_services "COMP_A"
                ;;
            comp_b|COMP_B)
                stop_company_services "COMP_B"
                ;;
            comp_c|COMP_C)
                stop_company_services "COMP_C"
                ;;
            all|"")
                stop_all_companies
                ;;
            *)
                print_error "Unknown company: $2"
                print_info "Available companies: comp_a, comp_b, comp_c, all"
                exit 1
                ;;
        esac
        ;;
    restart)
        case "$2" in
            comp_a|COMP_A)
                restart_service "COMP_A_backend" "$BACKEND_DIR" \
                    "./start_comp_a.sh" \
                    5001
                ;;
            comp_b|COMP_B)
                restart_service "COMP_B_backend" "$BACKEND_DIR" \
                    "./start_comp_b.sh" \
                    5002
                ;;
            comp_c|COMP_C)
                restart_service "COMP_C_backend" "$BACKEND_DIR" \
                    "./start_comp_c.sh" \
                    5003
                ;;
            all|"")
                restart_all_companies
                ;;
            *)
                print_error "Unknown company: $2"
                print_info "Available companies: comp_a, comp_b, comp_c, all"
                exit 1
                ;;
        esac
        ;;
    status)
        show_status
        ;;
    setup)
        setup_multi_tenant_db
        ;;
    generate)
        generate_all_data
        ;;
    *)
        echo "🏢 Multi-Tenant PostgreSQL Notification System"
        echo "=============================================="
        echo ""
        echo "Usage: $0 {start|stop|restart|status|setup|generate} [company]"
        echo ""
        echo "Commands:"
        echo "  start [company]    - Start services for a company or all companies"
        echo "  stop [company]     - Stop services for a company or all companies"
        echo "  restart [company]  - Restart services for a company or all companies"
        echo "  status             - Show status of all services"
        echo "  setup              - Setup multi-tenant database schema"
        echo "  generate           - Generate test data for all companies"
        echo ""
        echo "Companies:"
        echo "  comp_a, comp_b, comp_c, all"
        echo ""
        echo "Examples:"
        echo "  $0 start all              # Start all company services"
        echo "  $0 start comp_a           # Start Company A services only"
        echo "  $0 status                 # Show status of all services"
        echo "  $0 setup                  # Setup multi-tenant database"
        echo "  $0 generate               # Generate test data"
        exit 1
        ;;
esac
