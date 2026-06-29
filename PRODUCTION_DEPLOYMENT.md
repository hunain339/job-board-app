# Production Deployment Checklist

## ✅ What's Already Done

- [x] Django app connected to Supabase PostgreSQL
- [x] All migrations applied to Supabase database
- [x] REST API configured with JWT authentication
- [x] CORS configured for frontend
- [x] Static files configured
- [x] User authentication system ready
- [x] Jobs and Applications apps ready

## 🔧 What Needs Configuration for Production

### 1. Environment Variables
Update your production `.env` file with:

```bash
# CRITICAL - MUST CHANGE THESE
DEBUG=False
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# Security Headers
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS - ONLY your frontend domain
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Database - Your current Supabase settings (keep these)
USE_POSTGRES=True
DB_NAME=postgres
DB_USER=postgres.eojtppurcfetsskhulla
DB_PASSWORD=ineddmysupabse
DB_HOST=aws-1-ap-northeast-2.pooler.supabase.com
DB_PORT=6543
DB_SSLMODE=require

# Email (configure for your SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 2. Generate Production Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and set it as `SECRET_KEY` in your production `.env`.

### 3. Collect Static Files (Run Once Before Deploy)

```bash
python manage.py collectstatic --noinput
```

This copies all static files (CSS, JS, images) to `staticfiles/` for serving.

### 4. Verify Everything Works

Run the production readiness check:

```bash
DEBUG=False python check_production_ready.py
```

Then test with:

```bash
DEBUG=False python manage.py runserver 0.0.0.0:8000
```

### 5. Database Backups

Your Supabase database has automatic daily backups.

To download a manual backup:
1. Go to Supabase Dashboard
2. Project Settings → Backups
3. Click "Download backup"

### 6. Monitoring

#### Monitor App Logs
```bash
# On your production server
tail -f /var/log/app.log
```

#### Monitor Database
- Visit Supabase Dashboard → Database → Logs
- Check slow queries
- Monitor storage usage

#### Health Check Endpoint (Optional)
Add this to your `urls.py` to monitor uptime:

```python
# jobs/urls.py or main urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})

urlpatterns = [
    # ... your urls
    path('health/', health_check),
]
```

### 7. Deployment Steps

**For Docker/Cloud Deployment:**

1. Build your Docker image with updated `settings.py`
2. Set environment variables in your hosting platform
3. Run migrations (if needed)
4. Collect static files
5. Start the application

**Example Docker command:**
```bash
docker run \
  -e DEBUG=False \
  -e SECRET_KEY="your-secret-key" \
  -e ALLOWED_HOSTS="yourdomain.com" \
  -e DB_HOST="aws-1-ap-northeast-2.pooler.supabase.com" \
  -e DB_USER="postgres.eojtppurcfetsskhulla" \
  -e DB_PASSWORD="ineddmysupabse" \
  -p 8000:8000 \
  job_board:latest
```

**For Traditional Server Deployment:**

```bash
# SSH into server
ssh your-server.com

# Pull latest code
cd /var/www/job_board
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations if needed
python manage.py migrate --noinput

# Restart application
sudo systemctl restart job_board
```

### 8. SSL/HTTPS Setup

If using a reverse proxy (Nginx):

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/job_board/staticfiles/;
    }

    location /media/ {
        alias /var/www/job_board/media/;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📋 Pre-Launch Checklist

- [ ] Change `DEBUG=False`
- [ ] Set a strong `SECRET_KEY`
- [ ] Set correct `ALLOWED_HOSTS`
- [ ] Configure `CORS_ALLOWED_ORIGINS` to your frontend
- [ ] Enable SSL/HTTPS (`SECURE_SSL_REDIRECT=True`)
- [ ] Set up email backend (Gmail, SendGrid, etc.)
- [ ] Test database connection
- [ ] Run `collectstatic --noinput`
- [ ] Run `python check_production_ready.py` and verify all checks pass
- [ ] Test API endpoints with correct credentials
- [ ] Set up monitoring and logging
- [ ] Test authentication flow (signup, login, token refresh)
- [ ] Verify CORS works with frontend
- [ ] Test file uploads (if applicable)
- [ ] Backup production secrets securely

## 🚀 Post-Launch Monitoring

- Monitor error logs
- Check database performance
- Verify automatic backups are working
- Monitor API response times
- Check storage quota usage
- Monitor user registration/login patterns

## 📞 Support Resources

- [Django Deployment Documentation](https://docs.djangoproject.com/en/5.0/howto/deployment/)
- [Supabase Database Guide](https://supabase.com/docs/guides/database)
- [Gunicorn Configuration](https://docs.gunicorn.org/)
- [Nginx Configuration](https://nginx.org/en/docs/)

---

**Status**: Your app is development-ready on Supabase PostgreSQL. 
Complete the above steps to launch to production.
