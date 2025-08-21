# NeuronLabs Development Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Repository Overview
NeuronLabs is an AI-powered Android application development project featuring:
- Android APK builds (NeuronLabs_Working.apk, GhostEdgeModern.apk, etc.)  
- Web-based AI interfaces with Flask backends
- Docker containerization and bot registry systems
- GitHub Codespaces integration with multi-language support

### Essential Setup Commands
Run these commands in order to bootstrap the development environment:

```bash
# Verify development environment
python3 --version  # Should show Python 3.12+
node --version     # Should show Node.js 20.x
docker --version   # Should show Docker 28.0+
docker compose version  # Should show Docker Compose v2.38+

# Install dependencies (if requirements.txt exists)
pip3 install -r requirements.txt || echo "No requirements.txt found"

# Install Node.js dependencies (if package.json exists)
npm install || echo "No package.json found"

# Test bot registry system
chmod +x bots_registry-əə.sh
./bots_registry-əə.sh  # Scans and registers bots in ./bots/ directory
```

**TIMING**: Initial setup takes 30-60 seconds. Dependencies install takes 1-5 minutes depending on requirements.

### Build Commands

#### Docker Builds
```bash
# Simple container build (validated working)
docker build -f Dockerfile.simple -t neuronlabs-simple .
# Takes 2-5 minutes. NEVER CANCEL - wait for completion.

# Test container execution
docker run --rm neuronlabs-simple
```

**CRITICAL**: Docker builds that require network access may fail due to SSL certificate issues. Use offline or pre-cached builds when possible.

#### Python Development
```bash
# Validate Python syntax
python3 -m py_compile *.py

# Run Flask applications
python3 test_app.py  # Starts on port 5000

# Install specific packages 
pip3 install flask requests  # Takes 3-10 seconds
```

#### Node.js Development  
```bash
# Validate package.json
npm test  # Runs defined test scripts

# Syntax check
node -c package.json || echo "Invalid JSON"
```

### Testing Commands

#### Bot Registry System
```bash
# Create a test bot
mkdir -p bots
cat > bots/test_bot << 'EOF'
#!/bin/bash
if [ "$1" = "--audit" ]; then
  echo "Test bot v1.0 - audit passed"  
else
  echo "Test bot executing..."
fi
EOF
chmod +x bots/test_bot

# Register and audit bots
./bots_registry-əə.sh  # Takes 1-5 seconds per bot
```

#### Application Testing  
```bash
# Test Flask health endpoints
curl -s http://localhost:5000/health

# Validate APK structure (without Android SDK)
unzip -l *.apk | head -20
```

### Validation Scenarios

Always run these validation steps after making changes:

1. **Python Application Test**: 
   - Start Flask app: `python3 test_app.py`
   - Test health endpoint: `curl http://localhost:5000/health`
   - Should return `{"status": "ok", "service": "neuronlabs-test"}`

2. **Container Validation**:
   - Build test image: `docker build -f Dockerfile.simple -t test .`
   - Run container: `docker run --rm test`
   - Should output "NeuronLabs container test successful"

3. **Bot Registry Validation**:
   - Run registry: `./bots_registry-əə.sh`
   - Check logs: `cat bots_registry-əə.log`
   - Verify bots are registered with SHA256 checksums

## Critical Build Information

### Timing Expectations
- **NEVER CANCEL**: Docker builds take 2-15 minutes depending on complexity
- **NEVER CANCEL**: APK analysis/extraction takes 30-120 seconds for large files
- Bot registry scans: 1-10 seconds
- Python dependency installs: 3-60 seconds
- Node.js installs: 1-5 seconds

### Network Limitations
- Docker builds requiring PyPI/npm may fail due to SSL certificate issues
- Use `--trusted-host` flags or offline installations when needed
- APK extraction and local operations always work

### File Structure
```
NeuronLabs/
├── *.apk                   # Android application packages
├── bots_registry-əə.sh     # Bot discovery and registration
├── bots/                   # Executable bot scripts
├── .devcontainer/          # GitHub Codespaces configuration
├── requirements.txt        # Python dependencies (if present)
├── package.json           # Node.js dependencies (if present)
└── test_app.py            # Flask test application
```

## Common Tasks

### APK Analysis
```bash
# List APK contents
unzip -l NeuronLabs_Working.apk | head -20

# Extract specific files
unzip NeuronLabs_Working.apk assets/index.html

# Check APK file type
file *.apk
```

### Container Operations
```bash
# List running containers
docker ps

# Stop all containers
docker stop $(docker ps -q)

# Clean up images
docker system prune -f
```

### Development Server
```bash
# Start Flask development server
python3 test_app.py
# Access at http://localhost:5000

# Environment variables are pre-configured:
# BACKEND_URL, NODE_SERVICE_URL, FLASK_URL
```

## Port Configuration
- **5000**: Flask applications
- **8329**: Node.js services  
- **8330**: Backend services
- **8340**: Additional services

## Known Issues
- Android SDK not available at `/usr/local/android-sdk` (devcontainer config references missing path)
- Network-dependent Docker builds may fail with SSL errors
- Some devcontainer commands reference missing requirements.txt/package.json files

## Validation Checklist
Before committing changes, always run:
- [ ] `python3 -m py_compile *.py` (syntax check)
- [ ] `./bots_registry-əə.sh` (bot registration)
- [ ] `docker build -f Dockerfile.simple -t test .` (container build)
- [ ] `curl http://localhost:5000/health` (if Flask app running)
- [ ] Manual verification of core user scenarios

## Manual Validation Requirements
After building and running applications, execute these complete user scenarios:
1. **Web Interface**: Start Flask app, verify HTML renders correctly with NeuronLabs branding
2. **Bot System**: Create, register, and execute a test bot successfully  
3. **Container Workflow**: Build and run a complete Docker container
4. **APK Inspection**: Extract and verify APK contents match expected structure

Always test actual functionality, not just startup/shutdown procedures.