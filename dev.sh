#!/bin/bash

# JobBoard Development Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Commands
case "${1:-help}" in
    setup)
        print_header "Setting up JobBoard Development Environment"
        
        # Create virtual environment
        print_info "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        print_success "Virtual environment created"
        
        # Install dependencies
        print_info "Installing dependencies..."
        pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt
        print_success "Dependencies installed"
        
        # Setup environment
        print_info "Setting up environment variables..."
        if [ ! -f .env ]; then
            cp .env.example .env
            print_success "Created .env file"
        fi
        
        # Setup Tailwind
        print_info "Setting up Tailwind CSS..."
        npm install
        npm run build:css
        print_success "Tailwind CSS configured"
        
        # Run migrations
        print_info "Running migrations..."
        python manage.py migrate
        print_success "Database migrations completed"
        
        # Create initial data
        print_info "Creating initial job categories..."
        python manage.py shell << EOF
from jobs.models import JobCategory
categories = [
    JobCategory(name='Backend', slug='backend'),
    JobCategory(name='Frontend', slug='frontend'),
    JobCategory(name='Full Stack', slug='full-stack'),
    JobCategory(name='Mobile', slug='mobile'),
    JobCategory(name='DevOps', slug='devops'),
    JobCategory(name='Data Science', slug='data-science'),
]
JobCategory.objects.bulk_create(categories, ignore_conflicts=True)
print("Categories created successfully!")
EOF
        print_success "Setup completed!"
        ;;
    
    run)
        print_header "Starting JobBoard Development Server"
        
        # Activate venv
        source venv/bin/activate 2>/dev/null || true
        
        # Start Tailwind watcher
        print_info "Starting Tailwind CSS watcher..."
        npm run watch:css &
        TAILWIND_PID=$!
        
        # Start Django server
        print_info "Starting Django development server..."
        python manage.py runserver 0.0.0.0:8000
        ;;
    
    test)
        print_header "Running Tests"
        
        source venv/bin/activate 2>/dev/null || true
        
        if [ -z "$2" ]; then
            pytest --cov=. --cov-report=html
            print_success "All tests passed! Coverage report: htmlcov/index.html"
        else
            pytest "$2" -v
        fi
        ;;
    
    migrate)
        print_header "Database Migration"
        
        source venv/bin/activate 2>/dev/null || true
        
        if [ -z "$2" ]; then
            python manage.py migrate
        else
            python manage.py migrate "$2"
        fi
        print_success "Migration completed"
        ;;
    
    makemigrations)
        print_header "Create Migrations"
        
        source venv/bin/activate 2>/dev/null || true
        python manage.py makemigrations
        print_success "Migrations created"
        ;;
    
    shell)
        print_header "Django Shell"
        
        source venv/bin/activate 2>/dev/null || true
        python manage.py shell
        ;;
    
    admin)
        print_header "Create Superuser"
        
        source venv/bin/activate 2>/dev/null || true
        python manage.py createsuperuser
        print_success "Superuser created"
        ;;
    
    static)
        print_header "Collecting Static Files"
        
        source venv/bin/activate 2>/dev/null || true
        python manage.py collectstatic --noinput
        print_success "Static files collected"
        ;;
    
    clean)
        print_header "Cleaning Up"
        
        print_info "Removing cache files..."
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name '*.pyc' -delete
        find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
        
        print_info "Removing build artifacts..."
        rm -rf build/ dist/ *.egg-info/
        
        print_success "Cleanup completed"
        ;;
    
    docker-build)
        print_header "Building Docker Image"
        
        docker build -t jobboard:latest .
        print_success "Docker image built"
        ;;
    
    docker-up)
        print_header "Starting Docker Compose"
        
        docker-compose up -d
        print_success "Services started"
        print_info "Access application at: http://localhost"
        ;;
    
    docker-down)
        print_header "Stopping Docker Compose"
        
        docker-compose down
        print_success "Services stopped"
        ;;
    
    docker-logs)
        print_header "Docker Logs"
        
        docker-compose logs -f "${2:-web}"
        ;;
    
    lint)
        print_header "Linting Code"
        
        source venv/bin/activate 2>/dev/null || true
        
        # If flake8 is not installed, try to run with available tools
        if command -v flake8 &> /dev/null; then
            flake8 . --max-line-length=120 --exclude=venv,migrations
        else
            print_info "flake8 not installed. Install with: pip install flake8"
        fi
        ;;
    
    format)
        print_header "Formatting Code"
        
        source venv/bin/activate 2>/dev/null || true
        
        # If black is installed, use it
        if command -v black &> /dev/null; then
            black . --exclude=venv
            print_success "Code formatted with black"
        else
            print_info "black not installed. Install with: pip install black"
        fi
        ;;
    
    help|*)
        cat << EOF
${BLUE}JobBoard Development Helper${NC}

${YELLOW}Usage:${NC} ./dev.sh <command> [options]

${YELLOW}Development Commands:${NC}
  setup              Setup development environment (first time)
  run                Start development server with Tailwind watcher
  test [file]        Run tests (optionally specific file)
  migrate [app]      Run database migrations
  makemigrations     Create new migrations
  shell              Open Django shell
  admin              Create superuser
  static             Collect static files
  clean              Clean cache and build artifacts
  
${YELLOW}Docker Commands:${NC}
  docker-build       Build Docker image
  docker-up          Start all services with Docker Compose
  docker-down        Stop all services
  docker-logs [service]  View service logs
  
${YELLOW}Code Quality:${NC}
  lint               Run linting checks
  format             Format code with black

${YELLOW}Examples:${NC}
  ./dev.sh setup           # Initial setup
  ./dev.sh run             # Start development server
  ./dev.sh test            # Run all tests
  ./dev.sh test tests/test_users.py  # Run specific tests
  ./dev.sh docker-up       # Start Docker stack
  
${YELLOW}Common Workflows:${NC}
  1. First time:    ./dev.sh setup
  2. Then:          ./dev.sh run
  3. In another terminal: ./dev.sh test

${BLUE}For more help, see README.md or QUICKSTART.md${NC}
EOF
        ;;
esac
