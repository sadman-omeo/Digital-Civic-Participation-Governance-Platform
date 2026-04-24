# ✅ PRE-DEPLOYMENT CHECKLIST

Complete this checklist before pushing to Vercel:

## 1. ✅ Code Changes (DONE)
- [x] Restructured project with `api/` directory
- [x] Created `api/index.py` as Vercel entry point
- [x] Updated `vercel.json` configuration
- [x] Updated `requirements.txt` with all dependencies
- [x] Added `config.py` for environment-based configuration
- [x] Updated `.gitignore` to exclude sensitive files
- [x] Created `DEPLOYMENT.md` documentation

## 2. 📋 Environment Variables Setup (YOU NEED TO DO THIS)

### Critical Variables - Set in Vercel Dashboard:

Go to your Vercel Project → Settings → Environment Variables

**Required for Production:**
```
SECRET_KEY               = Generate a strong random key (use: python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL            = Your PostgreSQL connection string (NOT SQLite)
FLASK_ENV               = production
```

**For Features:**
```
groq_api                = Your Groq API key (from groq.com)
RECAPTCHA_SITE_KEY      = From Google reCAPTCHA
RECAPTCHA_SECRET_KEY    = From Google reCAPTCHA
BREVO_API_KEY           = From Brevo email service
BREVO_SENDER_EMAIL      = Your sender email
BREVO_SENDER_NAME       = Your sender name
```

## 3. 🗄️ Database Setup (CRITICAL)

**SQLite WILL NOT WORK on Vercel!** Choose ONE:

### Option A: PostgreSQL (Recommended)
1. Create free PostgreSQL database at one of:
   - **Supabase** (https://supabase.com) - Free tier, no credit card needed
   - **Railway.app** (https://railway.app) - $5/month free tier
   - **Render** (https://render.com) - Free tier available
   - **Neon** (https://neon.tech) - Free tier with auto-sleep

2. Copy the connection string (looks like: `postgresql://user:password@host:port/dbname`)
3. Add as `DATABASE_URL` in Vercel environment variables

### Option B: For Testing Only (NOT RECOMMENDED)
- Data will be lost on every deployment
- Only for development/testing

## 4. 🚀 Before You Push

### Step 1: Remove .env from Git History
```bash
git rm --cached .env
git commit -m "Remove .env from version control"
```

### Step 2: Test Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python api/index.py
```

Should see: `Running on http://0.0.0.0:5000`

### Step 3: Commit All Changes
```bash
git add .
git commit -m "Configure for Vercel deployment"
git push origin main
```

## 5. 📤 Deploy to Vercel

1. Go to your Vercel Dashboard
2. Your project should auto-detect the push
3. Wait for build to complete
4. Check build logs if there are errors

## 6. 🔍 After Deployment

### Check Logs:
```
Vercel Dashboard → Your Project → Deployments → Latest → Logs
```

### Common Errors & Solutions:

**Error: "ModuleNotFoundError"**
- ✅ Solved: Imports configured correctly

**Error: "DATABASE_URL not set"**
- ✅ Solution: Add to Vercel environment variables

**Error: "psycopg2 not found"**
- ✅ Solved: Added to requirements.txt

**Error: "Port already in use"**
- ✅ Not an issue on Vercel (serverless)

## 7. ⚙️ Environment Variables Generation

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy output and paste into Vercel as `SECRET_KEY`

---

## Summary

- ✅ Code is ready
- ⏳ You need to:
  1. Set up PostgreSQL database (get connection string)
  2. Add environment variables to Vercel
  3. Push to GitHub
  4. Vercel will auto-deploy

**Ready to push?** Yes! ✅
