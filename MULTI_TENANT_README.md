# Multi-Tenant PostgreSQL Notification System

A comprehensive multi-tenant notification system supporting multiple companies with separate schemas, frontends, and backends.

## 🏢 Architecture Overview

This system supports **3 companies** with complete isolation:

| Company | Schema | Frontend Port | Backend Port | Theme Color |
|---------|--------|---------------|--------------|-------------|
| **Company Alpha** | `company_a` | 3001 | 5001 | WhatsApp Green (#25D366) |
| **Company Beta** | `company_b` | 3002 | 5002 | Twitter Blue (#1DA1F2) |
| **Company Gamma** | `company_c` | 3003 | 5003 | Facebook Blue (#4267B2) |

## 🚀 Quick Start

### 1. Setup Multi-Tenant Database
```bash
./services/multi_tenant_manager.sh setup
```

### 2. Start All Company Services
```bash
./services/multi_tenant_manager.sh start all
```

### 3. Generate Test Data
```bash
./services/multi_tenant_manager.sh generate
```

### 4. Access Frontends
- **Company Alpha**: http://localhost:3001
- **Company Beta**: http://localhost:3002  
- **Company Gamma**: http://localhost:3003

## 📊 Database Schema

### Multi-Tenant Structure
```
notify_postgres/
├── companies (shared metadata)
├── company_a/
│   ├── eng_interactions
│   ├── company_settings
│   ├── users
│   └── analytics
├── company_b/
│   ├── eng_interactions
│   ├── company_settings
│   ├── users
│   └── analytics
└── company_c/
    ├── eng_interactions
    ├── company_settings
    ├── users
    └── analytics
```

### Company-Specific Tables

Each company schema includes:

1. **`eng_interactions`** - Main engagement table with partitions
2. **`company_settings`** - Company-specific configuration
3. **`users`** - Company users and agents
4. **`analytics`** - Company metrics and KPIs

## 🔧 Service Management

### Start Services
```bash
# Start all companies
./services/multi_tenant_manager.sh start all

# Start specific company
./services/multi_tenant_manager.sh start comp_a
./services/multi_tenant_manager.sh start comp_b
./services/multi_tenant_manager.sh start comp_c
```

### Stop Services
```bash
# Stop all companies
./services/multi_tenant_manager.sh stop all

# Stop specific company
./services/multi_tenant_manager.sh stop comp_a
```

### Check Status
```bash
./services/multi_tenant_manager.sh status
```

### Restart Services
```bash
# Restart all companies
./services/multi_tenant_manager.sh restart all

# Restart specific company
./services/multi_tenant_manager.sh restart comp_a
```

## 📱 Frontend Configuration

Each company has its own frontend configuration:

### Company Alpha (COMP_A)
- **File**: `services/frontend/src/App_CompanyA.tsx`
- **Port**: 3001
- **Backend**: http://localhost:5001
- **Theme**: WhatsApp Green
- **Channels**: WhatsApp, Email

### Company Beta (COMP_B)
- **File**: `services/frontend/src/App_CompanyB.tsx`
- **Port**: 3002
- **Backend**: http://localhost:5002
- **Theme**: Twitter Blue
- **Channels**: Twitter, Facebook

### Company Gamma (COMP_C)
- **File**: `services/frontend/src/App_CompanyC.tsx`
- **Port**: 3003
- **Backend**: http://localhost:5003
- **Theme**: Facebook Blue
- **Channels**: All (WhatsApp, Twitter, Facebook, Email)

## 🔄 Data Generation

### Generate Data for All Companies
```bash
./services/multi_tenant_manager.sh generate
```

### Manual Data Generation
```bash
cd services/database
python multi_tenant_generator.py
```

### Data Generation Options
1. Generate data for all companies (20 interactions each)
2. Generate data for Company A only
3. Generate data for Company B only
4. Generate data for Company C only
5. Generate large dataset for all companies (50 interactions each)

## 🌐 API Endpoints

Each company backend provides:

### Engagement Management
- `GET /api/engagements` - List all engagements
- `POST /api/engagements` - Create new engagement
- `PUT /api/engagements/{id}` - Update engagement status

### Company Information
- `GET /api/company/info` - Get company configuration
- `GET /api/analytics` - Get company analytics

### WebSocket Events
- `new_engagement` - Real-time new engagement notifications
- `status_update` - Real-time status change notifications

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=notify_postgres
DB_USER=postgres
DB_PASSWORD=your_password

# Company Configuration (set per backend instance)
COMPANY_CODE=COMP_A  # or COMP_B, COMP_C
BACKEND_PORT=5001    # or 5002, 5003
```

### Company-Specific Settings
Each company can have different:
- **Channels**: WhatsApp, Twitter, Facebook, Email
- **User prefixes**: Different naming conventions
- **Themes**: Brand-specific colors
- **Ports**: Separate frontend/backend ports

## 📈 Analytics & Monitoring

### Company Analytics
Each company schema includes analytics tables with:
- Daily engagement metrics
- Channel performance
- Response time tracking
- Customer satisfaction scores

### Real-Time Monitoring
- WebSocket notifications per company
- Company-specific notification channels
- Isolated data streams

## 🐳 Docker Support

### Multi-Tenant Docker Compose
```yaml
version: '3.8'
services:
  database:
    image: postgres:15
    environment:
      POSTGRES_DB: notify_postgres
    ports:
      - "5432:5432"
  
  backend-comp-a:
    build: ./services/backend
    environment:
      COMPANY_CODE: COMP_A
      BACKEND_PORT: 5001
    ports:
      - "5001:5001"
  
  backend-comp-b:
    build: ./services/backend
    environment:
      COMPANY_CODE: COMP_B
      BACKEND_PORT: 5002
    ports:
      - "5002:5002"
  
  backend-comp-c:
    build: ./services/backend
    environment:
      COMPANY_CODE: COMP_C
      BACKEND_PORT: 5003
    ports:
      - "5003:5003"
```

## 🔒 Security & Isolation

### Data Isolation
- **Schema-level isolation**: Each company has separate schema
- **Port isolation**: Separate backend ports per company
- **Notification isolation**: Company-specific notification channels

### Access Control
- Company-specific user tables
- Schema-based permissions
- Isolated API endpoints

## 🚀 Deployment

### Production Deployment
1. **Database Setup**: Create multi-tenant schemas
2. **Backend Deployment**: Deploy company-specific backends
3. **Frontend Deployment**: Deploy company-specific frontends
4. **Load Balancing**: Configure company-specific routing
5. **Monitoring**: Set up company-specific monitoring

### Scaling
- **Horizontal scaling**: Add more companies easily
- **Vertical scaling**: Scale individual company services
- **Database partitioning**: Company-based partitioning

## 📝 Development

### Adding New Companies
1. Add company configuration to `multi_tenant_manager.sh`
2. Create new schema using `create_company_schema()` function
3. Add company-specific frontend component
4. Update service manager configurations

### Customization
- **Company themes**: Modify frontend color schemes
- **Channel support**: Add/remove channels per company
- **Analytics**: Customize metrics per company
- **Notifications**: Company-specific notification rules

## 🐛 Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure unique ports per company
2. **Schema errors**: Run setup command to create schemas
3. **Connection issues**: Check database credentials
4. **Frontend not loading**: Verify backend is running

### Debug Commands
```bash
# Check service status
./services/multi_tenant_manager.sh status

# View logs
tail -f /tmp/COMP_A_backend.log
tail -f /tmp/COMP_B_backend.log
tail -f /tmp/COMP_C_backend.log

# Test database connection
psql -h localhost -p 5432 -U postgres -d notify_postgres
```

## 📚 Additional Resources

- [Single-Tenant Setup Guide](README.md)
- [API Documentation](docs/API.md)
- [Database Schema Reference](docs/Database.md)
- [Frontend Development Guide](docs/Frontend.md)

---

**Multi-Tenant PostgreSQL Notification System** - Supporting multiple companies with complete data isolation and real-time notifications.
