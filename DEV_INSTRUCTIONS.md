# Development Server Instructions

## Running the Development Server Locally

### Quick Start
```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations (if needed)
python manage.py migrate

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### Access the Application
- **Web Interface**: http://localhost:8000 (HTTP only)
- **Admin Panel**: http://localhost:8000/admin
- **API Endpoint**: http://localhost:8000/api

### Important
- **Always use HTTP** (not HTTPS) when accessing the development server
- `DEBUG=True` is set in `.env` for development
- SSL/HTTPS requirements are disabled in development mode
- Do NOT set `DEBUG=False` unless you're testing production settings

## Using Docker (Optional)
```bash
# Start services with Docker Compose
docker-compose up

# Access via: http://localhost:8000
```

## Environment Variables
The `.env` file contains development settings:
- `DEBUG=True` - Enables debug mode
- `SECURE_SSL_REDIRECT=False` - Disables HTTPS requirement
- `SESSION_COOKIE_SECURE=False` - Allows cookies over HTTP
- `CSRF_COOKIE_SECURE=False` - Allows CSRF cookies over HTTP

## Troubleshooting

### "ERROR: You're accessing the development server over HTTPS, but it only supports HTTP"
**Solution**: 
- Access via `http://` not `https://`
- Make sure `DEBUG=True` in `.env`
- Verify `.env` file exists with correct settings

### Database Errors
```bash
# Reset database and create superuser
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_jobs.py -v

# Run with coverage
pytest --cov=.
```
