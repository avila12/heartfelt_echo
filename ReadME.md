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
Weather api:
- https://rapidapi.com
- https://rapidapi.com/weatherapi/api/weatherapi-com/playground/apiendpoint_45d0557e-e911-4a71-b6ff-1f9015f156af

Hardware:
- Raspberry Pi OS 4 +

OS
- Raspberry Pi OS Lite

### Steps
1. OS Setup:
    ```bash
    root user pi
    device name heartfeltecho
    ```
   
2. Clone the repository:
    ```bash
    sudo apt install git
    git clone https://github.com/avila12/heartfelt_echo
    cd heartfelt_echo
    ```

3. Create .env file and Configuration:
    ```bash
    sudo nanao .env
    ```
4. .env values:
   ```bash
    FLASK_PORT=5000
    WEATHERAPI_KEY = <your key>
    EVENT_URL = <your calendar url>
    EVENT_HOLIDAY_URL = <your holiday calendar url>
    ```

5. Install dependencies:
    ```bash
    chmod +x install.sh
    ./setup_kiosk.sh
    ```


## Folder Structure

```
.
|-- photos/                # Photos for backbround
|-- scripts/               # script mouels
|-- static/                # Static files (CSS, JS, Images)
|-- templates/             # HTML templates
|-- app.py                 # Main application file
|-- config.py              # Configuration settings
|-- README.md              # Project documentation
|-- requirements.txt       # Python dependencies
|-- routes.py              # Project routes
|-- scheduler.py           # Project scheduler
|-- setup_kiosk.sh         # Raspberry Pi Setup script
|-- tests/                 # Unit and integration tests
```

---

## Configuration
- Modify `.env` for environment-specific settings.
- Set up environment variables for sensitive data such as API keys and database URIs:

---


## License



---

## Acknowledgments

---

## Contact


---


