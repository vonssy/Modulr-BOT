# 🚀 Modulr BOT

> Automated transfer modulr test token and multi-account management

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/vonssy/Modulr-BOT.svg)](https://github.com/vonssy/Modulr-BOT/stargazers)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Proxy Recommendation](#proxy-recommendation)
- [Support](#support)
- [Contributing](#contributing)

## 🎯 Overview

Modulr BOT is an automated tool designed to transfer modulr test token across multiple accounts. It provides seamless offers robust proxy support for enhanced security and reliability.

**🧩 Modulr Extension:** [Chrome Web Store](https://chromewebstore.google.com/detail/modulr-wallet/cdmhpjjhnamicehbdojmlnnodfcgnehn)  
**🚰 Modulr Faucet:** [Modulr Explorer](https://testnet.explorer.modulr.cloud/faucet)

## ✨ Features

- 🔄 **Automated Account Management** - Retrieve account information automatically
- 🌐 **Flexible Proxy Support** - Run with or without proxy configuration
- 🔀 **Smart Proxy Rotation** - Automatic rotation of invalid proxies
- 💸 **Transfer Test Token** - Automated transfer modulr test token to another address
- 👥 **Multi-Account Support** - Manage multiple accounts simultaneously

## 📋 Requirements

- **Python:** Version 3.9 or higher
- **pip:** Latest version recommended

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vonssy/Modulr-BOT.git
cd Modulr-BOT
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# or for Python 3 specifically
pip3 install -r requirements.txt
```

### 3. Library Version Management

> ⚠️ **Important:** Ensure library versions match those specified in `requirements.txt`

**Check installed library version:**
```bash
pip show library_name
```

**Uninstall conflicting library:**
```bash
pip uninstall library_name
```

**Install specific library version:**
```bash
pip install library_name==version
```

## ⚙️ Configuration

### Account Setup

Create or edit `accounts.txt` in the project directory:

```
your_seedB64_1
your_seedB64_2
your_seedB64_3
```

### Config Setup

Create or edit `.env` in the project directory:

```
RECIPIENT=BntNywzXyy3XSZe4wJyeDcRBXVhYZenGtdfTabKpL6p6

SEND_COUNT=10
SEND_AMOUNT=10

MIN_DELAY=5
MAX_DELAY=10
```

### Proxy Configuration (Optional)

Create or edit `proxy.txt` in the project directory:

```
# Simple format (HTTP protocol by default)
192.168.1.1:8080

# With protocol specification
http://192.168.1.1:8080
https://192.168.1.1:8080

# With authentication
http://username:password@192.168.1.1:8080
```

## 🚀 Usage

Run the bot using one of the following commands:

```bash
python bot.py
# or for Python 3 specifically
python3 bot.py
```

### Runtime Options

When starting the bot, you'll be prompted to choose:

1. **Proxy Mode Selection:**
   - Option `1`: Run with proxy
   - Option `2`: Run without proxy

2. **Auto-Rotation:** 
   - `y`: Enable automatic invalid proxy rotation
   - `n`: Disable auto-rotation

## 💖 Support the Project

If this project has been helpful to you, consider supporting its development:

### Cryptocurrency Donations

| Network | Address |
|---------|---------|
| **EVM** | `0xe3c9ef9a39e9eb0582e5b147026cae524338521a` |
| **TON** | `UQBEFv58DC4FUrGqinBB5PAQS7TzXSm5c1Fn6nkiet8kmehB` |
| **SOL** | `E1xkaJYmAFEj28NPHKhjbf7GcvfdjKdvXju8d8AeSunf` |
| **SUI** | `0xa03726ecbbe00b31df6a61d7a59d02a7eedc39fe269532ceab97852a04cf3347` |

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. ⭐ **Star this repository** if you find it useful
2. 👥 **Follow** for updates on new features
3. 🐛 **Report issues** via GitHub Issues
4. 💡 **Suggest improvements** or new features
5. 🔧 **Submit pull requests** for bug fixes or enhancements

## 📞 Contact & Support

- **Developer:** vonssy
- **Issues:** [GitHub Issues](https://github.com/vonssy/Modulr-BOT/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vonssy/Modulr-BOT/discussions)

---

<div align="center">

**Made with ❤️ by [vonssy](https://github.com/vonssy)**

*Thank you for using Modulr BOT! Don't forget to ⭐ star this repository.*

</div>