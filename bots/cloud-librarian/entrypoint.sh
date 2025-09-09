#!/bin/bash
# entrypoint.sh - Cloud Librarian Bot Startup Script

echo "🚀 Starting Cloud Librarian Bot Engine..."

# Ensure OneDrive mount point exists
mkdir -p /onedrive/library

# Check if rclone configuration exists
if [ -f "/root/.config/rclone/rclone.conf" ]; then
    echo "📡 Found rclone configuration, attempting to mount OneDrive..."
    
    # Mount OneDrive remote in background
    # Note: In production, ensure your rclone.conf has proper OneDrive credentials
    rclone mount ${RCLONE_REMOTE:-onedrive}: /onedrive --daemon --allow-other || {
        echo "⚠️  OneDrive mount failed, continuing with local storage only"
    }
    
    # Wait a moment for mount to stabilize
    sleep 3
    
    # Test if mount is working
    if mountpoint -q /onedrive; then
        echo "✅ OneDrive mounted successfully at /onedrive"
    else
        echo "⚠️  OneDrive not mounted, using local storage"
    fi
else
    echo "⚠️  No rclone configuration found, using local storage only"
    echo "   Mount your rclone config to /root/.config/rclone/rclone.conf"
fi

# Start Telegram bot in background if token is provided
if [ ! -z "$TELEGRAM_TOKEN" ]; then
    echo "🤖 Starting Telegram bot integration..."
    python telegram_bot.py &
    TELEGRAM_PID=$!
    echo "   Telegram bot started with PID: $TELEGRAM_PID"
else
    echo "⚠️  TELEGRAM_TOKEN not set, Telegram integration disabled"
fi

# Start the main Flask bot engine
echo "🔧 Starting Flask API engine on port 5000..."
echo "   Library path: ${LIBRARY_MOUNT:-/onedrive/library}"
echo "   rclone remote: ${RCLONE_REMOTE:-onedrive}"

# Health check function
health_check() {
    curl -sf http://localhost:5000/health > /dev/null
}

# Start Flask app
python bot_engine.py &
FLASK_PID=$!

# Wait for Flask to start
echo "⏳ Waiting for Flask engine to start..."
for _ in {1..30}; do
    if health_check; then
        echo "✅ Cloud Librarian Bot Engine is ready!"
        echo ""
        echo "📋 Service Status:"
        echo "   🔧 Flask API: Running (PID: $FLASK_PID)"
        [ ! -z "$TELEGRAM_TOKEN" ] && echo "   🤖 Telegram Bot: Running (PID: $TELEGRAM_PID)"
        echo "   📂 Library Mount: ${LIBRARY_MOUNT:-/onedrive/library}"
        echo ""
        echo "🌐 API Endpoints:"
        echo "   GET  /health      - Health check"
        echo "   POST /engine      - Main command processor"
        echo "   POST /organize    - Organize code snippets"
        echo "   GET  /search?q=   - Search library"
        echo ""
        break
    fi
    sleep 1
done

# If health check failed
if ! health_check; then
    echo "❌ Failed to start Flask engine"
    exit 1
fi

# Keep container running and monitor processes
while true; do
    # Check if Flask is still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "❌ Flask engine died, restarting..."
        python bot_engine.py &
        FLASK_PID=$!
    fi
    
    # Check if Telegram bot is still running (if it was started)
    if [ ! -z "$TELEGRAM_TOKEN" ] && ! kill -0 "$TELEGRAM_PID" 2>/dev/null; then
        echo "❌ Telegram bot died, restarting..."
        python telegram_bot.py &
        TELEGRAM_PID=$!
    fi
    
    sleep 10
done