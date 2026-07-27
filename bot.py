import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Sports list
SPORTS = {
    "football": "⚽ Football",
    "basketball": "🏀 Basketball",
    "tennis": "🎾 Tennis",
    "cricket": "🏏 Cricket",
    "golf": "⛳ Golf",
    "f1": "🏎️ Formula 1",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message."""
    user = update.effective_user
    await update.message.reply_text(
        f"🏆 Welcome {user.first_name}!\n\n"
        "I'm your Sports News Bot.\n\n"
        "Commands:\n"
        "/sports - Choose a sport\n"
        "/help - Show help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    await update.message.reply_text(
        "📋 Commands:\n"
        "/start - Start the bot\n"
        "/sports - Choose a sport\n"
        "/help - Show this help"
    )

async def sports_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show sports menu."""
    keyboard = []
    for key, name in SPORTS.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=key)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚽ Choose a sport:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    
    sport_key = query.data
    sport_name = SPORTS.get(sport_key, sport_key)
    
    # Send sample news (since we're keeping it simple)
    news = (
        f"📰 **{sport_name} News**\n\n"
        f"• Latest updates about {sport_key}\n"
        f"• Championship standings\n"
        f"• Player transfers and injuries\n"
        f"• Upcoming matches\n\n"
        f"🔹 To get real news, add NEWS_API_KEY\n"
        f"🔹 Get free key at newsapi.org"
    )
    
    await query.edit_message_text(
        news,
        parse_mode="Markdown"
    )

def main():
    """Start the bot."""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return
    
    logger.info("Starting bot...")
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sports", sports_menu))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Start polling
    logger.info("Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
