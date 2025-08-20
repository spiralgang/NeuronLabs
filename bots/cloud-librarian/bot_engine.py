#!/usr/bin/env python3
"""
Bot Engine for Cloudspace Librarian Service

This script demonstrates:
  - Initialization of a local "library" area on a cloudspace mount (via rclone)
  - Basic command handling and auto-integration with external interfaces (e.g., Telegram)
  - An engine calling function structure to process requests
"""

import os
import time
import logging
import json
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify
import subprocess

# -- Engine configuration --
LIBRARY_MOUNT = os.getenv("LIBRARY_MOUNT", "/onedrive/library")
RCLONE_REMOTE = os.getenv("RCLONE_REMOTE", "onedrive")

# Create a Flask app for webhooks/HTTP-based interactions
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloud_librarian")

class CloudLibrarian:
    def __init__(self):
        self.library_path = LIBRARY_MOUNT
        self.index_file = os.path.join(self.library_path, "index.json")
        self.ensure_library_structure()
        
    def ensure_library_structure(self):
        """Create library directory structure if it doesn't exist"""
        os.makedirs(self.library_path, exist_ok=True)
        os.makedirs(os.path.join(self.library_path, "python"), exist_ok=True)
        os.makedirs(os.path.join(self.library_path, "javascript"), exist_ok=True)
        os.makedirs(os.path.join(self.library_path, "bash"), exist_ok=True)
        os.makedirs(os.path.join(self.library_path, "docker"), exist_ok=True)
        os.makedirs(os.path.join(self.library_path, "misc"), exist_ok=True)
        
    def load_index(self):
        """Load the code library index"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                logger.warning("Could not load index, creating new one")
        return {"files": {}, "tags": {}, "last_updated": None}
    
    def save_index(self, index):
        """Save the code library index"""
        index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def organize_code(self, data):
        """
        Organize, index, or ingest a new code snippet into the library.
        Automatically detects language and organizes accordingly.
        """
        snippet = data.get("snippet", "")
        filename = data.get("filename", "")
        tags = data.get("tags", [])
        
        if not snippet and not filename:
            return {"error": "No snippet or filename provided"}
        
        # Auto-detect language and determine directory
        language = self.detect_language(snippet, filename)
        target_dir = os.path.join(self.library_path, language)
        
        # Generate filename if not provided
        if not filename:
            snippet_hash = hashlib.md5(snippet.encode()).hexdigest()[:8]
            filename = f"snippet_{snippet_hash}.{self.get_extension(language)}"
        
        file_path = os.path.join(target_dir, filename)
        
        # Save the file
        with open(file_path, 'w') as f:
            f.write(snippet)
        
        # Update index
        index = self.load_index()
        file_info = {
            "path": file_path,
            "language": language,
            "tags": tags,
            "size": len(snippet),
            "created": datetime.now().isoformat(),
            "hash": hashlib.md5(snippet.encode()).hexdigest()
        }
        
        index["files"][filename] = file_info
        for tag in tags:
            if tag not in index["tags"]:
                index["tags"][tag] = []
            index["tags"][tag].append(filename)
        
        self.save_index(index)
        
        logger.info(f"Organized code snippet: {filename} in {language} directory")
        return {
            "status": "organized",
            "filename": filename,
            "language": language,
            "path": file_path
        }
    
    def search_code(self, data):
        """Search through the code library"""
        query = data.get("query", "")
        language = data.get("language")
        tags = data.get("tags", [])
        
        index = self.load_index()
        results = []
        
        for filename, file_info in index["files"].items():
            match_score = 0
            
            # Language filter
            if language and file_info["language"] != language:
                continue
                
            # Tag filter
            if tags and not any(tag in file_info["tags"] for tag in tags):
                continue
                
            # Text search in filename
            if query.lower() in filename.lower():
                match_score += 10
                
            # Text search in tags
            if any(query.lower() in tag.lower() for tag in file_info["tags"]):
                match_score += 5
                
            if match_score > 0 or not query:
                results.append({
                    "filename": filename,
                    "info": file_info,
                    "score": match_score
                })
        
        # Sort by match score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "status": "search_complete",
            "query": query,
            "results_count": len(results),
            "results": results[:20]  # Limit to top 20 results
        }
    
    def backup_library(self, data):
        """Create a backup of the library"""
        backup_name = data.get("name", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        try:
            # Use rclone to sync to a backup directory
            backup_path = f"{RCLONE_REMOTE}:backups/{backup_name}"
            result = subprocess.run([
                "rclone", "sync", self.library_path, backup_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "backup_complete",
                    "backup_name": backup_name,
                    "backup_path": backup_path
                }
            else:
                return {
                    "error": "Backup failed",
                    "details": result.stderr
                }
        except Exception as e:
            return {"error": f"Backup failed: {str(e)}"}
    
    def sync_library(self, data):
        """Synchronize library with OneDrive"""
        try:
            result = subprocess.run([
                "rclone", "sync", self.library_path, f"{RCLONE_REMOTE}:library"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "sync_complete",
                    "message": "Library synchronized with OneDrive"
                }
            else:
                return {
                    "error": "Sync failed",
                    "details": result.stderr
                }
        except Exception as e:
            return {"error": f"Sync failed: {str(e)}"}
    
    def detect_language(self, snippet, filename=""):
        """Detect programming language from snippet or filename"""
        if filename:
            ext = filename.split('.')[-1].lower()
            ext_map = {
                'py': 'python', 'js': 'javascript', 'sh': 'bash',
                'dockerfile': 'docker', 'yml': 'docker', 'yaml': 'docker'
            }
            if ext in ext_map:
                return ext_map[ext]
        
        # Simple content-based detection
        if snippet:
            if 'def ' in snippet or 'import ' in snippet:
                return 'python'
            elif 'function' in snippet or 'const ' in snippet:
                return 'javascript'
            elif '#!/bin/bash' in snippet or 'echo ' in snippet:
                return 'bash'
            elif 'FROM ' in snippet or 'RUN ' in snippet:
                return 'docker'
        
        return 'misc'
    
    def get_extension(self, language):
        """Get file extension for language"""
        ext_map = {
            'python': 'py',
            'javascript': 'js',
            'bash': 'sh',
            'docker': 'dockerfile',
            'misc': 'txt'
        }
        return ext_map.get(language, 'txt')

# Initialize the librarian
librarian = CloudLibrarian()

def call_engine_function(command, data):
    """
    Routing function which calls different engines based on the command.
    """
    if command == "organize":
        return librarian.organize_code(data)
    elif command == "search":
        return librarian.search_code(data)
    elif command == "backup":
        return librarian.backup_library(data)
    elif command == "sync":
        return librarian.sync_library(data)
    else:
        return {"error": f"Unknown command: {command}"}

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "cloud-librarian",
        "library_path": LIBRARY_MOUNT,
        "timestamp": datetime.now().isoformat()
    })

# Main engine endpoint
@app.route("/engine", methods=["POST"])
def engine():
    req = request.json
    if not req:
        return jsonify({"error": "No JSON data provided"}), 400

    command = req.get("command")
    if not command:
        return jsonify({"error": "No command specified"}), 400

    logger.info("Received command: %s", command)
    response = call_engine_function(command, req)
    return jsonify(response)

# Specific endpoints for common operations
@app.route("/organize", methods=["POST"])
def organize():
    data = request.json or {}
    data["command"] = "organize"
    return jsonify(call_engine_function("organize", data))

@app.route("/search", methods=["GET"])
def search():
    data = {
        "query": request.args.get("q", ""),
        "language": request.args.get("lang"),
        "tags": request.args.get("tags", "").split(",") if request.args.get("tags") else []
    }
    return jsonify(call_engine_function("search", data))

if __name__ == "__main__":
    # Ensure library directory exists
    if not os.path.exists(LIBRARY_MOUNT):
        os.makedirs(LIBRARY_MOUNT, exist_ok=True)
    
    logger.info("Starting Cloud Librarian Bot Engine with library mount at: %s", LIBRARY_MOUNT)
    
    # Run the Flask app; in production, use a proper WSGI server
    app.run(host="0.0.0.0", port=5000, debug=False)