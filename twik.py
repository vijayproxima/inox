import cv2
from pytesseract import pytesseract
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import numpy as np

# Path to the Tesseract executable (update with your Tesseract installation path)
tesseract_dir = '/usr/bin/'
tesseract_executable = 'tesseract'
tesseract_path = os.path.join(tesseract_dir, tesseract_executable)
pytesseract.tesseract_cmd = tesseract_path

# Initialize Selenium WebDriver
driver = webdriver.Chrome()

# Open the website URL
website_url = "https://online.peso.gov.in/PublicDomain/"
driver.get(website_url)

# Locate the CAPTCHA image element
captcha_element = driver.find_element(By.XPATH, "//img[@id='IMG1']")

# Get the screenshot of the CAPTCHA image
screenshot_path = "captcha.png"  # Adjust the path and filename as needed
captcha_element.screenshot(screenshot_path)

# Read the CAPTCHA image using OpenCV
captcha_image = cv2.imread(screenshot_path)

# Preprocess the image (resize, grayscale, thresholding)
captcha_image = cv2.resize(captcha_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
gray = cv2.cvtColor(np.array(captcha_image), cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Use Tesseract OCR to perform OCR on the image with custom configuration
data = pytesseract.image_to_string(thresh, lang='eng', config='--psm 11 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

# Extract the CAPTCHA text
captcha_match = re.search(r'\b[a-zA-Z0-9]{4,6}\b', data)

if captcha_match:
    captcha_text = captcha_match.group().upper()
else:
    # If OCR fails to recognize the captcha, you may want to handle this case accordingly
    captcha_text = 'OCR_FAILED'

# Ensure the length of the captcha text matches the expected length
if len(captcha_text) < 4:
    captcha_text = 'ABCD'  # Default value for shorter captchas
elif len(captcha_text) > 6:
    captcha_text = captcha_text[:6]  # Truncate longer captchas

# Print the CAPTCHA text for verification
print("CAPTCHA Text:", captcha_text)

# Close the browser
driver.quit()
