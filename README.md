# 🤖 AliExpress Telegram Bot
**Python Telegram Bot - Beginner Friendly**

Automatically search and share AliExpress products with affiliate links through Telegram!

📱 **Created by Tech Mouad**
📺 **YouTube:** https://www.youtube.com/@techmouad
📸 **Instagram:** https://www.instagram.com/tech_mouad/
☕ **Support:** https://buymeacoffee.com/techmouad
**Subscribe for more automation tools! 🚀**

## 🎯 What It Does
**Before:** ❌ Manual product search = Hours of work  
**After:** ✅ Just send a message to bot = Get products instantly! ☕

## ✨ Features
- 🔍 **Smart Product Search** - Find any product on AliExpress
- 🔗 **Automatic Affiliate Links** - Generate commission links instantly  
- 📱 **Easy Telegram Interface** - Just chat with the bot
- � **Product Details** - Get prices, images, and descriptions
- 📊 **Real-time Results** - Fast and accurate search results

## 🚀 Quick Setup (No Coding Required!)

### 1. Install Python (One Time Setup)
1. Go to [python.org](https://python.org)
2. Download and install Python
3. ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation

### 2. Download This Bot
1. Click the green **"Code"** button above → **"Download ZIP"**
2. Extract the ZIP file to your Desktop

### 3. Install Requirements
1. Open **Command Prompt** (Windows) or **Terminal** (Mac/Linux)
2. Type these commands:
   ```
   cd Desktop/AliexpressBot
   pip install -r requirements.txt
   ```

### 4. Get Your Bot Token 🤖
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Choose a name and username for your bot
4. **Copy the token** BotFather gives you (keep it safe!)

### 5. Get AliExpress API Credentials 🔑
1. Go to [AliExpress Open Platform](https://open.aliexpress.com/)
2. Sign up/login with your account
3. Create a new application
4. Copy your **App Key** and **App Secret**

### 6. Setup Your Environment
1. Find the file called `.env.example` in your bot folder
2. Rename it to `.env` (remove the .example part)
3. Open the `.env` file and fill in your information:
   ```
   TELEGRAM_BOT_TOKEN=paste_your_bot_token_here
   ALIEXPRESS_API_PUBLIC=paste_your_app_key_here
   ALIEXPRESS_API_SECRET=paste_your_app_secret_here
   ```

## 🌐 Running Your Bot

### Option 1: Local Testing (Easiest)
1. Open Command Prompt/Terminal
2. Navigate to your bot folder:
   ```
   cd Desktop/AliexpressBot
   ```
3. Run the bot:
   ```
   python Bot.py
   ```
4. Your bot is now running! Test it on Telegram

### Option 2: Online 24/7 with ngrok (Advanced)
Make your bot accessible from anywhere!

#### Step 1: Install ngrok
1. Go to [ngrok.com](https://ngrok.com) and create free account
2. Download ngrok for your system
3. Extract ngrok to your bot folder

#### Step 2: Setup ngrok
1. Open Command Prompt in your bot folder
2. Run:
   ```
   ngrok authtoken YOUR_NGROK_TOKEN
   ```
   (Get your token from ngrok dashboard)

#### Step 3: Start ngrok tunnel
1. First, run your bot:
   ```
   python Bot.py
   ```
2. Open another Command Prompt and run:
   ```
   ngrok http 5000
   ```
3. Copy the **https** URL ngrok gives you (looks like: `https://abc123.ngrok.io`)

#### Step 4: Set Webhook
1. Add this line to your `.env` file:
   ```
   WEBHOOK_URL=https://your-ngrok-url.ngrok.io/webhook
   ```
2. Restart your bot

**🎉 Your bot is now accessible from anywhere!**
**⚠️ Important: Your PC must stay ON for the bot to work**

### Option 3: True 24/7 Hosting (Real Cloud Hosting)
Want your bot to work even when your PC is OFF? Use cloud hosting!

#### 🆓 Free Cloud Options:
**Railway (Recommended for beginners)**
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect this bot repository
4. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `ALIEXPRESS_API_PUBLIC` 
   - `ALIEXPRESS_API_SECRET`
   - `WEBHOOK_URL` (Railway will provide this)
5. Deploy automatically!

**Render.com**
1. Sign up at [render.com](https://render.com)
2. Create "New Web Service" from GitHub
3. Add environment variables
4. Deploy for free

#### 💰 Paid Options ($5-10/month):
- **DigitalOcean** - Simple VPS hosting
- **Heroku** - Easy deployment platform
- **AWS/Google Cloud** - Enterprise solutions

**🎉 Now your bot is TRULY online 24/7!**
**✅ Works even when your PC is completely off**
**✅ No ngrok needed**
**✅ Professional hosting**

## 🔧 How to Use Your Bot

1. **Start the bot:** Send `/start` to your bot on Telegram
2. **Search products:** Just type what you're looking for (e.g., "wireless headphones")
3. **Get affiliate links:** The bot automatically generates commission links
4. **Share with friends:** Send the links to earn commissions!

## 📁 Project Files
```
AliexpressBot/
├── Bot.py                     ← Main bot file
├── requirements.txt           ← Dependencies
├── .env.example              ← Environment template
├── aliexpress_api/           ← API wrapper
└── README.md                 ← This guide
```

## ❓ Common Issues

**"Python not found"**  
→ Reinstall Python with "Add to PATH" checked

**"Bot not responding"**  
→ Check your bot token is correct in .env file

**"API errors"**  
→ Verify your AliExpress API credentials

**"ngrok tunnel closed"**  
→ Restart ngrok command, URL changes each time

**"No products found"**  
→ Try different search terms or check API limits

## 🔒 Security Tips
- Keep your bot token and API keys private
- Don't share your `.env` file
- Test with small searches first
- Monitor your API usage

## 🎬 Video Tutorial
Watch the complete setup tutorial on our YouTube channel!

## 💡 Need Help?
- Check our YouTube channel for tutorials: [@techmouad](https://www.youtube.com/@techmouad)
- Follow us on Instagram for updates: [@tech_mouad](https://www.instagram.com/tech_mouad/)
- Create an issue on GitHub if you find bugs
- Support the project: [Buy me a coffee ☕](https://buymeacoffee.com/techmouad)

---

**Made with ❤️ by Tech Mouad**  
📺 [**YouTube**](https://www.youtube.com/@techmouad) | 📸 [**Instagram**](https://www.instagram.com/tech_mouad/) | ☕ [**Buy me a coffee**](https://buymeacoffee.com/techmouad)

*Star this repo if it helped you! ⭐*