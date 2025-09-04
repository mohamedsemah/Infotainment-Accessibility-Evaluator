# Infotainment Accessibility Evaluator Makefile

.PHONY: help dev test build up down clean install-frontend install-backend

# Default target
help:
	@echo "Infotainment Accessibility Evaluator"
	@echo "===================================="
	@echo ""
	@echo "Available targets:"
	@echo "  dev              - Run development environment (backend + frontend)"
	@echo "  test             - Run all tests"
	@echo "  build            - Build all Docker images"
	@echo "  up               - Start Docker containers"
	@echo "  down             - Stop Docker containers"
	@echo "  clean            - Clean up containers and images"
	@echo "  install-frontend - Install frontend dependencies"
	@echo "  install-backend  - Install backend dependencies"
	@echo "  lint             - Run linting"
	@echo "  format           - Format code"
	@echo ""

# Development environment
dev:
	@echo "Starting development environment..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo ""
	@echo "Make sure to copy env.example to .env and add your API keys!"
	@echo ""
	@if [ ! -f .env ]; then \
		echo "Warning: .env file not found. Copying from env.example..."; \
		cp env.example .env; \
		echo "Please edit .env and add your API keys before running 'make dev'"; \
		exit 1; \
	fi
	@echo "Starting backend and frontend in development mode..."
	@cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
	@cd frontend && npm run dev &
	@echo "Development servers started. Press Ctrl+C to stop."

# Testing
test:
	@echo "Running tests..."
	@cd backend && python -m pytest app/tests/ -v
	@echo "Tests completed."

# Build Docker images
build:
	@echo "Building Docker images..."
	@docker-compose build
	@echo "Build completed."

# Start containers
up:
	@echo "Starting containers..."
	@if [ ! -f .env ]; then \
		echo "Warning: .env file not found. Copying from env.example..."; \
		cp env.example .env; \
		echo "Please edit .env and add your API keys before running 'make up'"; \
	fi
	@docker-compose up -d
	@echo "Containers started."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"

# Stop containers
down:
	@echo "Stopping containers..."
	@docker-compose down
	@echo "Containers stopped."

# Clean up
clean:
	@echo "Cleaning up containers and images..."
	@docker-compose down -v --rmi all
	@docker system prune -f
	@echo "Cleanup completed."

# Install dependencies
install-frontend:
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "Frontend dependencies installed."

install-backend:
	@echo "Installing backend dependencies..."
	@cd backend && pip install -e .
	@echo "Backend dependencies installed."

# Install all dependencies
install: install-backend install-frontend
	@echo "All dependencies installed."

# Linting
lint:
	@echo "Running linting..."
	@cd backend && python -m flake8 app/ --max-line-length=88
	@cd backend && python -m mypy app/ --ignore-missing-imports
	@cd frontend && npm run lint
	@echo "Linting completed."

# Format code
format:
	@echo "Formatting code..."
	@cd backend && python -m black app/ --line-length=88
	@cd backend && python -m isort app/ --profile=black
	@cd frontend && npm run format
	@echo "Code formatting completed."

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/healthz && echo "Backend: OK" || echo "Backend: FAILED"
	@curl -f http://localhost:5173/ && echo "Frontend: OK" || echo "Frontend: FAILED"

# Development setup
setup: install
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from template. Please add your API keys."; \
	fi
	@echo "Development environment setup completed."
	@echo "Next steps:"
	@echo "1. Edit .env and add your API keys"
	@echo "2. Run 'make dev' to start development servers"

# Production deployment
deploy:
	@echo "Deploying to production..."
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production deployment completed."

# Logs
logs:
	@docker-compose logs -f

# Shell access
shell-backend:
	@docker-compose exec backend bash

shell-frontend:
	@docker-compose exec frontend sh
