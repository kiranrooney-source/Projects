# Setup Instructions for Selenium Scripts

## Prerequisites

1. **Install Python** (3.7 or higher)
2. **Install Chrome browser**
3. **Download ChromeDriver** or use webdriver-manager

## Installation

```bash
# Install required packages
pip install selenium webdriver-manager

# Or use requirements.txt
pip install -r requirements.txt
```

## Alternative Script with WebDriver Manager

If you get ChromeDriver errors, use this version:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Auto-download ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()

# Your recorded actions will be here...

driver.quit()
```

## Common Issues & Solutions

1. **ChromeDriver not found**: Install webdriver-manager
2. **Permission denied**: Run as administrator
3. **Element not found**: Increase wait times or check selectors
4. **Chrome not found**: Ensure Chrome is installed in default location