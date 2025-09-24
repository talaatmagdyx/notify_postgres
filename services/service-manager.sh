#!/bin/bash

# Service Management Script for PostgreSQL Notification System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service directories
SERVICES_DIR="services"
BACKEND_DIR="$SERVICES_DIR/backend"
FRONTEND_DIR="$SERVICES_DIR/frontend"
ENGINE_DIR="$SERVICES_DIR/notification-engine"
DATABASE_DIR="$SERVICES_DIR/database"

# Function to print colored output
print_status() {
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

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if lsof -i :$port > /dev/null 2>&1; then
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
    
    print_status "Starting $service_name service..."
    
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
    
    print_status "Stopping $service_name service..."
    
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
    
    stop_service $service_name $port
    sleep 2
    start_service $service_name $service_dir $start_command $port
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    echo "=================="
    
    if check_service "database" 5432; then
        print_success "Database: Running (port 5432)"
    else
        print_error "Database: Not running"
    fi
    
    if check_service "backend" 5001; then
        print_success "Backend: Running (port 5001)"
    else
        print_error "Backend: Not running"
    fi
    
    if check_service "frontend" 3000; then
        print_success "Frontend: Running (port 3000)"
    else
        print_error "Frontend: Not running"
    fi
    
    if check_service "notification-engine" 5432; then
        print_success "Notification Engine: Running"
    else
        print_error "Notification Engine: Not running"
    fi
}

# Function to start all services
start_all() {
    print_status "Starting all services..."
    
    # Start database
    start_service "database" "$DATABASE_DIR" "python setup_db.py" 5432
    
    # Start backend
    start_service "backend" "$BACKEND_DIR" "./start.sh" 5001
    
    # Start frontend
    start_service "frontend" "$FRONTEND_DIR" "npm start" 3000
    
    # Start notification engine
    start_service "notification-engine" "$ENGINE_DIR" "bash -c 'source ../../.venv/bin/activate && python notification_system.py'" 5432
    
    print_success "All services started!"
    show_status
}

# Function to stop all services
stop_all() {
    print_status "Stopping all services..."
    
    stop_service "frontend" 3000
    stop_service "backend" 5001
    stop_service "notification-engine" 5432
    stop_service "database" 5432
    
    print_success "All services stopped!"
}

# Function to restart all services
restart_all() {
    print_status "Restarting all services..."
    stop_all
    sleep 3
    start_all
}

# Main script logic
case "$1" in
    start)
        case "$2" in
            backend)
                start_service "backend" "$BACKEND_DIR" "./start.sh" 5001
                ;;
            frontend)
                start_service "frontend" "$FRONTEND_DIR" "npm start" 3000
                ;;
            engine)
                start_service "notification-engine" "$ENGINE_DIR" "bash -c 'source ../../.venv/bin/activate && python notification_system.py'" 5432
                ;;
            database)
                start_service "database" "$DATABASE_DIR" "python setup_db.py" 5432
                ;;
            all|"")
                start_all
                ;;
            *)
                print_error "Unknown service: $2"
                exit 1
                ;;
        esac
        ;;
    stop)
        case "$2" in
            backend)
                stop_service "backend" 5001
                ;;
            frontend)
                stop_service "frontend" 3000
                ;;
            engine)
                stop_service "notification-engine" 5432
                ;;
            database)
                stop_service "database" 5432
                ;;
            all|"")
                stop_all
                ;;
            *)
                print_error "Unknown service: $2"
                exit 1
                ;;
        esac
        ;;
    restart)
        case "$2" in
            backend)
                restart_service "backend" "$BACKEND_DIR" "./start.sh" 5001
                ;;
            frontend)
                restart_service "frontend" "$FRONTEND_DIR" "npm start" 3000
                ;;
            engine)
                restart_service "notification-engine" "$ENGINE_DIR" "bash -c 'source ../../.venv/bin/activate && python notification_system.py'" 5432
                ;;
            database)
                restart_service "database" "$DATABASE_DIR" "python setup_db.py" 5432
                ;;
            all|"")
                restart_all
                ;;
            *)
                print_error "Unknown service: $2"
                exit 1
                ;;
        esac
        ;;
    status)
        show_status
        ;;
    *)
        echo "PostgreSQL Notification System - Service Manager"
        echo "================================================"
        echo ""
        echo "Usage: $0 {start|stop|restart|status} [service]"
        echo ""
        echo "Services:"
        echo "  backend     - Flask API backend"
        echo "  frontend    - React frontend"
        echo "  engine      - Notification engine"
        echo "  database    - Database service"
        echo "  all         - All services (default)"
        echo ""
        echo "Examples:"
        echo "  $0 start all          # Start all services"
        echo "  $0 start backend      # Start only backend"
        echo "  $0 stop frontend      # Stop only frontend"
        echo "  $0 restart all        # Restart all services"
        echo "  $0 status             # Show service status"
        exit 1
        ;;
esac
