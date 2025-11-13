# 📊 Stock Assistant Chatbot - Web Version

This is the web-ready version of the Stock Assistant Chatbot, configured for deployment on Render.

## 🎯 Features

- **NLP extraction**: Finds companies/tickers anywhere in question
- **30-day historical data** with Alpha Vantage → Yahoo Finance fallback
- **News integration** for predictive questions
- **Sector analysis** with dynamic stock retrieval
- **Smart responses**: Simple answers for simple questions, detailed analysis when needed
- **Complete source references**

## 🚀 Quick Deploy to Render

### Option 1: Using Render Dashboard (Recommended)

1. **Push to GitHub**
   ```bash
   git add stockassistantweb/
   git commit -m "Add web version for Render"
   git push
   ```

2. **Go to Render**
   - Visit https://render.com
   - Sign up/login (free account)
   - Click "New +" → "Web Service"

3. **Connect Repository**
   - Connect your GitHub account
   - Select your repository
   - Choose the `1_foundations/stockassistantweb` directory

4. **Configure Service**
   - **Name:** `stock-assistant` (or your choice)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python Stock_assistant_web.py`
   - **Plan:** Free

5. **Add Environment Variables**
   In the Render dashboard, go to "Environment" and add:
   - `OPENAI_API_KEY` = your OpenAI API key
   - `ALPHA_VANTAGE_API_KEY` = your Alpha Vantage API key (optional but recommended)

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 2-3 minutes for build and deployment
   - Your app will be live at: `https://stock-assistant.onrender.com`

### Option 2: Using render.yaml (Advanced)

If you have the Render CLI installed:

```bash
render deploy
```

The `render.yaml` file is already configured in this directory.

## 📝 Files Included

- `Stock_assistant_web.py` - Main application (web-ready)
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `README.md` - This file

## 🔧 Local Testing

Before deploying, test locally:

```bash
cd stockassistantweb
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
export ALPHA_VANTAGE_API_KEY=your_key  # Optional
python Stock_assistant_web.py
```

The app will run on `http://localhost:7860`

## ⚠️ Important Notes

### Free Tier Limitations

- **Sleep after inactivity**: Free tier apps sleep after 15 minutes of inactivity
- **First request delay**: First request after sleep takes ~30 seconds to wake up
- **Custom domain**: Free tier supports custom domains
- **HTTPS**: Automatic HTTPS included

### Environment Variables

Make sure to set these in Render dashboard:
- `OPENAI_API_KEY` (required)
- `ALPHA_VANTAGE_API_KEY` (optional, but recommended for better data)

### Port Configuration

The app automatically uses the `PORT` environment variable set by Render. No manual configuration needed!

## 🎨 UI Features

- **Chat interface** with message history
- **Copy button** on messages
- **Example questions** for quick start
- **Clear button** to reset conversation
- **Responsive design** works on mobile and desktop

## 📊 Example Questions

- "What's Apple's price?"
- "Should I buy Tesla?"
- "Healthcare stocks declining this month?"
- "When was NVIDIA highest?"
- "What are the top 3 technology stocks?"

## 🆘 Troubleshooting

### App not starting?
- Check environment variables are set correctly
- Check build logs in Render dashboard
- Verify `requirements.txt` has all packages

### Port errors?
- The code handles this automatically via `PORT` env var
- No manual configuration needed

### Slow first request?
- This is normal on free tier (app wakes from sleep)
- Consider upgrading to paid plan for always-on

### Import errors?
- Make sure all packages in `requirements.txt` are installed
- Check build logs for missing dependencies

## 🔗 Resources

- [Render Documentation](https://render.com/docs)
- [Gradio Documentation](https://www.gradio.app/docs)
- [Original Stock Assistant](../stock_assistant_chatbot.py)

## 📄 License

Same as parent project.

---

**Ready to deploy?** Follow the Quick Deploy steps above! 🚀

