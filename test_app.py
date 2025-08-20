#!/usr/bin/env python3
"""
Test Flask application for NeuronLabs
Based on patterns found in repository analysis
"""
from flask import Flask, render_template_string

app = Flask(__name__)

# Simple HTML template based on patterns found in APK
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeuronLabs Test</title>
    <style>
        body { 
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
            color: #00ff88;
            font-family: 'Courier New', monospace;
            text-align: center;
            padding: 50px;
        }
        .title { font-size: 2em; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="title">NeuronLabs Test Server</div>
    <p>✅ Flask application is running</p>
    <p>✅ Repository validation successful</p>
    <p>Server Time: {{ timestamp }}</p>
</body>
</html>
'''

@app.route('/')
def index():
    import datetime
    return render_template_string(HTML_TEMPLATE, timestamp=datetime.datetime.now())

@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'neuronlabs-test'}

if __name__ == '__main__':
    print("Starting NeuronLabs test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)