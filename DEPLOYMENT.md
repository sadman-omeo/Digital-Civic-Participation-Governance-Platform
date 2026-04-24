# 🚀 Vercel Deployment Guide

**Status: ✅ READY FOR DEPLOYMENT**

This guide walks you through deploying your Digital Civic Participation Platform to Vercel.

## 📋 Quick Checklist

- [x] Code restructured for Vercel
- [x] Requirements updated with all dependencies
- [x] Configuration ready for production
- [ ] PostgreSQL database set up
- [ ] Environment variables added to Vercel
- [ ] Code pushed to GitHub

See [VERCEL_SETUP.md](VERCEL_SETUP.md) for detailed setup instructions.

---

## 🎯 Deployment Steps

### Step 1: Set Up Your Database

**⚠️ IMPORTANT: SQLite will NOT work on Vercel!**

Choose a PostgreSQL provider:

#### Option A: Supabase (Recommended - Free)
1. Go to https://supabase.com
2. Sign up (free tier - no credit card needed)
3. Create new project
4. Go to Project Settings → Database
5. Copy connection string (Standard URI format)
6. Example: `postgresql://user:password@db.xxx.supabase.co:5432/postgres`

#### Option B: Railway.app
1. Go to https://railway.app
2. Sign up
3. Create new PostgreSQL service
4. Copy connection string from Variables

#### Option C: Render.com
1. Go to https://render.com
2. Create PostgreSQL database
3. Copy Internal Database URL

### Step 2: Add Environment Variables to Vercel

1. Go to Vercel Dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add each variable below:

```
SECRET_KEY = [Generate with: python -c "import secrets; print(secrets.token_hex(32))"]
DATABASE_URL = [Your PostgreSQL connection string from Step 1]
FLASK_ENV = production
groq_api = [Your Groq API key]
RECAPTCHA_SITE_KEY = [Your reCAPTCHA site key]
RECAPTCHA_SECRET_KEY = [Your reCAPTCHA secret key]
BREVO_API_KEY = [Your Brevo API key]
BREVO_SENDER_EMAIL = [Your sender email]
BREVO_SENDER_NAME = [Your sender name]
```

### Step 3: Remove .env from Git

```bash
git rm --cached .env
git commit -m "Remove .env from version control"
```

### Step 4: Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run test script
python test_deployment.py

# Run Flask app
python api/index.py
```

Should see: `Running on http://0.0.0.0:5000`

### Step 5: Push to GitHub

```bash
git add .
git commit -m "Configure for Vercel deployment"
git push origin main
```

Vercel will automatically detect and deploy! 🚀

### Step 6: Monitor Deployment

1. Go to Vercel Dashboard
2. Check **Deployments** tab
3. Click latest deployment for logs
4. Wait for status to show ✅ READY

---

## 📂 Project Structure

```
project-root/
├── api/
│   ├── __init__.py
│   ├── index.py                    # ← Vercel runs this
│   ├── database_init.py
│   ├── brevo_email_helper.py
│   ├── recaptcha_helper.py
│   └── election_status_helper.py
├── models/                         # Database models
├── routes/                         # API blueprints
├── static/                         # CSS, JS, images
├── templates/                      # HTML templates
├── config.py                       # Configuration
├── database_init.py               # Database setup (root level)
├── vercel.json                    # Vercel config
├── requirements.txt               # Python dependencies
├── test_deployment.py             # Local test script
├── VERCEL_SETUP.md               # Setup checklist
├── DEPLOYMENT.md                 # This file
└── .env (git ignored)
```

---

## 🔧 Configuration Details

### Database
- **Local Development**: SQLite (`voting_system.db`)
- **Production (Vercel)**: PostgreSQL (via `DATABASE_URL`)
- Automatic detection based on `DATABASE_URL` environment variable

### Security
- `SECRET_KEY`: Change from default in production
- `SESSION_COOKIE_SECURE`: Enabled for HTTPS
- `SESSION_COOKIE_HTTPONLY`: Prevents JavaScript access

### Uploads
- **Max file size**: 16MB
- **Storage path**: `static/uploads/`
- ⚠️ **Not persistent on Vercel** - Consider S3 for production

---

## ❌ Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'xxx'"
**Solution:**
- Dependency missing from requirements.txt
- Check requirements.txt has all packages
- Run: `pip install -r requirements.txt`

### Issue: "DATABASE_URL not set"
**Solution:**
- Environment variables not added to Vercel
- Go to Vercel Settings → Environment Variables
- Restart deployment after adding variables

### Issue: "Connection refused / Database unavailable"
**Solution:**
- PostgreSQL URL incorrect
- Check connection string format: `postgresql://user:pass@host:port/dbname`
- Verify database is accessible from Vercel IPs

### Issue: "Secret Key has been changed, invalidating all sessions"
**Solution:**
- This is normal on first deployment
- Users will need to log in again
- Happens when `SECRET_KEY` environment variable changes

### Issue: "Deployment timeout"
**Solution:**
- Database migrations taking too long
- Reduce `db.create_all()` operations
- Pre-create tables if needed

---

## 📊 Monitoring

### View Logs
- Vercel Dashboard → Deployments → Select deployment → Logs
- Function logs show Flask requests
- Build logs show installation errors

### Useful Commands

Check deployment status:
```bash
vercel status
```

View environment variables:
```bash
vercel env list
```

---

## 🔄 Rollback

If deployment fails:
1. Vercel Dashboard → Deployments
2. Click failed deployment
3. Click "Rollback to previous"

---

## 🆘 Need Help?

1. Check [VERCEL_SETUP.md](VERCEL_SETUP.md) for detailed setup
2. Run `python test_deployment.py` to diagnose issues
3. Check Vercel deployment logs
4. Verify all environment variables are set

---

## ✅ Success!

Once deployed, you should see:
- Green checkmark ✅ in Vercel Deployments
- Website accessible at your Vercel domain
- All routes working
- Database connected and working
- Emails sending (if configured correctly)

---

**Last Updated:** April 25, 2026


