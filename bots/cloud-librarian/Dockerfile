# Use an official Python slim image
FROM python:3.9-slim

# Install system dependencies, including rclone and fuse for mounting
RUN apt-get update && \
    apt-get install -y rclone fuse curl && \
    rm -rf /var/lib/apt/lists/*

# Set workdir and install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY bot_engine.py .
COPY telegram_bot.py .
COPY entrypoint.sh .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Create necessary directories
RUN mkdir -p /onedrive/library /root/.config/rclone

# Expose port 5000 for Flask
EXPOSE 5000

# Use the entrypoint script as command
ENTRYPOINT ["./entrypoint.sh"]