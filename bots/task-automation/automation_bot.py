#!/usr/bin/env python3
"""
Task Automation Bot - Handles repetitive development tasks

This bot automates common development workflows including:
- Project scaffolding
- Dependency management  
- Code formatting and linting
- Test execution
- Build processes
- Deployment tasks
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

class TaskAutomationBot:
    def __init__(self):
        self.supported_languages = ['python', 'javascript', 'typescript', 'go', 'rust']
        self.templates = {
            'python': {
                'files': {
                    'main.py': '#!/usr/bin/env python3\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()',
                    'requirements.txt': '# Add your dependencies here\n',
                    'README.md': '# {project_name}\n\nDescription of your project.',
                    '.gitignore': '__pycache__/\n*.pyc\n*.pyo\n*.pyd\n.env\nvenv/\n.venv/\ndist/\nbuild/\n*.egg-info/'
                },
                'commands': {
                    'install': 'pip install -r requirements.txt',
                    'format': 'black .',
                    'lint': 'flake8 .',
                    'test': 'pytest',
                    'run': 'python main.py'
                }
            },
            'javascript': {
                'files': {
                    'index.js': 'console.log("Hello, World!");',
                    'package.json': '{\n  "name": "{project_name}",\n  "version": "1.0.0",\n  "main": "index.js",\n  "scripts": {\n    "start": "node index.js",\n    "test": "jest"\n  }\n}',
                    'README.md': '# {project_name}\n\nDescription of your project.',
                    '.gitignore': 'node_modules/\n*.log\ndist/\nbuild/\n.env\n.DS_Store'
                },
                'commands': {
                    'install': 'npm install',
                    'format': 'prettier --write .',
                    'lint': 'eslint .',
                    'test': 'npm test',
                    'run': 'npm start'
                }
            }
        }
    
    def create_project(self, data):
        """Create a new project from template"""
        project_name = data.get('name', 'new-project')
        language = data.get('language', 'python')
        base_path = data.get('path', '.')
        
        if language not in self.supported_languages:
            return {"error": f"Unsupported language: {language}"}
        
        project_path = Path(base_path) / project_name
        
        if project_path.exists():
            return {"error": f"Project directory already exists: {project_path}"}
        
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create files from template
            template = self.templates.get(language, self.templates['python'])
            created_files = []
            
            for filename, content in template['files'].items():
                file_path = project_path / filename
                formatted_content = content.format(project_name=project_name)
                
                with open(file_path, 'w') as f:
                    f.write(formatted_content)
                created_files.append(str(file_path))
            
            # Initialize git repository
            try:
                subprocess.run(['git', 'init'], cwd=project_path, check=True, capture_output=True)
                subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
                subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=project_path, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                pass  # Git operations are optional
            
            return {
                "status": "project_created",
                "project_name": project_name,
                "language": language,
                "path": str(project_path),
                "files_created": created_files,
                "next_steps": template['commands']
            }
            
        except Exception as e:
            return {"error": f"Failed to create project: {str(e)}"}
    
    def install_dependencies(self, data):
        """Install project dependencies"""
        project_path = Path(data.get('path', '.'))
        language = data.get('language', 'auto')
        
        # Auto-detect language if not specified
        if language == 'auto':
            if (project_path / 'package.json').exists():
                language = 'javascript'
            elif (project_path / 'requirements.txt').exists():
                language = 'python'
            elif (project_path / 'Cargo.toml').exists():
                language = 'rust'
            elif (project_path / 'go.mod').exists():
                language = 'go'
            else:
                return {"error": "Could not detect project language"}
        
        try:
            if language == 'python':
                result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                                      cwd=project_path, capture_output=True, text=True)
            elif language == 'javascript':
                result = subprocess.run(['npm', 'install'], 
                                      cwd=project_path, capture_output=True, text=True)
            elif language == 'rust':
                result = subprocess.run(['cargo', 'build'], 
                                      cwd=project_path, capture_output=True, text=True)
            elif language == 'go':
                result = subprocess.run(['go', 'mod', 'tidy'], 
                                      cwd=project_path, capture_output=True, text=True)
            else:
                return {"error": f"Unsupported language for dependency installation: {language}"}
            
            return {
                "status": "dependencies_installed",
                "language": language,
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
            
        except Exception as e:
            return {"error": f"Failed to install dependencies: {str(e)}"}
    
    def format_code(self, data):
        """Format code in project"""
        project_path = Path(data.get('path', '.'))
        language = data.get('language', 'auto')
        
        # Auto-detect language
        if language == 'auto':
            if any(project_path.glob('*.py')):
                language = 'python'
            elif any(project_path.glob('*.js')) or any(project_path.glob('*.ts')):
                language = 'javascript'
            else:
                return {"error": "Could not detect language for formatting"}
        
        try:
            if language == 'python':
                # Try black first, then autopep8
                formatters = [
                    ['black', '.'],
                    ['autopep8', '--in-place', '--recursive', '.']
                ]
            elif language in ['javascript', 'typescript']:
                formatters = [
                    ['prettier', '--write', '.'],
                    ['eslint', '--fix', '.']
                ]
            else:
                return {"error": f"No formatter configured for {language}"}
            
            results = []
            for formatter in formatters:
                try:
                    result = subprocess.run(formatter, cwd=project_path, 
                                          capture_output=True, text=True, timeout=60)
                    results.append({
                        "tool": formatter[0],
                        "success": result.returncode == 0,
                        "output": result.stdout
                    })
                    if result.returncode == 0:
                        break  # Use first successful formatter
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    results.append({
                        "tool": formatter[0],
                        "success": False,
                        "error": "Tool not found or timed out"
                    })
            
            return {
                "status": "formatting_complete",
                "language": language,
                "results": results
            }
            
        except Exception as e:
            return {"error": f"Failed to format code: {str(e)}"}
    
    def run_tests(self, data):
        """Run tests for project"""
        project_path = Path(data.get('path', '.'))
        language = data.get('language', 'auto')
        
        # Auto-detect language
        if language == 'auto':
            if (project_path / 'pytest.ini').exists() or any(project_path.glob('test_*.py')):
                language = 'python'
            elif (project_path / 'package.json').exists():
                language = 'javascript'
            else:
                return {"error": "Could not detect test framework"}
        
        try:
            if language == 'python':
                test_commands = ['pytest -v', 'python -m unittest discover', 'python -m pytest']
            elif language == 'javascript':
                test_commands = ['npm test', 'yarn test', 'jest']
            else:
                return {"error": f"No test runner configured for {language}"}
            
            for cmd in test_commands:
                try:
                    result = subprocess.run(cmd.split(), cwd=project_path, 
                                          capture_output=True, text=True, timeout=120)
                    
                    return {
                        "status": "tests_complete",
                        "language": language,
                        "command": cmd,
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "errors": result.stderr
                    }
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return {"error": "No working test runner found"}
            
        except Exception as e:
            return {"error": f"Failed to run tests: {str(e)}"}
    
    def analyze_project(self, data):
        """Analyze project structure and health"""
        project_path = Path(data.get('path', '.'))
        
        if not project_path.exists():
            return {"error": "Project path does not exist"}
        
        analysis = {
            "path": str(project_path),
            "languages": [],
            "frameworks": [],
            "files": {
                "total": 0,
                "by_extension": {}
            },
            "dependencies": {},
            "git": {
                "initialized": False,
                "commits": 0,
                "branch": None
            },
            "recommendations": []
        }
        
        # Analyze files
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                analysis["files"]["total"] += 1
                ext = file_path.suffix.lower()
                analysis["files"]["by_extension"][ext] = analysis["files"]["by_extension"].get(ext, 0) + 1
        
        # Detect languages
        if analysis["files"]["by_extension"].get('.py', 0) > 0:
            analysis["languages"].append('python')
        if analysis["files"]["by_extension"].get('.js', 0) > 0:
            analysis["languages"].append('javascript')
        if analysis["files"]["by_extension"].get('.ts', 0) > 0:
            analysis["languages"].append('typescript')
        
        # Check for dependency files and frameworks
        if (project_path / 'requirements.txt').exists():
            analysis["frameworks"].append('python-pip')
        if (project_path / 'package.json').exists():
            analysis["frameworks"].append('nodejs')
        if (project_path / 'Cargo.toml').exists():
            analysis["frameworks"].append('rust')
        
        # Git analysis
        git_dir = project_path / '.git'
        if git_dir.exists():
            analysis["git"]["initialized"] = True
            try:
                result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], 
                                      cwd=project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    analysis["git"]["commits"] = int(result.stdout.strip())
            except:
                pass
        
        # Generate recommendations
        if not analysis["git"]["initialized"]:
            analysis["recommendations"].append("Initialize Git repository")
        if not (project_path / 'README.md').exists():
            analysis["recommendations"].append("Add README.md file")
        if 'python' in analysis["languages"] and not (project_path / 'requirements.txt').exists():
            analysis["recommendations"].append("Add requirements.txt file")
        
        return {
            "status": "analysis_complete",
            "analysis": analysis
        }

# Initialize bot
automation_bot = TaskAutomationBot()

def process_command(command, data):
    """Process automation commands"""
    if command == "create_project":
        return automation_bot.create_project(data)
    elif command == "install_deps":
        return automation_bot.install_dependencies(data)
    elif command == "format":
        return automation_bot.format_code(data)
    elif command == "test":
        return automation_bot.run_tests(data)
    elif command == "analyze":
        return automation_bot.analyze_project(data)
    else:
        return {"error": f"Unknown command: {command}"}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "task-automation-bot",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/automation", methods=["POST"])
def automation():
    req = request.json
    if not req:
        return jsonify({"error": "No JSON data provided"}), 400
    
    command = req.get("command")
    if not command:
        return jsonify({"error": "No command specified"}), 400
    
    response = process_command(command, req)
    return jsonify(response)

if __name__ == "__main__":
    print("🤖 Starting Task Automation Bot...")
    app.run(host="0.0.0.0", port=5001, debug=False)