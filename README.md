# BWT Perla – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Custom Home Assistant integration for **BWT Perla water softeners**.  
It provides sensors and binary sensors for monitoring water consumption, hardness, regenerations, salt level, and more.

---

## Features

- Full integration with Home Assistant
- Auto-discovery via config flow (UI setup)
- Exposes all key values reported by the BWT Perla JSON API
- Proper device classes, units, and state classes for statistics
- Multilingual support (Danish, German, Swedish, Norwegian, Spanish, French, Italian, Finnish, English)

### Example Entities

- Water treated today / month / year
- Total water since setup
- Current flow rate
- Hardness in / out (°dH, CaCO₃)
- Regeneration counters and timestamps
- Salt level, remaining days, and usage
- Error and out-of-service states

---

## Installation

### HACS (recommended)

1. Go to **HACS → Integrations → Custom repositories**.
2. Add this repository URL: https://github.com/eskholm/bwt_perla/
3. Category: **Integration**.
3. Install the integration.
4. Restart Home Assistant.

### Manual

1. Clone or download this repository.
2. Copy the `custom_components/bwt_perla` folder into your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

---

## Configuration

Go to **Settings → Devices & Services → Add Integration** and search for **BWT Perla**.

You’ll be asked to provide:

- Host/IP of the BWT device
- Port (default `8080`)
- Username / password (if configured)
- Optional scan interval

No YAML configuration is required.

---

## Development

- Python 3.11+
- Follows [Home Assistant developer documentation](https://developers.home-assistant.io/)
- Lint with `flake8` and `black`

---

## License

This project is licensed under the [MIT License](LICENSE).

