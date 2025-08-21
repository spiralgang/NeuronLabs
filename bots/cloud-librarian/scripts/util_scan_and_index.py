#!/usr/bin/env python3
"""
Utility Script for Scanning and Indexing Code Files

This script scans directories for code files and automatically
indexes them in the Cloud Librarian system.
"""

import os
import sys
import json
import hashlib
import requests
from pathlib import Path
import argparse

class CodeScanner:
    def __init__(self, engine_url="http://localhost:5000"):
        self.engine_url = engine_url
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.sh': 'bash',
            '.bash': 'bash',
            '.dockerfile': 'docker',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'text',
            '.sql': 'sql',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust'
        }
        
    def scan_directory(self, directory, recursive=True):
        """Scan directory for code files"""
        directory = Path(directory)
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return []
            
        files = []
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and self.is_code_file(file_path):
                files.append(file_path)
                
        return files
    
    def is_code_file(self, file_path):
        """Check if file is a code file based on extension"""
        return file_path.suffix.lower() in self.supported_extensions
    
    def get_language(self, file_path):
        """Get programming language from file extension"""
        ext = file_path.suffix.lower()
        return self.supported_extensions.get(ext, 'misc')
    
    def read_file_content(self, file_path):
        """Safely read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (UnicodeDecodeError, IOError) as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return None
    
    def extract_tags(self, content, language):
        """Extract tags from code content"""
        tags = [language]
        
        # Language-specific tag extraction
        if language == 'python':
            if 'flask' in content.lower():
                tags.append('flask')
            if 'django' in content.lower():
                tags.append('django')
            if 'fastapi' in content.lower():
                tags.append('fastapi')
            if 'import pandas' in content or 'from pandas' in content:
                tags.append('pandas')
            if 'import numpy' in content or 'from numpy' in content:
                tags.append('numpy')
                
        elif language == 'javascript':
            if 'react' in content.lower():
                tags.append('react')
            if 'vue' in content.lower():
                tags.append('vue')
            if 'angular' in content.lower():
                tags.append('angular')
            if 'node' in content.lower() or 'require(' in content:
                tags.append('nodejs')
                
        elif language == 'docker':
            if 'FROM' in content:
                tags.append('dockerfile')
            if 'docker-compose' in content.lower():
                tags.append('docker-compose')
                
        # Generic tags
        if 'api' in content.lower():
            tags.append('api')
        if 'database' in content.lower() or 'db' in content.lower():
            tags.append('database')
        if 'test' in content.lower():
            tags.append('testing')
            
        return list(set(tags))  # Remove duplicates
    
    def organize_file(self, file_path):
        """Send file to librarian for organization"""
        content = self.read_file_content(file_path)
        if not content:
            return None
            
        language = self.get_language(file_path)
        tags = self.extract_tags(content, language)
        
        data = {
            "snippet": content,
            "filename": file_path.name,
            "tags": tags,
            "language": language,
            "source_path": str(file_path)
        }
        
        try:
            response = requests.post(f"{self.engine_url}/organize", json=data, timeout=30)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to organize {file_path.name}: {e}")
            return None
    
    def scan_and_index(self, directories, dry_run=False):
        """Scan directories and index all code files"""
        all_files = []
        
        # Collect all files
        for directory in directories:
            print(f"🔍 Scanning directory: {directory}")
            files = self.scan_directory(directory)
            all_files.extend(files)
            print(f"   Found {len(files)} code files")
        
        print(f"\n📊 Total files found: {len(all_files)}")
        
        if dry_run:
            print("\n🔍 Dry run - files that would be indexed:")
            for file_path in all_files[:10]:  # Show first 10
                language = self.get_language(file_path)
                print(f"   {file_path.name} ({language})")
            if len(all_files) > 10:
                print(f"   ... and {len(all_files) - 10} more")
            return
        
        # Index files
        success_count = 0
        error_count = 0
        
        print(f"\n📝 Indexing files...")
        for i, file_path in enumerate(all_files, 1):
            print(f"   [{i:3d}/{len(all_files)}] {file_path.name}", end=" ")
            
            result = self.organize_file(file_path)
            if result and "error" not in result:
                print("✅")
                success_count += 1
            else:
                print("❌")
                error_count += 1
                if result:
                    print(f"      Error: {result.get('error', 'Unknown error')}")
        
        print(f"\n📈 Indexing completed:")
        print(f"   ✅ Successfully indexed: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📊 Success rate: {success_count/(success_count+error_count)*100:.1f}%")

def main():
    parser = argparse.ArgumentParser(description="Scan and index code files with Cloud Librarian")
    parser.add_argument("directories", nargs="+", help="Directories to scan")
    parser.add_argument("--engine-url", default="http://localhost:5000", help="Librarian engine URL")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be indexed without actually doing it")
    parser.add_argument("--non-recursive", action="store_true", help="Don't scan subdirectories")
    
    args = parser.parse_args()
    
    # Check if engine is reachable
    scanner = CodeScanner(args.engine_url)
    try:
        response = requests.get(f"{args.engine_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Librarian engine not reachable at {args.engine_url}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ Librarian engine not reachable at {args.engine_url}")
        sys.exit(1)
    
    print("✅ Connected to Cloud Librarian engine")
    
    # Scan and index
    scanner.scan_and_index(args.directories, args.dry_run)

if __name__ == "__main__":
    main()