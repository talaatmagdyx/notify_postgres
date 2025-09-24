# PostgreSQL Notification System

A complete real-time notification system using PostgreSQL LISTEN/NOTIFY with a React frontend that displays engagements in a WhatsApp-like interface.

## 🚀 Quick Start

### 1. Setup Database
```bash
./scripts/setup_db.py
```

### 2. Start the System
```bash
./scripts/start.sh
```

### 3. Generate Sample Data
```bash
./scripts/generate.sh
```

## 📁 Project Structure

```
notify_postgres/
├── 📁 backend/                 # Flask API Backend
│   ├── app.py                 # Main Flask application
│   └── requirements.txt       # Backend dependencies
├── 📁 frontend/               # React Frontend
│   ├── src/                   # React source code
│   ├── public/                # Static files
│   └── package.json           # Frontend dependencies
├── 📁 scripts/                # Utility Scripts
│   ├── setup_db.py           # Database setup
│   ├── start.sh              # Start system
│   ├── generate.sh           # Data generation menu
│   ├── quick_generate.py     # Quick data generator
│   ├── generate_data.py      # Full data generator
│   └── reset_data.py         # Clear and regenerate data
├── 📁 tests/                 # Test Files
│   └── test.py               # Basic notification test
├── 📁 docs/                  # Documentation
│   └── README.md             # This file
├── 📄 .env                   # Environment variables
├── 📄 .gitignore             # Git ignore rules
├── 📄 requirements.txt       # Python dependencies
├── 📄 schema.sql             # Database schema
└── 📄 notification_system.py # Core notification system
```

## 🎯 Features

### Real-time Notifications
- ✅ PostgreSQL LISTEN/NOTIFY triggers
- ✅ WebSocket connections
- ✅ Live engagement updates
- ✅ Status change notifications

### React Frontend
- ✅ WhatsApp-like interface
- ✅ Real-time engagement list
- ✅ Live notification bar
- ✅ Status update buttons
- ✅ Channel selection (WhatsApp, Twitter, Facebook, Email)

### Backend API
- ✅ REST API endpoints
- ✅ WebSocket server
- ✅ PostgreSQL integration
- ✅ Real-time data streaming

## 🔧 API Endpoints

- `GET /api/engagements` - Get all engagements
- `POST /api/engagements` - Create new engagement
- `PUT /api/engagements/{id}/status` - Update engagement status

## 📊 Data Generation

### Quick Options
```bash
# Generate 20 sample interactions
./scripts/quick_generate.py

# Clear existing data and generate fresh
./scripts/reset_data.py

# Interactive data generator
./scripts/generate_data.py
```

### Data Generation Menu
```bash
./scripts/generate.sh
```

Options:
1. Quick generate (20 interactions)
2. Generate realistic scenario (20 interactions)
3. Generate large batch (50 interactions)
4. Generate WhatsApp only (15 interactions)
5. Generate Twitter only (10 interactions)
6. Clear data and generate fresh (20 interactions)
7. Interactive data generator
8. Exit

## 🎭 Sample Data

The system generates realistic interactions with:
- **WhatsApp**: Phone number users with support questions
- **Twitter**: Social media users with feedback and issues
- **Facebook**: Social media users with product inquiries
- **Email**: Business users with formal inquiries

## 🚀 Usage

1. **Setup**: `./scripts/setup_db.py`
2. **Start**: `./scripts/start.sh`
3. **Generate Data**: `./scripts/generate.sh`
4. **Open App**: http://localhost:3000
5. **API**: http://localhost:5001

## 🔧 Development

### Backend Development
```bash
cd backend
source ../.venv/bin/activate
python app.py
```

### Frontend Development
```bash
cd frontend
npm start
```

### Database Management
```bash
# Setup database
./scripts/setup_db.py

# Generate test data
./scripts/generate.sh
```

## 📱 Screenshots

The React app features:
- Real-time engagement list with channel icons
- Live notification sidebar
- Status update buttons
- WhatsApp-like interface design
- WebSocket connection status

## 🎉 Success!

Your PostgreSQL notification system is now complete with:
- ✅ Real-time notifications
- ✅ Beautiful React interface
- ✅ Comprehensive data generation
- ✅ Professional project structure

Enjoy your real-time PostgreSQL notification system! 🚀
