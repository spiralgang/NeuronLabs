# Configuration Directory

This directory contains configuration files and environment settings for the NeuronLabs project.

## Files

### Environment Configuration
- `environment_urls.txt` - Backend service URLs and endpoints
  - Backend URL: Service backend endpoint
  - Node Service URL: Node.js service endpoint  
  - Flask URL: Flask application endpoint

## Usage

These configuration files are used to set up development and production environments.

### Environment Variables
The URLs in `environment_urls.txt` should be set as environment variables:

```bash
export BACKEND_URL="https://your-backend-url"
export NODE_SERVICE_URL="https://your-node-service-url"
export FLASK_URL="https://your-flask-url"
```

## Security

- Never commit sensitive credentials to version control
- Use environment-specific configuration files
- Rotate service URLs regularly for production environments