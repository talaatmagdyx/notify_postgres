# PostgreSQL Notification System - Makefile

.PHONY: help setup start start-multi generate generate-alpha generate-beta generate-gamma generate-large test clean install

help: ## Show this help message
	@echo "PostgreSQL Notification System"
	@echo "============================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "🔧 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "🔧 Installing backend dependencies..."
	cd services/backend && pip install -r requirements.txt
	@echo "🔧 Installing frontend dependencies..."
	cd services/frontend && npm install

setup: ## Setup database schema
	@echo "🔧 Setting up database..."
	cd services/database && python setup_db.py

start: ## Start all services
	@echo "🚀 Starting all services..."
	./services/service-manager.sh start all

start-multi: ## Start multi-tenant services
	@echo "🏢 Starting multi-tenant services..."
	./services/multi_tenant_manager.sh start

stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	./services/service-manager.sh stop all

restart: ## Restart all services
	@echo "🔄 Restarting all services..."
	./services/service-manager.sh restart all

docker-start: ## Start services with Docker Compose
	@echo "🐳 Starting services with Docker..."
	docker-compose up -d

docker-stop: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-logs: ## View Docker logs
	@echo "📋 Viewing Docker logs..."
	docker-compose logs -f

generate: ## Generate sample data for all companies
	@echo "📊 Generating sample data for all companies..."
	cd services/database && echo "1" | python multi_tenant_generator.py

generate-alpha: ## Generate data for Company Alpha only
	@echo "📊 Generating data for Company Alpha..."
	cd services/database && echo "2" | python multi_tenant_generator.py

generate-beta: ## Generate data for Company Beta only
	@echo "📊 Generating data for Company Beta..."
	cd services/database && echo "3" | python multi_tenant_generator.py

generate-gamma: ## Generate data for Company Gamma only
	@echo "📊 Generating data for Company Gamma..."
	cd services/database && echo "4" | python multi_tenant_generator.py

generate-large: ## Generate large dataset for all companies
	@echo "📊 Generating large dataset for all companies..."
	cd services/database && echo "5" | python multi_tenant_generator.py

test: ## Run basic notification test
	@echo "🧪 Running notification test..."
	python tests/test.py

backend: ## Start backend service only
	@echo "🔧 Starting backend service..."
	./services/service-manager.sh start backend

frontend: ## Start frontend service only
	@echo "📱 Starting frontend service..."
	./services/service-manager.sh start frontend

engine: ## Start notification engine only
	@echo "⚡ Starting notification engine..."
	./services/service-manager.sh start engine

database: ## Start database service only
	@echo "🗄️ Starting database service..."
	./services/service-manager.sh start database

clean: ## Clean generated files
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__/
	rm -rf services/frontend/node_modules/
	rm -rf services/frontend/build/
	rm -rf .venv/

reset: ## Reset database and generate fresh data
	@echo "🔄 Resetting database..."
	cd services/database && python reset_data.py

status: ## Check service status
	@echo "📊 Checking service status..."
	./services/service-manager.sh status

all: install setup generate ## Install, setup, and generate data
	@echo "🎉 Complete setup finished!"
	@echo "📱 Frontend: http://localhost:3000"
	@echo "🔧 Backend: http://localhost:5001"
