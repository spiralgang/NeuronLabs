{
  "name": "NeuronLabs Codespace",
  "features": {
    "ghcr.io/devcontainers/features/python:1": { "version": "3.11" },
    "ghcr.io/devcontainers/features/node:1": { "version": "20" },
    "ghcr.io/devcontainers/features/android:1": { "version": "33.0.2" }
  },
  "forwardPorts": [8330, 8329, 5000, 8340],
  "postCreateCommand": "pip install -r requirements.txt || true && npm install || true",
  "remoteEnv": {
    "BACKEND_URL": "https://8330-iirrm6xp04qvn5736a43c-96bf24aa.manusvm.computer:8330",
    "NODE_SERVICE_URL": "https://8330-iirrm6xp04qvn5736a43c-96bf24aa.manusvm.computer:8329",
    "FLASK_URL": "https://8330-iirrm6xp04qvn5736a43c-96bf24aa.manusvm.computer:5000"
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.flake8",
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint",
        "redhat.vscode-yaml",
        "ms-androidtools.vscode-android",
        "ms-vscode.cpptools",
        "streetsidesoftware.code-spell-checker",
        "eamodio.gitlens"
      ],
      "settings": {
        "python.formatting.provider": "black",
        "python.linting.flake8Enabled": true,
        "editor.formatOnSave": true,
        "eslint.enable": true,
        "prettier.enable": true,
        "android.sdkPath": "/usr/local/android-sdk"
      }
    }
  },
  "updateContentCommand": "pip install -r requirements.txt || true && npm install || true"
}
