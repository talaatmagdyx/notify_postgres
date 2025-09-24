# PostgreSQL Notification System

A complete real-time notification system using PostgreSQL LISTEN/NOTIFY with a service-oriented architecture.

## 🏗️ Service Architecture

```
notify_postgres/
├── 📁 services/                    # Service-oriented architecture
│   ├── 📁 backend/                 # Flask API Service
│   │   ├── app.py                  # Main Flask application
│   │   ├── requirements.txt        # Backend dependencies
│   │   ├── config.ini              # Service configuration
│   │   └── Dockerfile              # Container configuration
│   ├── 📁 frontend/                # React Frontend Service
│   │   ├── src/                    # React source code
│   │   ├── public/                 # Static files
│   │   ├── package.json            # Frontend dependencies
│   │   ├── config.ini              # Service configuration
│   │   └── Dockerfile              # Container configuration
│   ├── 📁 notification-engine/      # Notification Engine Service
│   │   ├── notification_system.py  # Core notification system
│   │   ├── config.ini              # Service configuration
│   │   └── Dockerfile              # Container configuration
│   ├── 📁 database/                # Database Service
│   │   ├── schema.sql              # Database schema
│   │   └── config.ini              # Service configuration
│   └── service-manager.sh          # Service management script
├── 📁 scripts/                     # Utility Scripts
├── 📁 tests/                       # Test Files
├── 📁 docs/                        # Documentation
├── 📄 docker-compose.yml           # Docker orchestration
├── 📄 Makefile                     # Easy command shortcuts
└── 📄 README.md                    # This file
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Start all services with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Option 2: Service Manager
```bash
# Start all services
./services/service-manager.sh start all

# Start specific service
./services/service-manager.sh start backend

# Check status
./services/service-manager.sh status

# Stop all services
./services/service-manager.sh stop all
```

### Option 3: Manual Start
```bash
# Setup database
make setup

# Start services individually
make backend
make frontend
```

## 🎯 Services

### 🔧 Backend Service
- **Port**: 5001
- **Type**: Flask API + WebSocket
- **Features**: REST API, real-time notifications
- **Start**: `./services/service-manager.sh start backend`

### 📱 Frontend Service
- **Port**: 3000
- **Type**: React Web App
- **Features**: WhatsApp-like interface, real-time updates
- **Start**: `./services/service-manager.sh start frontend`

### ⚡ Notification Engine
- **Type**: Background Service
- **Features**: PostgreSQL LISTEN/NOTIFY processing
- **Start**: `./services/service-manager.sh start engine`

### 🗄️ Database Service
- **Port**: 5432
- **Type**: PostgreSQL Database
- **Features**: Schema management, triggers, notifications
- **Start**: `./services/service-manager.sh start database`

## 📊 Service Management

### Service Commands
```bash
# Start services
./services/service-manager.sh start [service]
./services/service-manager.sh start all
./services/service-manager.sh start backend
./services/service-manager.sh start frontend

# Stop services
./services/service-manager.sh stop [service]
./services/service-manager.sh stop all

# Restart services
./services/service-manager.sh restart [service]
./services/service-manager.sh restart all

# Check status
./services/service-manager.sh status
```

### Docker Commands
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild services
docker-compose build --no-cache
```

## 🔧 Configuration

Each service has its own configuration file:
- `services/backend/config.ini` - Backend service config
- `services/frontend/config.ini` - Frontend service config
- `services/notification-engine/config.ini` - Engine config
- `services/database/config.ini` - Database config

## 📱 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Database**: localhost:5432

## 🎉 Features

- ✅ Service-oriented architecture
- ✅ Docker containerization
- ✅ Real-time PostgreSQL notifications
- ✅ WhatsApp-like React interface
- ✅ WebSocket connections
- ✅ Service management tools
- ✅ Health checks and monitoring
- ✅ Scalable and maintainable

## 🚀 Development

### Local Development
```bash
# Start services individually
./services/service-manager.sh start backend
./services/service-manager.sh start frontend
```

### Production Deployment
```bash
# Use Docker Compose
docker-compose up -d
```

### Service Monitoring
```bash
# Check service status
./services/service-manager.sh status

# View service logs
docker-compose logs -f [service]
```

Your PostgreSQL notification system is now organized with a professional service-oriented architecture! 🚀