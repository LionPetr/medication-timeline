# Deployment Guide: Render + Vercel

## Prerequisites
- GitHub account
- Render account (free tier available)
- Vercel account (free tier available)
- Your code pushed to GitHub

---

## Part 1: Backend Deployment (Render)

### Step 1: Push to GitHub
```bash
cd c:\Git\medication-timeline
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/medication-timeline.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `medication-timeline-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn backend.wsgi:application`
   - **Instance Type**: Free

5. Add **Environment Variables**:
   - `SECRET_KEY`: Click "Generate" for a secure key
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com`
   - `CORS_ALLOWED_ORIGINS`: `https://your-frontend.vercel.app` (update after Vercel deployment)

6. Create a **PostgreSQL Database**:
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `medication-timeline-db`
   - Copy the **Internal Database URL**

7. Add to your web service environment variables:
   - `DATABASE_URL`: Paste the Internal Database URL

8. Click **"Create Web Service"**

### Step 3: Run Migrations
Once deployed, go to the **Shell** tab in Render and run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Update Frontend API URL

1. Create a `.env.production` file in the frontend folder:
```
REACT_APP_API_URL=https://your-backend-name.onrender.com
```

2. Update your `App.js` to use the environment variable:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

3. Commit and push these changes to GitHub.

### Step 2: Deploy on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

5. Add **Environment Variables**:
   - `REACT_APP_API_URL`: `https://your-backend-name.onrender.com`

6. Click **"Deploy"**

### Step 3: Update CORS Settings

1. Go back to Render
2. Update the `CORS_ALLOWED_ORIGINS` environment variable:
   - Value: `https://your-frontend-name.vercel.app`
3. Render will automatically redeploy

---

## Part 3: Final Testing

1. Visit your Vercel URL: `https://your-frontend-name.vercel.app`
2. The frontend should connect to the backend on Render
3. Test the timeline and undated medications features

---

## Troubleshooting

### Backend Issues:
- Check Render logs: Dashboard → Logs
- Verify environment variables are set correctly
- Ensure `build.sh` has execute permissions: `chmod +x build.sh`

### Frontend Issues:
- Check Vercel deployment logs
- Verify `REACT_APP_API_URL` points to correct backend URL
- Check browser console for CORS errors

### Database Issues:
- Verify `DATABASE_URL` is correctly set
- Run migrations in Render shell: `python manage.py migrate`

---

## Local Development After Deployment

Keep using:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

The `.env` files ensure local development works while production uses the deployed URLs.
