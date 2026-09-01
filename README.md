<div align="center">

# 🌌 Universal Google Image Bulk Downloader Pro
**The Ultimate Anti-CAPTCHA High-Resolution Image Scraper**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-webdriver-green.svg)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Automate massive image dataset generation for E-Commerce catalogs, AI Training, and Content Management Systems without ever getting blocked.*

<br>
<img src="https://via.placeholder.com/800x400.png?text=Terminal+Demo+Recording" alt="Terminal Execution Demo">
<br>

</div>

---

## 🚀 Overview

**Universal Google Image Bulk Downloader Pro** is a production-grade, highly configurable image scraping tool designed to bypass strict anti-bot mechanisms. 

Whether you need **1,000+ premium food dishes**, **apparel mockups**, or **nature landscapes**, this tool seamlessly parses your Excel/CSV sheets and downloads perfectly formatted, high-resolution imagery completely hands-free.

## ✨ Key Features

- 🛡️ **Anti-CAPTCHA Architecture**: Built on top of `undetected-chromedriver` with persistent profile sessions. Solve a CAPTCHA once, and never see it again.
- 🎯 **Two-Tier Smart Search**:
  1. **Premium First**: Forces Google to source images from premium stock photography sites (Freepik, Unsplash, Pexels, Pixabay) for maximum quality.
  2. **Intelligent Fallback**: Falls back to Google Images but actively filters out messy content like `-recipe` or `-video` to guarantee clean product images.
- 📂 **Multi-Job JSON Queue**: Process 50 different Excel files in a single run. The `config.json` system allows you to configure different search contexts (e.g., "clothing apparel" vs "Indian food dish") for each file.
- 🧠 **Smart Header Detection**: Effortlessly parses messy Excel sheets. Works perfectly with 1-column files, 2-column files, or custom column headers.
- ⚡ **Resume & Skip Logic**: Network dropped? No problem. The script instantly skips already downloaded images, saving massive bandwidth and time.

---

## 📦 Installation & Dependencies

1. **Clone the Repository** (or download the folder):
   ```bash
   git clone https://github.com/hariompatel61/universal-image-downloader.git
   cd universal-image-downloader
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have Google Chrome installed on your machine).*
   
   **Contents of `requirements.txt`:**
   ```text
   undetected-chromedriver>=3.5.5
   selenium>=4.21.0
   pandas>=2.0.0
   openpyxl>=3.1.2
   Pillow>=10.0.0
   requests>=2.31.0
   ```

---

## ⚙️ Configuration (`config.json`)

On the first run, the script generates a `config.json`. Below is a full, exhaustive example of all available fields you can tweak:

```json
{
    "premium_sites": [
        "freepik.com",
        "unsplash.com",
        "pexels.com",
        "pixabay.com"
    ],
    "min_width": 180,
    "min_height": 180,
    "wait_seconds_per_image": 15,
    "jobs": [
        {
            "data_file": "Study_Break_College_Canteen_Menu.xlsx",
            "name_column": "Item Name",
            "category_column": "Category",
            "search_context": "Indian food dish",
            "fallback_filters": "-recipe -video -youtube",
            "output_folder": "product_images"
        },
        {
            "data_file": "clothing_catalog.xlsx",
            "name_column": "",
            "category_column": "",
            "search_context": "clothing apparel flat lay",
            "fallback_filters": "-human -model",
            "output_folder": "clothing_images"
        }
    ]
}
```

---

## 🛠️ Troubleshooting & FAQ

**Q: I'm getting a `SessionNotCreatedException` (Driver Mismatch)**
> This means the undetected-chromedriver version doesn't match your installed Google Chrome version. By default, the script forces `version_main=151`. If you update Chrome, simply open the Python script and update `version_main=XXX` in the `init_driver()` function to match your browser.

**Q: Google is still showing me CAPTCHAs!**
> The script gives you 10 seconds on the very first run to solve the CAPTCHA manually. Once solved, `undetected-chromedriver` saves your session cookies in the `chrome_profile/` folder, meaning you won't be asked again on subsequent runs.

**Q: It skipped an item that I want it to re-download.**
> The script skips files that already exist in the output folder to save time. To force a re-download, simply delete the old image file, and run the script again.

---

## ⚖️ Ethical Use, Rate Limiting, & Legal Disclaimer

> [!WARNING]
> **Disclaimer:** This tool is intended for **personal, educational, and research purposes only**.

- **Respect Image Licenses**: Downloading an image does not grant you the copyright. Always ensure you have the proper licenses or rights to use downloaded imagery, especially for commercial purposes.
- **Rate Limiting**: To prevent accidental denial-of-service (DoS) to search engines, the script incorporates built-in random delays (1.5s to 3.5s) and longer page waits (3.5s). It generally averages **~10-15 requests per minute**. Do not remove these delays, as hammering servers unethically will lead to immediate IP bans.

---

## 🤝 Contributing

We welcome community contributions! If you have ideas for adding new fallback logic, supporting other browsers, or improving error handling, please see our [CONTRIBUTING.md](CONTRIBUTING.md) file.

---

<div align="center">
<i>Built for efficiency. Engineered for scale.</i>
</div>

<br>

---
###### Tags for Search (SEO/AEO/GEO):
`Google Image Scraper` `Bulk Image Downloader` `Python Selenium Image Scraper` `Undetected Chromedriver` `Bypass CAPTCHA Google Images` `E-commerce Catalog Image Scraper` `Dataset Generation` `AI Training Images Scraper` `Excel to Images Python` `Automated Image Downloader` `High Resolution Image Scraper` `Stock Photo Scraper`
