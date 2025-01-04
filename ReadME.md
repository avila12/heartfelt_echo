# Dementia Daily Support Platform

## Overview

This Flask-based web application tools to aid those affected by dementia.

---

## Status

**Work in Progress**: This application is not ready for production. Features and functionality are still under development.

---

## Features

---

## Installation

### Prerequisites
Hardware:
- Raspberry Pi OS 4 +

OS
- Raspberry Pi OS Lite

Ensure you have the following installed:
- Python 3.7+
- Flask 2.0+
- Virtualenv

### Steps
1. OS Setup:
    ```bash
    root user pi
    device name heartfeltecho
    ```
   
1. Clone the repository:
    ```bash
    git clone https://github.com/avila12/heartfelt_echo
    cd heartfelt_echo
    ```

2. Create .env file:
    ```bash
    sudo nanao .env
    ```

3. Install dependencies:
    ```bash
    chmod +x install.sh
    ./setup_kiosk.sh
    ```


## Folder Structure

```
.
|-- static/                # Static files (CSS, JS, Images)
|-- templates/             # HTML templates
|-- app.py                 # Main application file
|-- config.py              # Configuration settings
|-- requirements.txt       # Python dependencies
|-- README.md              # Project documentation
|-- tests/                 # Unit and integration tests
```

---

## Configuration
- Modify `config.py` for environment-specific settings.
- Set up environment variables for sensitive data such as API keys and database URIs:

---


## License



---

## Acknowledgments

---

## Contact


---


