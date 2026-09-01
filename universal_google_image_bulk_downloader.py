import os
import re
import time
import json
import hashlib
import random
import zipfile
from pathlib import Path
from urllib.parse import quote

import requests
import pandas as pd
from PIL import Image
from io import BytesIO

# Using undetected-chromedriver to bypass CAPTCHAs
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "chrome_profile"
CONFIG_FILE = BASE_DIR / "config.json"

DEFAULT_CONFIG = {
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
            "name_column": "", 
            "category_column": "",
            "search_context": "Indian food dish",
            "fallback_filters": "-recipe -video -youtube",
            "output_folder": "product_images"
        },
        {
            "data_file": "example_clothing_catalog.xlsx",
            "search_context": "clothing apparel",
            "fallback_filters": "",
            "output_folder": "clothing_images"
        }
    ]
}

# We no longer block these domains per user request
BLOCKED_DOMAINS = []
BLOCKED_TEXT_HINTS = ["watermark"]


def load_or_create_config():
    if not CONFIG_FILE.exists():
        print(f"Creating default configuration file: {CONFIG_FILE.name}")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
        
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def random_delay():
    time.sleep(random.uniform(1.5, 3.5))


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def slugify(value):
    value = clean(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")


def load_products(job):
    """Load products from a specific Excel or CSV file."""
    data_file_path = job.get("data_file")
    name_col_override = job.get("name_column")
    category_col_override = job.get("category_column")

    p = Path(data_file_path)
    if not p.is_absolute():
        p = BASE_DIR / data_file_path
        
    if not p.exists():
        print(f"Warning: Data file not found: {p}")
        return []
        
    products = []
    print(f"Loading data from {p.name}...")
    try:
        if p.suffix == '.xlsx':
            df = pd.read_excel(p, header=None)
        else:
            df = pd.read_csv(p, header=None)
        
        # If the file has only 1 column, it's just names
        if len(df.columns) == 1:
            name_col = df.columns[0]
            cat_col = None
            slug_col = None
        else:
            # Find the header row by looking for 'name', 'item', or 'product'
            header_idx = 0
            for idx, row in df.iterrows():
                row_strs = [str(x).lower() for x in row.values]
                if any('name' in r or 'title' in r or 'product' in r for r in row_strs if 'unnamed' not in r):
                    header_idx = idx
                    break
            
            # Set the header and data
            df.columns = [str(x).lower().strip() for x in df.iloc[header_idx].values]
            df = df.iloc[header_idx+1:].reset_index(drop=True)
            
            if name_col_override and str(name_col_override).lower() in df.columns:
                name_col = str(name_col_override).lower()
            else:
                # Try to map columns strictly
                name_col = next((c for c in df.columns if c in ['item name', 'name', 'title', 'product name', 'product']), None)
                if not name_col:
                    name_col = next((c for c in df.columns if 'name' in c or 'title' in c), None)
            
            if category_col_override and str(category_col_override).lower() in df.columns:
                cat_col = str(category_col_override).lower()
            else:
                cat_col = next((c for c in df.columns if 'category' in c or 'cat' in c), None)
                
            slug_col = next((c for c in df.columns if 'slug' in c), None)
            
            if not name_col:
                # If still no name_col but there are exactly 2 columns, assume first is name, second is category
                if len(df.columns) == 2:
                    name_col = df.columns[0]
                    cat_col = df.columns[1]
                else:
                    print(f"Could not find a 'name' column in {p.name}. Found columns: {list(df.columns)}")
                    return []
            
        for _, row in df.iterrows():
            name = str(row[name_col])
            if pd.isna(name) or name.strip() == "nan" or not name.strip(): continue
            
            cat = str(row[cat_col]) if cat_col and not pd.isna(row[cat_col]) else ""
            if cat.strip() == "nan": cat = ""
            
            slug = str(row[slug_col]) if slug_col and not pd.isna(row[slug_col]) else slugify(name)
            if slug.strip() == "nan": slug = slugify(name)
            
            products.append({
                "name": name,
                "category": cat,
                "slug": slug
            })
    except Exception as e:
        print(f"Error loading {p.name}: {e}")
            
    # Ensure unique slugs
    used = set()
    unique_products = []
    for prod in products:
        base_slug = prod['slug']
        slug = base_slug
        n = 1
        while slug in used:
            slug = f"{base_slug}{n}"
            n += 1
        used.add(slug)
        prod['slug'] = slug
        unique_products.append(prod)

    return unique_products


def init_driver():
    print(f"Initializing Undetected ChromeDriver with profile: {PROFILE_DIR}")
    PROFILE_DIR.mkdir(exist_ok=True)
    
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    
    # Explicitly specify Chrome version 151 to fix driver mismatch error
    driver = uc.Chrome(options=options, version_main=151)
    driver.set_page_load_timeout(60)
    return driver


def image_bytes_from_src(src):
    if not src:
        return None

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/151 Safari/537.36"
            ),
            "Referer": "https://www.google.com/",
        }

        if src.startswith("data:image"):
            import base64
            return base64.b64decode(src.split(",", 1)[1])

        r = requests.get(src, headers=headers, timeout=30)
        if r.ok and r.content:
            return r.content
    except Exception:
        pass

    return None


