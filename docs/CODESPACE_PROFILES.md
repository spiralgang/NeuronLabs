# Codespace Profiles for NeuronLabs

This Codespace is pre-configured with robust profiles for Python, Node.js, and Android development, including:

- **Python 3.11**: Linting (flake8), autoformat (black), debug, test.
- **Node.js 20**: ESLint, Prettier, npm scripts.
- **Android SDK 33.0.2**: Native Android Studio/Gradle compatibility.
- **Remote Backend**: Preset environment variables for secure backend integration.

## Usage

- Ports 8330, 8329, 5000, and 8340 are forwarded for backend services.
- All code should reference environment variables for remote service calls.
- Linting and formatting are enforced on save.

## References

- /reference/vault
- [Dev Containers Specification](https://containers.dev/)
- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)