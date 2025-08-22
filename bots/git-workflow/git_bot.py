#!/usr/bin/env python3
"""
Git Workflow Bot - Automated Git operations and workflow management

This bot handles:
- Branch management and merging
- Automated commit patterns
- Pull request workflows
- Release management
- Code quality checks
- Automated versioning
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)

class GitWorkflowBot:
    def __init__(self):
        self.conventional_commit_types = {
            'feat': 'A new feature',
            'fix': 'A bug fix', 
            'docs': 'Documentation only changes',
            'style': 'Changes that do not affect the meaning of the code',
            'refactor': 'A code change that neither fixes a bug nor adds a feature',
            'test': 'Adding missing tests or correcting existing tests',
            'chore': 'Changes to the build process or auxiliary tools'
        }
    
    def check_git_repo(self, path='.'):
        """Check if directory is a git repository"""
        git_dir = Path(path) / '.git'
        return git_dir.exists()
    
    def run_git_command(self, cmd, path='.'):
        """Run git command and return result"""
        try:
        """Run git command and return result. Expects cmd as a list of arguments."""
        try:
            result = subprocess.run(cmd, cwd=path, capture_output=True, text=True)
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip()
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    def init_repository(self, data):
        """Initialize a new git repository"""
        path = data.get('path', '.')
        
        if self.check_git_repo(path):
            return {"error": "Git repository already exists"}
        
        commands = [
            "git init",
            "git config user.name 'Automation Bot'",
            "git config user.email 'bot@neuronlabs.dev'"
        ]
        
        results = []
        for cmd in commands:
            result = self.run_git_command(cmd, path)
            results.append({"command": cmd, "result": result})
            if not result["success"]:
                return {"error": f"Failed to execute: {cmd}", "details": result["error"]}
        
        return {
            "status": "repository_initialized",
            "path": path,
            "results": results
        }
    
    def create_branch(self, data):
        """Create and optionally switch to a new branch"""
        path = data.get('path', '.')
        branch_name = data.get('branch_name')
        switch = data.get('switch', True)
        
        if not branch_name:
            return {"error": "Branch name required"}
        
        if not self.check_git_repo(path):
            return {"error": "Not a git repository"}
        
        # Validate branch name
        if not re.match(r'^[a-zA-Z0-9/_-]+$', branch_name):
            return {"error": "Invalid branch name"}
        
        cmd = f"git checkout -b {branch_name}" if switch else f"git branch {branch_name}"
        result = self.run_git_command(cmd, path)
        
        if not result["success"]:
            return {"error": f"Failed to create branch: {result['error']}"}
        
        return {
            "status": "branch_created",
            "branch_name": branch_name,
            "switched": switch,
            "output": result["output"]
        }
    
    def commit_changes(self, data):
        """Create a conventional commit"""
        path = data.get('path', '.')
        commit_type = data.get('type', 'feat')
        scope = data.get('scope', '')
        description = data.get('description', '')
        body = data.get('body', '')
        breaking = data.get('breaking', False)
        
        if not self.check_git_repo(path):
            return {"error": "Not a git repository"}
        
        if commit_type not in self.conventional_commit_types:
            return {"error": f"Invalid commit type. Valid types: {list(self.conventional_commit_types.keys())}"}
        
        if not description:
            return {"error": "Commit description required"}
        
        # Build conventional commit message
        scope_part = f"({scope})" if scope else ""
        breaking_part = "!" if breaking else ""
        commit_msg = f"{commit_type}{scope_part}{breaking_part}: {description}"
        
        if body:
            commit_msg += f"\n\n{body}"
        
        if breaking:
            commit_msg += f"\n\nBREAKING CHANGE: {description}"
        
        # Stage all changes and commit
        commands = [
            "git add .",
            f"git commit -m '{commit_msg}'"
        ]
        
        for cmd in commands:
            result = self.run_git_command(cmd, path)
            if not result["success"]:
                return {"error": f"Failed to execute: {cmd}", "details": result["error"]}
        
        # Get commit hash
        hash_result = self.run_git_command("git rev-parse --short HEAD", path)
        commit_hash = hash_result["output"] if hash_result["success"] else "unknown"
        
        return {
            "status": "changes_committed",
            "commit_type": commit_type,
            "description": description,
            "commit_hash": commit_hash,
            "message": commit_msg
        }
    
            if not source_branch or not self.check_git_repo(path):
        """Merge one branch into another"""
        path = data.get('path', '.')
        source_branch = data.get('source_branch')
        target_branch = data.get('target_branch', 'main')
        strategy = data.get('strategy', 'merge')  # merge, squash, rebase
        
        if not source_branch:
            return {"error": "Source branch required"}
        
        if not self.check_git_repo(path):
            return {"error": "Not a git repository"}
        
        # Switch to target branch
        switch_result = self.run_git_command(f"git checkout {target_branch}", path)
        if not switch_result["success"]:
            return {"error": f"Failed to switch to {target_branch}: {switch_result['error']}"}
        
        # Perform merge
        if strategy == "squash":
            merge_cmd = f"git merge --squash {source_branch}"
        elif strategy == "rebase":
            merge_cmd = f"git rebase {source_branch}"
        else:
            merge_cmd = f"git merge {source_branch}"
        
        merge_result = self.run_git_command(merge_cmd, path)
        
        if not merge_result["success"]:
            return {"error": f"Merge failed: {merge_result['error']}"}
        
        # If squash merge, need to commit
        if strategy == "squash":
            commit_result = self.run_git_command(f"git commit -m 'Merge {source_branch} into {target_branch}'", path)
            if not commit_result["success"]:
                return {"error": f"Failed to commit squash merge: {commit_result['error']}"}
        
        return {
            "status": "branches_merged",
            "source_branch": source_branch,
            "target_branch": target_branch,
            "strategy": strategy,
            "output": merge_result["output"]
        }
    
    def create_tag(self, data):
        """Create a version tag"""
        path = data.get('path', '.')
        tag_name = data.get('tag_name')
        message = data.get('message', '')
        
        if not tag_name:
            return {"error": "Tag name required"}
        
        if not self.check_git_repo(path):
            return {"error": "Not a git repository"}
        
        # Validate semantic version format
        if not re.match(r'^v?\d+\.\d+\.\d+', tag_name):
            return {"error": "Tag should follow semantic versioning (e.g., v1.0.0)"}
        
        cmd = f"git tag -a {tag_name} -m '{message or tag_name}'"
        result = self.run_git_command(cmd, path)
        
        if not result["success"]:
            return {"error": f"Failed to create tag: {result['error']}"}
        
        return {
            "status": "tag_created",
            "tag_name": tag_name,
            "message": message or tag_name
        }
    
    def get_repo_status(self, data):
        """Get comprehensive repository status"""
        path = data.get('path', '.')
        
        if not self.check_git_repo(path):
            return {"error": "Not a git repository"}
        
        status_info = {}
        
        # Current branch
        branch_result = self.run_git_command("git branch --show-current", path)
        status_info["current_branch"] = branch_result["output"] if branch_result["success"] else "unknown"
        
        # Git status
        status_result = self.run_git_command("git status --porcelain", path)
        if status_result["success"]:
            lines = status_result["output"].split('\n') if status_result["output"] else []
            status_info["changes"] = {
                "modified": [line[3:] for line in lines if line.startswith(' M')],
                "added": [line[3:] for line in lines if line.startswith('A ')],
                "deleted": [line[3:] for line in lines if line.startswith(' D')],
                "untracked": [line[3:] for line in lines if line.startswith('??')]
            }
            status_info["clean"] = len(lines) == 0
        
        # Recent commits
        log_result = self.run_git_command("git log --oneline -n 5", path)
        if log_result["success"]:
            status_info["recent_commits"] = log_result["output"].split('\n') if log_result["output"] else []
        
        # All branches
        branches_result = self.run_git_command("git branch -a", path)
        if branches_result["success"]:
            status_info["branches"] = [
                branch.strip().replace('* ', '') 
                for branch in branches_result["output"].split('\n') 
                if branch.strip()
            ]
        
        # Tags
        tags_result = self.run_git_command("git tag -l", path)
        if tags_result["success"]:
            status_info["tags"] = tags_result["output"].split('\n') if tags_result["output"] else []
        
        return {
            "status": "repo_status_retrieved",
            "path": path,
            "info": status_info
        }
    
    def auto_version_bump(self, data):
        """Automatically bump version based on commit history"""
        path = data.get('path', '.')
        bump_type = data.get('type', 'auto')  # major, minor, patch, auto
        
        if not self.check_git_repo(path):
            return {"error": "Not a git repository"}
        
        # Get current version from tags
        tags_result = self.run_git_command("git tag -l --sort=-version:refname", path)
        if not tags_result["success"]:
            current_version = "v0.0.0"
        else:
            tags = [tag for tag in tags_result["output"].split('\n') if tag.startswith('v')]
            current_version = tags[0] if tags else "v0.0.0"
        
        # Parse current version
        version_match = re.match(r'v(\d+)\.(\d+)\.(\d+)', current_version)
        if not version_match:
            return {"error": f"Invalid current version format: {current_version}"}
        
        major, minor, patch = map(int, version_match.groups())
        
        # Auto-detect bump type from recent commits
        if bump_type == 'auto':
            commits_result = self.run_git_command("git log --oneline --since='1 week ago'", path)
            if commits_result["success"]:
                commits = commits_result["output"]
                if 'BREAKING CHANGE' in commits or re.search(r'\w+!:', commits):
                    bump_type = 'major'
                elif re.search(r'feat[\(\:]', commits):
                    bump_type = 'minor'
                else:
                    bump_type = 'patch'
            else:
                bump_type = 'patch'
        
        # Calculate new version
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        
        new_version = f"v{major}.{minor}.{patch}"
        
        # Create tag
        tag_result = self.run_git_command(f"git tag -a {new_version} -m 'Release {new_version}'", path)
        if not tag_result["success"]:
            return {"error": f"Failed to create version tag: {tag_result['error']}"}
        
        return {
            "status": "version_bumped",
            "previous_version": current_version,
            "new_version": new_version,
            "bump_type": bump_type
        }

# Initialize bot
git_bot = GitWorkflowBot()

def process_command(command, data):
    """Process Git workflow commands"""
    if command == "init":
        return git_bot.init_repository(data)
    elif command == "create_branch":
        return git_bot.create_branch(data)
    elif command == "commit":
        return git_bot.commit_changes(data)
    elif command == "merge":
        return git_bot.merge_branch(data)
    elif command == "tag":
        return git_bot.create_tag(data)
    elif command == "status":
        return git_bot.get_repo_status(data)
    elif command == "version_bump":
        return git_bot.auto_version_bump(data)
    else:
        return {"error": f"Unknown command: {command}"}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "git-workflow-bot",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/git", methods=["POST"])
def git_endpoint():
    req = request.json
    if not req:
        return jsonify({"error": "No JSON data provided"}), 400
    
    command = req.get("command")
    if not command:
        return jsonify({"error": "No command specified"}), 400
    
    response = process_command(command, req)
    return jsonify(response)

if __name__ == "__main__":
    print("🔧 Starting Git Workflow Bot...")
    app.run(host="127.0.0.1", port=5003, debug=False)