def save_as_jpg(raw, path, min_w, min_h):
    """Save the downloaded image WITHOUT crop or resize; preserve original dimensions."""
    try:
        im = Image.open(BytesIO(raw))
        im.load()

        w, h = im.size
        if w < min_w or h < min_h:
            return False, f"too small ({w}x{h})"

        if im.mode in ("RGBA", "LA", "P"):
            if im.mode == "P":
                im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, "white")
            if "A" in im.getbands():
                bg.paste(im, mask=im.getchannel("A"))
            else:
                bg.paste(im)
            im = bg
        else:
            im = im.convert("RGB")

        im.save(path, "JPEG", quality=95, optimize=True)
        return True, f"{w}x{h} (original dimensions, no crop/resize)"
    except Exception as e:
        return False, f"invalid image: {e}"


def get_first_google_result(driver):
    """Return the first real Google Images result thumbnail in DOM order."""
    imgs = driver.find_elements(By.TAG_NAME, "img")

    for img in imgs:
        try:
            if not img.is_displayed():
                continue

            src = img.get_attribute("src")
            if not src or not (src.startswith("http") or src.startswith("data:image")):
                continue

            rect = img.rect
            if rect.get("width", 0) < 150 or rect.get("height", 0) < 150:
                continue

            return img
        except Exception:
            continue

    return None


def extract_full_image_after_click(driver, thumb, min_w, min_h):
    """Click the first result and retrieve the largest available image URL."""
    thumb_src = thumb.get_attribute("src") or ""

    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'center'});",
            thumb,
        )
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", thumb)
    except Exception:
        try:
            thumb.click()
        except Exception:
            return None

    time.sleep(3.5) # Wait longer for the high-res image to load

    candidates = driver.find_elements(By.TAG_NAME, "img")
    best_src = None
    best_area = 0

    for img in candidates:
        try:
            if not img.is_displayed():
                continue

            src = img.get_attribute("src") or ""
            if not src or src == thumb_src or src.startswith("data:image"):
                continue

            natural_w = int(driver.execute_script(
                "return arguments[0].naturalWidth || 0;", img
            ) or 0)
            natural_h = int(driver.execute_script(
                "return arguments[0].naturalHeight || 0;", img
            ) or 0)

            area = natural_w * natural_h
            if natural_w >= min_w and natural_h >= min_h and area > best_area:
                best_area = area
                best_src = src
        except Exception:
            continue

    return best_src or thumb_src


def open_search_in_new_tab(driver, url):
    original = driver.current_window_handle
    driver.switch_to.new_window("tab")
    new_handle = driver.current_window_handle
    try:
        driver.get(url)
        return original, new_handle
    except Exception:
        raise


def download_image(driver, product, save_path, job, config):
    name = product["name"]
    category = product.get("category", "")
    
    search_context = job.get("search_context", "").strip()
    fallback_filters = job.get("fallback_filters", "").strip()
    wait_time = config.get("wait_seconds_per_image", 15)
    min_w = config.get("min_width", 180)
    min_h = config.get("min_height", 180)
    
    premium_sites_list = config.get("premium_sites", [])
    
    urls = []
    
    if premium_sites_list:
        premium_sites_str = " OR ".join([f"site:{s}" for s in premium_sites_list])
        query_premium = f'"{name}" {search_context} {premium_sites_str}'.strip()
        url_premium = "https://www.google.com/search?tbm=isch&q=" + quote(query_premium) + "&tbs=isz:l"
        urls.append((url_premium, "PREMIUM"))
    
    query_fallback = f'"{name}" {category} {search_context} {fallback_filters}'.strip()
    url_fallback = "https://www.google.com/search?tbm=isch&q=" + quote(query_fallback) + "&tbs=isz:l"
    urls.append((url_fallback, "FALLBACK"))

    failures = []

    for url, stage in urls:
        original_handle = None
        tab_handle = None
        try:
            original_handle, tab_handle = open_search_in_new_tab(driver, url)

            # Wait for images to load. It might time out if no images are found
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "img"))
                )
            except Exception:
                failures.append(f"{stage}: no results page")
                continue
                
            time.sleep(1.5)

            first = get_first_google_result(driver)
            if first is None:
                failures.append(f"{stage}: no valid result image found")
                continue

            full_src = extract_full_image_after_click(driver, first, min_w, min_h)
            raw = image_bytes_from_src(full_src)

            if not raw:
                thumb_src = first.get_attribute("src")
                raw = image_bytes_from_src(thumb_src)
                if not raw:
                    failures.append(f"{stage}: image download failed")
                    continue

            ok, reason = save_as_jpg(raw, save_path, min_w, min_h)
            if ok:
                return True, f"{stage} | {reason}"

            failures.append(f"{stage}: {reason}")

        finally:
            try:
                if tab_handle and tab_handle in driver.window_handles:
                    driver.switch_to.window(tab_handle)
                    driver.close()
            except Exception:
                pass

            try:
                if original_handle and original_handle in driver.window_handles:
                    driver.switch_to.window(original_handle)
            except Exception:
                pass

    return False, " | ".join(failures)


