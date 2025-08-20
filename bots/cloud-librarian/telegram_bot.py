#!/usr/bin/env python3
"""
Telegram Bot Integration for Cloud Librarian

This bot provides a Telegram interface to the Cloud Librarian engine,
allowing remote command control and file management.
"""

import os
import logging
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ENGINE_URL = os.getenv("ENGINE_URL", "http://localhost:5000")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_librarian")

class TelegramLibrarian:
    def __init__(self, token, engine_url):
        self.token = token
        self.engine_url = engine_url
        self.bot = Bot(token=token)
        
    def call_engine(self, command, data=None):
        """Call the librarian engine API"""
        if data is None:
            data = {}
        data["command"] = command
        
        try:
            response = requests.post(f"{self.engine_url}/engine", json=data, timeout=30)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Engine call failed: {e}")
            return {"error": f"Could not contact engine: {str(e)}"}
    
    def start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        welcome_message = """
🤖 *Cloud Librarian Bot*

I'm your automated code library assistant! I can help you:

📝 *Organize* - Store and categorize code snippets
🔍 *Search* - Find code in your library
💾 *Backup* - Create library backups
🔄 *Sync* - Synchronize with OneDrive

*Commands:*
/organize - Add a code snippet to library
/search <query> - Search for code
/backup - Create a backup
/sync - Sync with cloud storage
/status - Check system status
/help - Show this help message

Just send me code snippets and I'll organize them automatically!
        """
        update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    def help_command(self, update: Update, context: CallbackContext):
        """Handle /help command"""
        help_text = """
*Available Commands:*

/organize - Add code snippet to library
/search <query> - Search your code library
/backup [name] - Create a library backup
/sync - Synchronize with OneDrive
/status - Check engine status
/stats - Show library statistics

*Usage Examples:*
• `/search flask` - Find Flask-related code
• `/organize` (then send code) - Add code to library
• `/backup my_backup` - Create named backup

*Inline Usage:*
Just send me any code snippet and I'll organize it automatically with language detection!
        """
        update.message.reply_text(help_text, parse_mode='Markdown')
    
    def organize_command(self, update: Update, context: CallbackContext):
        """Handle /organize command"""
        if context.args:
            # Code provided as arguments
            snippet = " ".join(context.args)
            self.handle_code_organization(update, snippet)
        else:
            update.message.reply_text(
                "Please send the code snippet you want to organize, or use:\n"
                "`/organize <your code here>`",
                parse_mode='Markdown'
            )
    
    def search_command(self, update: Update, context: CallbackContext):
        """Handle /search command"""
        if not context.args:
            update.message.reply_text("Please provide a search query: `/search <query>`", parse_mode='Markdown')
            return
            
        query = " ".join(context.args)
        response = self.call_engine("search", {"query": query})
        
        if "error" in response:
            update.message.reply_text(f"❌ Search failed: {response['error']}")
            return
        
        results = response.get("results", [])
        if not results:
            update.message.reply_text(f"🔍 No results found for: *{query}*", parse_mode='Markdown')
            return
        
        # Format search results
        message = f"🔍 *Search Results for:* {query}\n\n"
        for i, result in enumerate(results[:5], 1):  # Show top 5 results
            filename = result["filename"]
            language = result["info"]["language"]
            tags = ", ".join(result["info"]["tags"]) if result["info"]["tags"] else "no tags"
            
            message += f"{i}. `{filename}`\n"
            message += f"   📁 Language: {language}\n"
            message += f"   🏷 Tags: {tags}\n\n"
        
        if len(results) > 5:
            message += f"... and {len(results) - 5} more results"
        
        update.message.reply_text(message, parse_mode='Markdown')
    
    def backup_command(self, update: Update, context: CallbackContext):
        """Handle /backup command"""
        backup_name = context.args[0] if context.args else None
        data = {"name": backup_name} if backup_name else {}
        
        update.message.reply_text("⏳ Creating backup...")
        response = self.call_engine("backup", data)
        
        if "error" in response:
            update.message.reply_text(f"❌ Backup failed: {response['error']}")
        else:
            backup_name = response.get("backup_name", "unknown")
            update.message.reply_text(f"✅ Backup created: `{backup_name}`", parse_mode='Markdown')
    
    def sync_command(self, update: Update, context: CallbackContext):
        """Handle /sync command"""
        update.message.reply_text("⏳ Synchronizing with OneDrive...")
        response = self.call_engine("sync")
        
        if "error" in response:
            update.message.reply_text(f"❌ Sync failed: {response['error']}")
        else:
            update.message.reply_text("✅ Library synchronized with OneDrive")
    
    def status_command(self, update: Update, context: CallbackContext):
        """Handle /status command"""
        try:
            response = requests.get(f"{self.engine_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status_message = f"""
🟢 *Engine Status: Online*

📍 Service: {data.get('service', 'unknown')}
📂 Library Path: `{data.get('library_path', 'unknown')}`
⏰ Last Check: {data.get('timestamp', 'unknown')}
                """
            else:
                status_message = "🔴 *Engine Status: Offline*"
        except:
            status_message = "🔴 *Engine Status: Unreachable*"
        
        update.message.reply_text(status_message, parse_mode='Markdown')
    
    def handle_code_organization(self, update: Update, snippet):
        """Handle code snippet organization"""
        # Try to detect if it's a code snippet
        if len(snippet) < 10:
            update.message.reply_text("⚠️ Snippet seems too short. Please provide a meaningful code snippet.")
            return
        
        response = self.call_engine("organize", {"snippet": snippet})
        
        if "error" in response:
            update.message.reply_text(f"❌ Organization failed: {response['error']}")
        else:
            filename = response.get("filename", "unknown")
            language = response.get("language", "unknown")
            update.message.reply_text(
                f"✅ Code organized!\n\n"
                f"📄 File: `{filename}`\n"
                f"💻 Language: {language}",
                parse_mode='Markdown'
            )
    
    def handle_text_message(self, update: Update, context: CallbackContext):
        """Handle regular text messages (potential code snippets)"""
        text = update.message.text
        
        # Check if it looks like code
        code_indicators = ['def ', 'function', 'import', 'from ', '#!/', 'const ', 'var ', 'let ', 'class ', 'if ', 'for ', 'while ']
        
        if any(indicator in text for indicator in code_indicators) or len(text.split('\n')) > 3:
            # Looks like code, organize it
            self.handle_code_organization(update, text)
        else:
            # Regular message, provide help
            update.message.reply_text(
                "I didn't recognize that as a command or code snippet. 🤔\n\n"
                "Try:\n"
                "• Send me code snippets to organize them\n"
                "• Use /help to see available commands\n"
                "• Use /search <query> to find code"
            )

def main():
    """Main function to start the Telegram bot"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable not set")
        return
    
    # Create the librarian bot
    librarian = TelegramLibrarian(TELEGRAM_TOKEN, ENGINE_URL)
    
    # Create the updater and dispatcher
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Add command handlers
    dp.add_handler(CommandHandler("start", librarian.start_command))
    dp.add_handler(CommandHandler("help", librarian.help_command))
    dp.add_handler(CommandHandler("organize", librarian.organize_command))
    dp.add_handler(CommandHandler("search", librarian.search_command))
    dp.add_handler(CommandHandler("backup", librarian.backup_command))
    dp.add_handler(CommandHandler("sync", librarian.sync_command))
    dp.add_handler(CommandHandler("status", librarian.status_command))
    
    # Add message handler for regular text
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, librarian.handle_text_message))
    
    # Start the bot
    logger.info("Starting Telegram Librarian Bot...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()