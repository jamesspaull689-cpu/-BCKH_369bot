import os
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Sports categories with their NewsAPI query parameters
SPORTS = {
    "football": "football",
    "basketball": "basketball",
    "tennis": "tennis",
    "cricket": "cricket",
    "golf": "golf",
    "f1": "formula 1",
}

# NewsAPI key (free tier - get from newsapi.org)
# You can also use a different API or web scraping
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"🏆 Welcome {user.first_name}!\n\n"
        "I'm your Sports News Bot. I'll keep you updated with the latest sports headlines.\n\n"
        "⚽ Use /sports to choose a sport and get the latest news.\n"
        "📰 Use /headlines to get top sports headlines.\n"
        "❓ Use /help for more commands."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    help_text = (
        "📋 **Available Commands:**\n\n"
        "/start - Start the bot\n"
        "/sports - Choose a sport to get news\n"
        "/headlines - Get top sports headlines\n"
        "/help - Show this help message\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def sports_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show a menu of sports to choose from."""
    keyboard = []
    for sport in SPORTS.keys():
        keyboard.append([InlineKeyboardButton(sport.capitalize(), callback_data=sport)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚽ Choose a sport to get the latest news:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses from the sports menu."""
    query = update.callback_query
    await query.answer()
    
    sport = query.data
    sport_name = SPORTS.get(sport, sport)
    
    await query.edit_message_text(f"📰 Fetching latest {sport_name} news...")
    
    # Fetch news from NewsAPI or use a fallback
    news = await get_sports_news(sport_name)
    
    if news:
        await query.message.reply_text(news)
    else:
        await query.message.reply_text(
            f"❌ Sorry, couldn't fetch {sport_name} news right now. Please try again later."
        )

async def get_sports_news(sport: str) -> str:
    """Fetch sports news from an API."""
    if NEWS_API_KEY:
        # Using NewsAPI
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": sport,
            "apiKey": NEWS_API_KEY,
            "pageSize": 5,
            "language": "en",
            "sortBy": "publishedAt"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok" and data.get("articles"):
                articles = data["articles"][:5]
                news_text = f"📰 **Latest {sport.capitalize()} News**\n\n"
                for i, article in enumerate(articles, 1):
                    title = article.get("title", "No title")
                    source = article.get("source", {}).get("name", "Unknown")
                    url = article.get("url", "#")
                    news_text += f"{i}. **{title}**\n"
                    news_text += f"   📌 {source}\n"
                    news_text += f"   🔗 [Read more]({url})\n\n"
                return news_text
            else:
                return "⚠️ No news articles found for this sport."
                
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return None
    else:
        # Fallback: Return sample news if no API key
        return (
            f"📰 **{sport.capitalize()} News**\n\n"
            "🔹 To get real news, get a free API key from newsapi.org\n"
            "🔹 Add it as NEWS_API_KEY in Railway environment variables\n\n"
            "📌 Sample headlines for demonstration:\n"
            f"• {sport.capitalize()} star signs record deal\n"
            f"• Championship updates for {sport}\n"
            f"• {sport.capitalize()} league standings announced\n"
        )

async def headlines(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get top sports headlines."""
    await update.message.reply_text("📰 Fetching top sports headlines...")
    
    if NEWS_API_KEY:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": "sports",
            "apiKey": NEWS_API_KEY,
            "pageSize": 5,
            "language": "en"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok" and data.get("articles"):
                articles = data["articles"][:5]
                news_text = "🏆 **Top Sports Headlines**\n\n"
                for i, article in enumerate(articles, 1):
                    title = article.get("title", "No title")
                    source = article.get("source", {}).get("name", "Unknown")
                    url = article.get("url", "#")
                    news_text += f"{i}. **{title}**\n"
                    news_text += f"   📌 {source}\n"
                    news_text += f"   🔗 [Read more]({url})\n\n"
                await update.message.reply_text(news_text, parse_mode="Markdown", disable_web_page_preview=True)
            else:
                await update.message.reply_text("⚠️ No sports headlines found.")
                
        except Exception as e:
            logger.error(f"Error fetching headlines: {e}")
            await update.message.reply_text("❌ Error fetching headlines. Please try again later.")
    else:
        await update.message.reply_text(
            "📰 **Top Sports Headlines**\n\n"
            "🔹 To get real news, get a free API key from newsapi.org\n"
            "🔹 Add it as NEWS_API_KEY in Railway environment variables\n\n"
            "Sample headlines:\n"
            "• Championship finals set for this weekend\n"
            "• Star player breaks all-time record\n"
            "• New coaching staff announced for top team"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.warning(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
        return
    
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sports", sports_menu))
    application.add_handler(CommandHandler("headlines", headlines))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot (using webhook or polling - Railway works with polling)
    logger.info("Bot started! Use /start to begin.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
