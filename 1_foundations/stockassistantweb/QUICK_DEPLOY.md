# ⚡ Quick Deploy to Render - 5 Minutes

## 🚀 Fast Track Steps

### 1. Push to GitHub
```bash
git add 1_foundations/stockassistantweb/
git commit -m "Ready for Render"
git push
```

### 2. Create Render Account
- Go to https://render.com
- Sign up with GitHub (easiest)

### 3. Create Web Service
- Click **"New +"** → **"Web Service"**
- Connect your GitHub repository
- Set **Root Directory:** `1_foundations/stockassistantweb`

### 4. Configure
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python Stock_assistant_web.py`
- **Plan:** Free

### 5. Add Environment Variables
In **"Environment"** tab, add:
- `OPENAI_API_KEY` = your key
- `ALPHA_VANTAGE_API_KEY` = your key

### 6. Deploy!
- Click **"Create Web Service"**
- Wait 2-3 minutes
- Your app: `https://your-service-name.onrender.com`

---

## ✅ That's It!

For detailed instructions, see `RENDER_DEPLOYMENT_STEPS.md`