def create_zip_archive(output_dir):
    """Create a zip archive containing all downloaded files in the output directory."""
    output_path = Path(output_dir)
    if not output_path.exists():
        return None

    files_to_zip = [f for f in output_path.rglob("*") if f.is_file() and not f.name.endswith(".zip")]

    if not files_to_zip:
        print(f"No files found in '{output_path.name}' to zip.")
        return None

    zip_file_path = output_path.parent / f"{output_path.name}.zip"
    print(f"Creating zip archive '{zip_file_path.name}' ({len(files_to_zip)} file(s))...")

    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            arcname = file_path.relative_to(output_path)
            zipf.write(file_path, arcname=str(arcname))

    print(f"Zip created successfully: {zip_file_path.name}")
    return zip_file_path


def process_job(job, config, driver):
    data_file = job.get("data_file")
    if not data_file:
        print("Skipping job: No 'data_file' specified.")
        return 0, 0
        
    out_dir_name = job.get("output_folder", "product_images")
    output_dir = BASE_DIR / out_dir_name
    output_dir.mkdir(exist_ok=True)
    
    products = load_products(job)
    if not products:
        print(f"Skipping job: No products found for {data_file}")
        return 0, 0
        
    report_file = BASE_DIR / f"report_{Path(data_file).stem}.csv"
    
    print("-" * 70)
    print(f"Starting Job: {data_file}")
    print(f"Context: '{job.get('search_context', '')}'")
    print(f"Output: {output_dir}")
    print(f"Items to process: {len(products)}")
    print("-" * 70)
    
    report = []
    
    for i, product in enumerate(products, 1):
        filename = f"{product['slug']}.jpg"
        path = output_dir / filename

        print(
            f"[{i:03d}/{len(products):03d}] "
            f"{product['name']} -> ",
            end="",
            flush=True
        )

        # ====== SKIP LOGIC ======
        if path.exists() and path.stat().st_size > 5000:
            print("SKIP (already exists)")
            report.append({
                "product": product["name"],
                "category": product.get("category", ""),
                "slug": product["slug"],
                "status": "exists",
                "file": filename,
                "reason": "File already exists",
            })
            continue

        try:
            ok, reason = download_image(driver, product, path, job, config)
        except Exception as e:
            msg = str(e)
            print(f"CHROME ERROR ({msg})")
            print("Restarting Chrome...")

            try:
                driver.quit()
            except Exception:
                pass

            driver = init_driver()

            try:
                ok, reason = download_image(driver, product, path, job, config)
            except Exception as e2:
                ok, reason = False, f"retry failed: {e2}"

        if ok:
            print(f"SUCCESS ({reason})")
            status = "success"
        else:
            print(f"FAIL ({reason})")
            status = "fail"
            if path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass

        report.append({
            "product": product["name"],
            "category": product.get("category", ""),
            "slug": product["slug"],
            "status": status,
            "file": filename if ok else "",
            "reason": reason,
        })

        random_delay()
        
    # Write report
    import csv
    with report_file.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["product", "category", "slug", "status", "file", "reason"],
        )
        writer.writeheader()
        writer.writerows(report)
        
    success = sum(1 for r in report if r["status"] in ("success", "exists"))
    failed = sum(1 for r in report if r["status"] == "fail")
    
    print(f"Job complete. Success/Skipped: {success} | Failed: {failed}")
    print(f"Report saved to: {report_file.name}")
    
    # Create zip archive of the output images
    zip_path = create_zip_archive(output_dir)
    if zip_path:
        print(f"All images archived into: {zip_path.name}")
        
    print("-" * 70)
    
    return success, failed


def main():
    print("=" * 70)
    print("UNIVERSAL GOOGLE IMAGE BULK DOWNLOADER PRO")
    print("=" * 70)
    
    config = load_or_create_config()
    jobs = config.get("jobs", [])
    
    if not jobs:
        print("No jobs defined in config.json. Please add a job and run again.")
        return

    driver = init_driver()
    
    driver.get("https://www.google.com")
    print("Opened Google. If this is your first run, you have 10 seconds to log in or solve any initial CAPTCHA.")
    time.sleep(10)

    try:
        total_success = 0
        total_failed = 0
        
        for job in jobs:
            succ, fail = process_job(job, config, driver)
            total_success += succ
            total_failed += fail
            
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    print("\n" + "=" * 70)
    print(f"ALL JOBS DONE. Total Success: {total_success} | Total Failed: {total_failed}")
    print("=" * 70)


if __name__ == "__main__":
    main()
