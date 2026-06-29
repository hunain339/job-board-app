# Supabase PostgreSQL Production Setup Guide

## ✓ Current Status
Your Django app is successfully connected to Supabase PostgreSQL!

- **Database**: Supabase PostgreSQL (aws-1-ap-northeast-2.pooler.supabase.com)
- **Status**: Connected ✓
- **Migrations**: All applied ✓
- **Tables**: 20 tables created ✓

## Configuration Summary

### 1. Database Configuration (✓ Already Set)
Your `.env` file has the Supabase credentials:
```
USE_POSTGRES=True
DB_NAME=postgres
DB_USER=postgres.eojtppurcfetsskhulla
DB_PASSWORD=ineddmysupabse
DB_HOST=aws-1-ap-northeast-2.pooler.supabase.com
DB_PORT=6543
DB_SSLMODE=require
```

The `settings.py` reads these via the `decouple` library and configures Django to use PostgreSQL.

### 2. Production Security Checklist

**Environment Variables to Update for Production:**
```env
# SECURITY - MUST CHANGE THESE
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here-min-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS - only allow your frontend
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Database (Supabase)
DB_SSLMODE=require
```

### 3. Django Settings That Handle Production

Your `settings.py` already includes production-ready configuration:

- **Database**: Uses `DATABASE_URL` or `USE_POSTGRES` + individual DB_* vars
- **SSL Mode**: `sslmode=require` for Supabase (already in .env)
- **Static Files**: Configured with `STATIC_ROOT` for production collection
- **Media Files**: Configured with `MEDIA_ROOT` 
- **CORS**: Configurable via env variables
- **JWT**: Token-based authentication configured
- **HTTPS**: Security headers configurable via env

### 4. Next Steps for Production Deployment

**1. Generate a Strong Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**2. Update `.env` for production:**
- Change `DEBUG=False`
- Set a strong `SECRET_KEY`
- Set correct `ALLOWED_HOSTS`
- Enable HTTPS settings
- Configure `CORS_ALLOWED_ORIGINS` to your frontend domain

**3. Run migrations (if deploying to new Supabase instance):**
```bash
python manage.py migrate --noinput
```

**4. Collect static files:**
```bash
python manage.py collectstatic --noinput
```

**5. Test in production-like environment:**
```bash
DEBUG=False python manage.py runserver
```

### 5. Supabase-Specific Features Available

Your Supabase PostgreSQL includes:

- **Row Level Security (RLS)**: Control who can access which rows
- **Realtime**: WebSocket support for real-time data updates
- **Auth**: Built-in user authentication (optional)
- **Storage**: File storage for user uploads
- **Edge Functions**: Serverless functions
- **Database Backups**: Automatic daily backups

Currently, you're using Supabase as a PostgreSQL database only, which is perfect for your Django app.

### 6. Monitoring & Maintenance

**Check database usage:**
Visit Supabase dashboard → Database → Stats

**Backup status:**
Supabase automatically backs up your database daily.

**Connection pooling:**
Your connection string uses the pooler (port 6543) which handles connection pooling automatically.

## Troubleshooting

### Connection Issues
- Ensure `DB_SSLMODE=require` is set
- Check IP whitelist in Supabase (if applicable)
- Verify credentials in `.env`

### Migration Issues
```bash
# Check migration status
python manage.py showmigrations

# Rollback if needed
python manage.py migrate [app] [migration_name]
```

### Performance
- Monitor slow queries in Supabase dashboard
- Use Django query logging in development
- Consider caching frequently accessed data

## Resources

- [Django & Supabase Guide](https://supabase.com/docs/guides/getting-started/apps/django)
- [Supabase Database Documentation](https://supabase.com/docs/guides/database)
- [Django Security Documentation](https://docs.djangoproject.com/en/5.0/topics/security/)
