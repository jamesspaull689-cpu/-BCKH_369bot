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

# Sports dictionary
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
        "I'm your Sports News Bot.\n"
        "Use /sports to get news.\n"
        "Use /help for commands."
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
    
    # Send sport-specific news
    news_messages = {
        "football": "⚽ **Football News**\n\n• Premier League updates\n• Champions League results\n• Transfer rumors\n• Match schedules",
        "basketball": "🏀 **Basketball News**\n\n• NBA standings\n• Playoff updates\n• Player stats\n• Trade rumors",
        "tennis": "🎾 **Tennis News**\n\n• Grand Slam results\n• ATP/WTA rankings\n• Tournament schedules\n• Player updates",
        "cricket": "🏏 **Cricket News**\n\n• ICC rankings\n• Test match updates\n• T20 league news\n• World Cup schedules",
        "golf": "⛳ **Golf News**\n\n• PGA Tour updates\n• Major championships\n• Player rankings\n• Tournament results",
        "f1": "🏎️ **F1 News**\n\n• Race results\n• Driver standings\n• Constructor standings\n• Race schedules"
    }
    
    news = news_messages.get(sport_key, f"📰 {sport_name} News")
    
    await query.edit_message_text(
        news,
        parse_mode="Markdown"
    )

def main():
    """Start the bot."""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables!")
        return
    
    logger.info("Starting Sports News Bot...")
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sports", sports_menu))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("Bot is running! Use /start in Telegram.")
    app.run_polling()

if __name__ == "__main__":
    main()
