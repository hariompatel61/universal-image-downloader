<div align="center">

# 🌌 Universal Google Image Bulk Downloader Pro
**The Ultimate Anti-CAPTCHA High-Resolution Image Scraper**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-webdriver-green.svg)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Automate massive image dataset generation for E-Commerce catalogs, AI Training, and Content Management Systems without ever getting blocked.*

</div>

---

## 🚀 Overview

**Universal Google Image Bulk Downloader Pro** is a production-grade, highly configurable image scraping tool designed to bypass Google's strict anti-bot mechanisms. 

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

## 📦 Installation

1. **Clone the Repository** (or download the folder):
   ```bash
   git clone https://github.com/yourusername/universal-image-downloader.git
   cd universal-image-downloader
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have Google Chrome installed on your machine).*

---

## ⚙️ Configuration & Usage

1. **Run the tool for the first time** to generate the default configuration:
   ```bash
   python universal_google_image_bulk_downloader.py
   ```
2. **Edit `config.json`**:
   Open the newly created `config.json` to define your download jobs. 
   
   ```json
   {
       "premium_sites": ["freepik.com", "unsplash.com", "pexels.com"],
       "wait_seconds_per_image": 15,
       "jobs": [
           {
               "data_file": "My_Catalog.xlsx",
               "name_column": "Product Name",
               "search_context": "high quality studio photography",
               "fallback_filters": "-video -youtube",
               "output_folder": "catalog_images"
           }
       ]
   }
   ```
3. **Start the Engine**:
   ```bash
   python universal_google_image_bulk_downloader.py
   ```
   *Note: On your very first run, a Chrome window will open. You have 10 seconds to manually solve any initial Google CAPTCHA. Your session is then saved in `chrome_profile/` for all future automated runs!*

---

## 📊 Perfect For:
- **E-Commerce Managers**: Automating Shopify, WooCommerce, or Amazon catalog imagery.
- **AI/ML Engineers**: Creating massive labeled datasets for Computer Vision (YOLO, ResNet) training.
- **Web Scrapers & Data Miners**: Extracting geo-tagged, SEO-optimized image assets.

---

<div align="center">
<i>Built for efficiency. Engineered for scale.</i>
</div>

<br>

---
###### Tags for Search (SEO/AEO/GEO):
`Google Image Scraper` `Bulk Image Downloader` `Python Selenium Image Scraper` `Undetected Chromedriver` `Bypass CAPTCHA Google Images` `E-commerce Catalog Image Scraper` `Dataset Generation` `AI Training Images Scraper` `Excel to Images Python` `Automated Image Downloader` `High Resolution Image Scraper` `Stock Photo Scraper`
