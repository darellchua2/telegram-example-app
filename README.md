# Telegram Bot Webhook Server

A secure FastAPI-based webhook server for Telegram bots with user authorization and modular architecture.

## 🚀 Features

- **FastAPI webhook server** for handling Telegram bot updates
- **User authorization** - restrict bot access to specific users
- **Modular architecture** - clean separation of concerns
- **Environment-based configuration** - secure credential management
- **Comprehensive logging** - track all interactions and unauthorized attempts
- **Type safety** - full type hints and Pydantic models

## 📁 Project Structure

```
telegram-example-app/
├── models/
│   ├── __init__.py          # Models package
│   └── webhook.py           # Webhook Pydantic models
├── utils/
│   ├── __init__.py          # Utils package
│   ├── auth.py              # Authorization & security
│   ├── config.py            # Configuration management
│   └── telegram_handlers.py # Message processing logic
├── main.py                  # FastAPI application
├── .env                     # Environment variables (create from .env.example)
├── .env.example             # Environment template
├── pyproject.toml           # Poetry dependencies
└── README.md               # This file
```

## 🛠️ Setup Instructions

### 1. **Prerequisites**

- Python 3.9+
- Poetry (for dependency management)
- A Telegram account

### 2. **Clone and Setup Environment**

```bash
# Clone the repository
git clone <your-repo-url>
cd telegram-example-app

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install Poetry in virtual environment
pip install poetry

# Install dependencies
poetry install
```

### 3. **Create Your Telegram Bot**

1. **Message @BotFather** on Telegram
2. **Create a new bot**:
   ```
   /newbot
   ```
3. **Choose a name**: `My Awesome Bot`
4. **Choose a username**: `my_awesome_bot` (must end with `bot`)
5. **Copy the bot token**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 4. **Get Your Telegram User ID**

1. **Message @userinfobot** on Telegram
2. **Copy your user ID**: `123456789`

### 5. **Configure Environment Variables**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

**Update `.env` with your actual values:**

```bash
# Telegram Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
WEBHOOK_SECRET=your_secure_random_string_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security Configuration - Your Telegram User ID
AUTHORIZED_USERS=123456789
```

**Generate a secure webhook secret:**

```bash
# Option 1: Using openssl
openssl rand -hex 32

# Option 2: Using Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 6. **Test Locally**

```bash
# Start the application
poetry run python main.py

# The server will start at http://localhost:8000
# Check health endpoint: http://localhost:8000/health
```

## 🌐 Webhook Registration

### **Option A: Local Development with ngrok (Recommended for Testing)**

1. **Install ngrok**: Download from [ngrok.com](https://ngrok.com/)

2. **Start your FastAPI app**:
   ```bash
   poetry run python main.py
   ```

3. **Expose with ngrok** (in another terminal):
   ```bash
   ngrok http 8000
   ```

   Note the HTTPS URL: `https://abc123.ngrok.io`

4. **Register webhook with Telegram**:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
        -H "Content-Type: application/json" \
        -d '{
          "url": "https://abc123.ngrok.io/webhook/<YOUR_WEBHOOK_SECRET>",
          "allowed_updates": ["message", "callback_query"],
          "max_connections": 40,
          "drop_pending_updates": true
        }'
   ```

### **Option B: Production Deployment**

Deploy to your preferred platform:

- **Railway**: `railway up`
- **Heroku**: `git push heroku main`
- **DigitalOcean App Platform**
- **AWS/GCP/Azure**

Then register webhook with your production URL:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://yourdomain.com/webhook/<YOUR_WEBHOOK_SECRET>",
       "allowed_updates": ["message", "callback_query"],
       "max_connections": 40,
       "drop_pending_updates": true
     }'
```

### **Webhook Registration Script**

Create `setup_webhook.py`:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WEBHOOK_URL = "https://yourdomain.com"  # Replace with your domain

def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

    data = {
        "url": f"{WEBHOOK_URL}/webhook/{WEBHOOK_SECRET}",
        "allowed_updates": ["message", "callback_query"],
        "max_connections": 40,
        "drop_pending_updates": True
    }

    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    set_webhook()
```

Run it:
```bash
poetry run python setup_webhook.py
```

## 🧪 Testing Your Bot

1. **Find your bot on Telegram**: Search for `@your_bot_username`
2. **Start a conversation**: Send `/start`
3. **Try commands**:
   - `/help` - Show available commands
   - `/whoami` - Show your user info
   - `/echo Hello` - Echo a message
4. **Check logs**: Your FastAPI app will show incoming webhook requests

## 🔧 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and get welcome message |
| `/help` | Show available commands |
| `/echo <text>` | Echo your message back |
| `/whoami` | Show your Telegram user ID and username |

## 🔐 Security Features

- **User Authorization**: Only users in `AUTHORIZED_USERS` can interact with the bot
- **Webhook Secret**: Prevents unauthorized webhook calls
- **Input Validation**: Pydantic models validate all incoming data
- **Comprehensive Logging**: All interactions and unauthorized attempts are logged
- **Environment Variables**: Sensitive data stored securely

### **How Authorization Works**

The auth manager acts as a **gatekeeper** for all bot interactions. Here's the complete flow:

```
┌─────────────────────────────────────────────────────────────────────┐
│                          TELEGRAM BOT FLOW                         │
└─────────────────────────────────────────────────────────────────────┘

