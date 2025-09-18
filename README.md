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
2. Add this repository URL:  
