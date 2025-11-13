# 🚀 Step-by-Step Guide: Deploy Stock Assistant Web on Render

Complete guide to deploy your Stock Assistant Web application to Render's free hosting platform.

---

## 📋 Prerequisites

Before you start, make sure you have:

- ✅ GitHub account (free)
- ✅ Render account (free - we'll create this)
- ✅ OpenAI API key
- ✅ Alpha Vantage API key (optional but recommended)
- ✅ Your code ready in the `stockassistantweb` folder

---

## Step 1: Prepare Your Code

### 1.1 Verify Files Are Ready

Make sure you have these files in `1_foundations/stockassistantweb/`:

```
stockassistantweb/
├── Stock_assistant_web.py    ← Main application
├── requirements.txt          ← Dependencies
├── render.yaml              ← Render config (optional)
└── README.md                ← Documentation
```

### 1.2 Test Locally (Optional but Recommended)

```bash
cd 1_foundations/stockassistantweb
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
export ALPHA_VANTAGE_API_KEY=your_key_here
python Stock_assistant_web.py
```

If it runs on `http://localhost:7860`, you're good to go!

---

## Step 2: Push Code to GitHub

### 2.1 Initialize Git (if not already done)

```bash
cd /Users/maneeshmukundan/projects/agents
git add 1_foundations/stockassistantweb/
git commit -m "Add Stock Assistant Web for Render deployment"
git push origin main
```

**Note:** Make sure your `.env` file is in `.gitignore` - never commit API keys!

### 2.2 Verify on GitHub

- Go to https://github.com/your-username/your-repo
- Confirm `1_foundations/stockassistantweb/` folder is visible
- Check that `Stock_assistant_web.py` and `requirements.txt` are there

---

## Step 3: Create Render Account

### 3.1 Sign Up

1. Go to **https://render.com**
2. Click **"Get Started for Free"** or **"Sign Up"**
3. Choose one of these options:
   - **Sign up with GitHub** (recommended - easiest)
   - **Sign up with Email** (then connect GitHub later)

### 3.2 Verify Email (if using email)

- Check your email inbox
- Click the verification link from Render

### 3.3 Connect GitHub (if not done during signup)

1. Go to **Dashboard** → **Account Settings**
2. Click **"Connect GitHub"** or **"Link GitHub Account"**
3. Authorize Render to access your repositories
4. Select the repositories you want to deploy (or "All repositories")

---

## Step 4: Create New Web Service

### 4.1 Start New Deployment

1. In Render dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**

### 4.2 Connect Repository

1. You'll see a list of your GitHub repositories
2. **Find and click** on your repository (the one with `stockassistantweb`)
3. Click **"Connect"**

---

## Step 5: Configure Service Settings

### 5.1 Basic Configuration

Fill in these fields:

- **Name:** `stock-assistant` (or any name you like)
- **Region:** Choose closest to you (e.g., `Oregon (US West)`)
- **Branch:** `main` (or your default branch)
- **Root Directory:** `1_foundations/stockassistantweb`

**Important:** Set Root Directory to `1_foundations/stockassistantweb` so Render knows where your files are!

### 5.2 Build & Start Commands

- **Environment:** Select **"Python 3"**

- **Build Command:**
  ```
  pip install -r requirements.txt
  ```

- **Start Command:**
  ```
  python Stock_assistant_web.py
  ```

### 5.3 Plan Selection

- **Plan:** Select **"Free"** (for testing)
- Click **"Create Web Service"**

---

## Step 6: Add Environment Variables

### 6.1 Navigate to Environment Tab

1. After creating the service, you'll see the service dashboard
2. Click on **"Environment"** tab (left sidebar)

### 6.2 Add Variables

Click **"Add Environment Variable"** and add these:

**Variable 1:**
- **Key:** `OPENAI_API_KEY`
- **Value:** `sk-your-actual-openai-key-here`
- Click **"Save Changes"**

**Variable 2:**
- **Key:** `ALPHA_VANTAGE_API_KEY`
- **Value:** `your-actual-alpha-vantage-key-here`
- Click **"Save Changes"**

**Important:** 
- Never share these keys publicly
- Keys are encrypted in Render
- You can update them anytime

### 6.3 Verify Variables

You should see both variables listed in the Environment tab.

---

## Step 7: Deploy

### 7.1 Automatic Deployment

Render will automatically:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Start your application
4. Assign a public URL

### 7.2 Monitor Deployment

1. Go to **"Logs"** tab to watch the deployment
2. You'll see:
   - Installing dependencies
   - Starting application
   - "Starting Stock Assistant..." message
   - Server running on port assigned by Render

### 7.3 Wait for Build

- First deployment takes **2-5 minutes**
- Subsequent deployments are faster (~1-2 minutes)
- Watch for: **"Your service is live at..."** message

---

## Step 8: Access Your App

### 8.1 Get Your URL

1. Once deployed, you'll see a **"Live"** status
2. Your app URL will be: `https://stock-assistant.onrender.com`
   (or `https://your-service-name.onrender.com`)

### 8.2 Test Your App

1. Click the URL or copy it to your browser
2. You should see the Stock Assistant interface
3. Try asking: **"What's Apple's price?"**

---

## Step 9: Verify Everything Works

### 9.1 Test Features

Try these questions:
- ✅ "What's Tesla's price?"
- ✅ "Should I buy Microsoft?"
- ✅ "Healthcare stocks declining this month?"

### 9.2 Check Logs

1. Go to **"Logs"** tab
2. Look for any errors
3. Verify API calls are working

---

## Step 10: Custom Domain (Optional)

### 10.1 Add Custom Domain

1. Go to **"Settings"** tab
2. Scroll to **"Custom Domains"**
3. Click **"Add Custom Domain"**
4. Enter your domain (e.g., `stock-assistant.yourdomain.com`)
5. Follow DNS configuration instructions

---

## 🔄 Updating Your App

### To Update After Code Changes:

1. **Push changes to GitHub:**
   ```bash
   git add .
   git commit -m "Update stock assistant"
   git push
   ```

2. **Render auto-deploys:**
   - Render detects the push
   - Automatically rebuilds and redeploys
   - Takes 1-3 minutes

3. **Or manually trigger:**
   - Go to Render dashboard
   - Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## ⚠️ Important Notes

### Free Tier Limitations

- **Sleep after 15 minutes** of inactivity
- **First request after sleep** takes ~30 seconds (wake-up time)
- **Custom domains** are supported
- **HTTPS** is automatic and free
- **No credit card** required for free tier

### Best Practices

- ✅ Keep API keys secure (never commit to Git)
- ✅ Monitor usage in Render dashboard
- ✅ Check logs regularly for errors
- ✅ Test locally before deploying

---

## 🆘 Troubleshooting

### Problem: Build Fails

**Solution:**
- Check **"Logs"** tab for error messages
- Verify `requirements.txt` has all dependencies
- Ensure `Stock_assistant_web.py` is in the root directory
- Check Python version (Render uses Python 3.9+)

### Problem: App Starts But Shows Error

**Solution:**
- Check environment variables are set correctly
- Verify API keys are valid
- Check logs for specific error messages
- Test API keys locally first

### Problem: "Port Already in Use"

**Solution:**
- This shouldn't happen - Render sets PORT automatically
- If it does, check your code uses `os.environ.get("PORT")`

### Problem: App Sleeps Too Often

**Solution:**
- This is normal on free tier
- First request after sleep takes ~30 seconds
- Consider upgrading to paid plan for always-on

### Problem: Slow Response Times

**Solution:**
- First request after sleep is slow (normal)
- Subsequent requests are fast
- Check your API response times
- Monitor Render logs for bottlenecks

---

## 📊 Monitoring Your App

### View Logs

1. Go to service dashboard
2. Click **"Logs"** tab
3. See real-time application logs
4. Filter by date/time

### View Metrics

1. Go to **"Metrics"** tab
2. See:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Set Up Alerts

1. Go to **"Alerts"** tab
2. Configure email notifications for:
   - Deployment failures
   - Service downtime
   - High error rates

---

## ✅ Success Checklist

After deployment, verify:

- [ ] App is accessible at Render URL
- [ ] UI loads correctly
- [ ] Can ask questions
- [ ] Gets stock data
- [ ] API keys are working
- [ ] No errors in logs
- [ ] HTTPS is enabled (automatic)

---

## 🎉 You're Done!

Your Stock Assistant Web is now live on Render!

**Your app URL:** `https://your-service-name.onrender.com`

**Share it with:** Friends, colleagues, or add it to your portfolio!

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Render Status Page](https://status.render.com)
- [Gradio Documentation](https://www.gradio.app/docs)
- [Support](https://render.com/support)

---

## 🔗 Quick Links

- **Render Dashboard:** https://dashboard.render.com
- **Your Service:** https://dashboard.render.com/web/your-service-name
- **Logs:** Available in service dashboard

---

**Need Help?** Check the logs first, then refer to Render's documentation or support.

**Happy Deploying! 🚀**