1️⃣ INITIALIZATION (main.py startup)
┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   config.py      │───▶│   main.py       │───▶│  AuthManager     │
│ loads .env vars  │    │ creates objects │    │ (initialized)    │
└──────────────────┘    └─────────────────┘    └──────────────────┘
        │                         │                       │
        ▼                         ▼                       ▼
AUTHORIZED_USERS=123,456    auth_manager = AuthManager    stores user IDs
                           (config.authorized_users)      in memory set
```

```
2️⃣ INCOMING MESSAGE FLOW
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌──────────────┐
│  Telegram   │───▶│   Webhook   │───▶│  TelegramHandlers│───▶│ AuthManager  │
│   Server    │    │  Endpoint   │    │ process_message() │    │ check_auth() │
└─────────────┘    └─────────────┘    └─────────────────┘    └──────────────┘
                          │                     │                     │
                          ▼                     ▼                     ▼
              POST /webhook/secret    extracts user_id=789    is_user_authorized(789)
                  {message: ...}      from message.from_user        ↓
                                                               checks if 789 in
                                                               {123, 456} = ❌
```

```
3️⃣ AUTHORIZATION CHECK DETAIL
┌──────────────────────────────────────────────────────────────────────┐
│                      AuthManager.is_user_authorized()                │
└──────────────────────────────────────────────────────────────────────┘

Input: user_id = 789

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Check if empty  │───▶│ Check if in set │───▶│ Return result   │
│ authorized_users│    │ 789 in {123,456}│    │ True/False      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
if set is empty:         if 789 in {123, 456}:    return True/False
  log warning              return True              ↓
  return True           else:                   back to handler
                          return False
```

```
4️⃣ COMPLETE REQUEST FLOW
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FULL MESSAGE PROCESSING                           │
└─────────────────────────────────────────────────────────────────────────────┘

User 789 sends "/start" ───┐
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ POST /webhook/secret                                                        │
│ {                                                                          │
│   "message": {                                                             │
│     "from": {"id": 789, "username": "john"},                              │
│     "text": "/start"                                                       │
│   }                                                                        │
│ }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ handlers.process_message(message)                                          │
│   │                                                                        │
│   ├─ Extract: user_id = 789, username = "john"                            │
│   │                                                                        │
│   ├─ Call: auth_manager.is_user_authorized(789)                           │
│   │   │                                                                    │
│   │   └─ Check: 789 in {123, 456} = False ❌                             │
│   │                                                                        │
│   ├─ Since unauthorized:                                                   │
│   │   ├─ Log warning                                                       │
│   │   ├─ Send: "🚫 Sorry, you are not authorized"                        │
│   │   └─ Return: {"authorized": False}                                     │
│   │                                                                        │
│   └─ Skip command processing                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

**🔑 Key Trigger Points:**

The auth manager is triggered at exactly **2 locations**:

1. **Message Processing** (`utils/telegram_handlers.py:106`)
   ```python
   if not self.auth_manager.is_user_authorized(user_id):
       # TRIGGERED HERE! Blocks unauthorized users from commands
   ```

2. **Callback Query Processing** (`utils/telegram_handlers.py:148`)
   ```python
   if not self.auth_manager.is_user_authorized(user_id):
       # TRIGGERED HERE! Blocks unauthorized button clicks
   ```

**📋 Object Relationships:**
```
main.py:
├── config (loads AUTHORIZED_USERS)
├── auth_manager = AuthManager(config.authorized_users)
└── handlers = TelegramHandlers(telegram_app, auth_manager)
                                                 │
                                                 ▼
                                    handlers stores reference
                                    and calls auth_manager
                                    on every message/callback
```

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint - returns server status |
| `/health` | GET | Health check endpoint |
| `/webhook/{token}` | POST | Telegram webhook endpoint (protected by secret) |

## 🐛 Troubleshooting

### **Check Webhook Status**
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### **Common Issues**

1. **Bot not responding**:
   - Check webhook URL is accessible externally
   - Verify bot token is correct
   - Check application logs for errors

2. **Unauthorized users can't access**:
   - Verify user ID in `AUTHORIZED_USERS`
   - Check logs for authorization attempts

3. **Webhook registration fails**:
   - Ensure URL uses HTTPS (ngrok provides this)
   - Check webhook secret matches your `.env` file
   - Verify bot token is valid

4. **Application won't start**:
   - Check all required environment variables are set
   - Verify virtual environment is activated
   - Check for syntax errors in logs

### **Reset Webhook (for testing)**
```bash
# Remove webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"

# Get updates manually (polling mode)
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

## 🚀 Development

### **Project Dependencies**

- **FastAPI**: Web framework
- **python-telegram-bot**: Telegram Bot API wrapper
- **Pydantic**: Data validation
- **python-dotenv**: Environment variable management
- **Uvicorn**: ASGI server

### **Adding New Commands**

Edit `utils/telegram_handlers.py` in the `_handle_command` method:

```python
elif text.startswith("/newcommand"):
    return "Response for new command"
```

### **Adding Authorization for New Users**

Add user IDs to the `AUTHORIZED_USERS` environment variable (comma-separated):

```bash
AUTHORIZED_USERS=123456789,987654321,555666777
```

## 📄 License

This project is open source. Feel free to use and modify as needed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review application logs
3. Verify webhook registration status
4. Test with simple commands like `/start`

---

**Important**: Never commit your `.env` file or expose your bot token publicly. Keep your credentials secure!