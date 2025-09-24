# PostgreSQL Notification System

A complete real-time notification system using PostgreSQL LISTEN/NOTIFY with a modern service-oriented architecture, multi-tenant support, and enhanced data generation.

## 🏗️ Service Architecture

```
notify_postgres/
├── 📁 services/                    # Service-oriented architecture
│   ├── 📁 backend/                 # Multi-tenant Flask API Service
│   │   ├── unified_app.py          # Unified multi-tenant backend
│   │   ├── multi_tenant_app.py     # Multi-tenant backend
│   │   ├── app.py                  # Legacy single-tenant backend
│   │   ├── start_comp_*.sh         # Company-specific startup scripts
│   │   ├── requirements.txt        # Backend dependencies
│   │   ├── config.ini              # Service configuration
│   │   └── Dockerfile              # Container configuration
│   ├── 📁 frontend/                # React Frontend Service
│   │   ├── src/                    # React source code
│   │   │   ├── App.tsx             # Main multi-tenant app
│   │   │   ├── App.css             # Modern glass-morphism styling
│   │   │   └── App_Company*.tsx    # Company-specific components
│   │   ├── public/                 # Static files
│   │   ├── package.json            # Frontend dependencies
│   │   ├── config.ini              # Service configuration
│   │   └── Dockerfile              # Container configuration
│   ├── 📁 notification-engine/      # Notification Engine Service
│   │   ├── unified_system.py       # Unified multi-tenant system
│   │   ├── multi_tenant_system.py  # Multi-tenant notification system
│   │   ├── notification_system.py  # Core notification system
│   │   ├── config.ini              # Service configuration
│   │   └── Dockerfile              # Container configuration
│   ├── 📁 database/                # Database Service
│   │   ├── multi_tenant_schema.sql # Multi-tenant database schema
│   │   ├── multi_tenant_generator.py # Enhanced Faker-based data generator
│   │   ├── schema.sql              # Single-tenant database schema
│   │   └── config.ini              # Service configuration
│   ├── multi_tenant_manager.sh     # Multi-tenant service management
│   └── service-manager.sh          # Service management script
├── 📁 scripts/                     # Utility Scripts
├── 📁 tests/                       # Test Files
├── 📁 docs/                        # Documentation
├── 📄 docker-compose.yml           # Docker orchestration
├── 📄 Makefile                     # Easy command shortcuts
├── 📄 MULTI_TENANT_README.md       # Multi-tenant documentation
└── 📄 README.md                    # This file
```

## 🚀 Quick Start

### Option 1: Multi-Tenant Setup (Recommended)
```bash
# Start multi-tenant services
make start-multi

# Generate realistic test data
make generate

# Access the unified frontend
open http://localhost:3000
```

### Option 2: Docker Compose
```bash
# Start all services with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Option 3: Service Manager
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

### Option 4: Manual Start
```bash
# Setup database
make setup

# Start services individually
make backend
make frontend
```

## 🎯 Services

### 🏢 Multi-Tenant Backend Services
- **TechFlow Solutions**: Port 5001 (Technology industry)
- **SocialMedia Pro**: Port 5002 (Social Media Marketing)
- **OmniChannel Corp**: Port 5003 (E-commerce)
- **Type**: Flask API + WebSocket
- **Features**: Multi-tenant REST API, real-time notifications, company-specific routing
- **Start**: `make start-multi` or `./services/multi_tenant_manager.sh start`

### 📱 Unified Frontend Service
- **Port**: 3000
- **Type**: React Web App with Multi-Tenant Support
- **Features**: 
  - Modern glass-morphism UI design
  - Company switching with dynamic themes
  - Real-time notifications with beautiful animations
  - Analytics dashboard with comprehensive metrics
  - WhatsApp-like interface for engagements
- **Start**: `./services/service-manager.sh start frontend`

### ⚡ Unified Notification Engine
- **Type**: Background Service
- **Features**: 
  - Multi-tenant PostgreSQL LISTEN/NOTIFY processing
  - Company-specific notification routing
  - Real-time WebSocket event distribution
  - Enhanced notification payloads
- **Start**: `./services/service-manager.sh start engine`

### 🗄️ Multi-Tenant Database Service
- **Port**: 5432
- **Type**: PostgreSQL Database with Multi-Tenant Schemas
- **Features**: 
  - Separate schemas for each company
  - Enhanced triggers and notification functions
  - Realistic test data generation with Faker
  - Comprehensive analytics tables
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

- **Unified Frontend**: http://localhost:3000 (Company switching interface)
- **TechFlow Solutions API**: http://localhost:5001
- **SocialMedia Pro API**: http://localhost:5002  
- **OmniChannel Corp API**: http://localhost:5003
- **Database**: localhost:5432

## 🎉 Features

### 🏗️ Architecture & Infrastructure
- ✅ Service-oriented architecture
- ✅ Multi-tenant support with separate schemas
- ✅ Docker containerization
- ✅ Unified notification system
- ✅ Service management tools
- ✅ Health checks and monitoring
- ✅ Scalable and maintainable

### 🎨 User Interface & Experience
- ✅ Modern glass-morphism UI design
- ✅ WhatsApp-like React interface
- ✅ Company switching with dynamic themes
- ✅ Real-time notifications with beautiful animations
- ✅ Analytics dashboard with comprehensive metrics
- ✅ Responsive design for all devices

### ⚡ Real-Time & Performance
- ✅ Real-time PostgreSQL notifications
- ✅ WebSocket connections with robust error handling
- ✅ Multi-tenant notification routing
- ✅ Enhanced notification payloads
- ✅ No artificial API limits (shows ALL data)
- ✅ Optimized database queries

### 📊 Data & Analytics
- ✅ Enhanced data generation with Faker
- ✅ Realistic test data across multiple industries
- ✅ Comprehensive analytics metrics
- ✅ Multi-locale support (US, GB, CA, AU)
- ✅ Rich metadata with location, device, browser info
- ✅ Intelligent data distribution patterns

## 🎭 Data Generation & Testing

### Enhanced Data Generation with Faker
```bash
# Generate realistic test data for all companies
make generate

# Generate data for specific companies
make generate-alpha    # TechFlow Solutions
make generate-beta     # SocialMedia Pro  
make generate-gamma    # OmniChannel Corp

# Generate large datasets
make generate-large
```

### Data Generation Features
- **Realistic User Data**: International phone numbers, emails, social media handles
- **Industry-Specific Content**: Technology, Social Media Marketing, E-commerce
- **Intelligent Distribution**: Recent bias, weekday patterns, status distribution
- **Rich Metadata**: Location, device, browser, customer tier information
- **Multi-Locale Support**: US, GB, CA, AU locales for diverse data

### Testing Commands
```bash
# Test the system
make test

# Check service status
make status

# View logs
make logs
```

## 🚀 Development

### Local Development
```bash
# Start multi-tenant services
make start-multi

# Generate test data
make generate

# Access unified frontend
open http://localhost:3000
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

## 📚 Documentation

- **[Multi-Tenant Setup](MULTI_TENANT_README.md)** - Detailed multi-tenant configuration
- **[Service Architecture](docs/README.md)** - Comprehensive system documentation
- **[API Documentation](docs/API.md)** - REST API endpoints and WebSocket events

Your PostgreSQL notification system now features a modern multi-tenant architecture with enhanced data generation and beautiful UI! 🚀