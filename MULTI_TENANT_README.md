# Multi-Tenant PostgreSQL Notification System

A comprehensive multi-tenant notification system with **unified frontend** and **enhanced data generation** supporting multiple companies with separate schemas and backends.

## 🏢 Architecture Overview

This system supports **3 companies** with **unified frontend** and **separate backends**:

| Company | Schema | Backend Port | Industry | Theme Color | Channels |
|---------|--------|--------------|----------|-------------|----------|
| **TechFlow Solutions** | `company_a` | 5001 | Technology | WhatsApp Green (#25D366) | WhatsApp, Email |
| **SocialMedia Pro** | `company_b` | 5002 | Social Media Marketing | Twitter Blue (#1DA1F2) | Twitter, Facebook |
| **OmniChannel Corp** | `company_c` | 5003 | E-commerce | Facebook Blue (#4267B2) | All Channels |

## 🚀 Quick Start

### 1. Setup Multi-Tenant Database
```bash
make setup
```

### 2. Start Multi-Tenant Services
```bash
make start-multi
```

### 3. Generate Realistic Test Data
```bash
make generate
```

### 4. Access Unified Frontend
- **Unified Frontend**: http://localhost:3000 (Company switching interface)

## 🎨 Unified Frontend Architecture

### Single Frontend with Company Switching
- **One React App**: Handles all companies dynamically
- **Company Switcher**: Easy switching between companies
- **Dynamic Themes**: Company-specific colors and branding
- **Real-time Updates**: Company-specific WebSocket connections
- **Analytics Dashboard**: Comprehensive metrics per company

### Frontend Features
- **Modern Glass-Morphism UI**: Beautiful, modern design
- **Real-time Notifications**: Animated notification system
- **Company-Specific Data**: Isolated data per company
- **Responsive Design**: Works on all devices
- **Analytics Integration**: Rich metrics and KPIs

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

## 📱 Unified Frontend Configuration

### Single React App with Dynamic Company Support
- **Main File**: `services/frontend/src/App.tsx`
- **Port**: 3000 (Unified)
- **Company Switching**: Dynamic routing and theming
- **Real-time Updates**: Company-specific WebSocket connections

### Company Configurations
- **TechFlow Solutions**: Backend 5001, WhatsApp Green theme, WhatsApp/Email channels
- **SocialMedia Pro**: Backend 5002, Twitter Blue theme, Twitter/Facebook channels  
- **OmniChannel Corp**: Backend 5003, Facebook Blue theme, All channels

### Frontend Features
- **Modern UI**: Glass-morphism design with beautiful animations
- **Company Switcher**: Easy switching between companies
- **Real-time Notifications**: Animated notification system
- **Analytics Dashboard**: Comprehensive metrics and KPIs
- **Responsive Design**: Works on all devices

## 🎭 Enhanced Data Generation with Faker

### Generate Realistic Test Data
```bash
# Generate data for all companies
make generate

# Generate data for specific companies
make generate-alpha    # TechFlow Solutions
make generate-beta     # SocialMedia Pro  
make generate-gamma    # OmniChannel Corp

# Generate large datasets
make generate-large
```

### Manual Data Generation
```bash
cd services/database
python multi_tenant_generator.py
```

### Data Generation Features
- **Realistic User Data**: International phone numbers, emails, social media handles
- **Industry-Specific Content**: Technology, Social Media Marketing, E-commerce
- **Intelligent Distribution**: Recent bias, weekday patterns, status distribution
- **Rich Metadata**: Location, device, browser, customer tier information
- **Multi-Locale Support**: US, GB, CA, AU locales for diverse data

### Data Generation Options
1. Generate data for all companies (20 interactions each)
2. Generate data for TechFlow Solutions only
3. Generate data for SocialMedia Pro only
4. Generate data for OmniChannel Corp only
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
