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
blur = cv2.GaussianBlur(gray, (3, 3), 0)
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
invert = 255 - opening

# Use Tesseract OCR to perform OCR on the image with custom configuration
data = re.sub('[ ]*', '', pytesseract.image_to_string(invert, lang='eng', config='--psm 6')).upper()

# Extract the CAPTCHA text
captcha_match = re.search(r'\b[a-zA-Z0-9]{4,6}\b', data)

if captcha_match:
    captcha_text = captcha_match.group()
else:
    # If OCR fails to recognize the captcha, you may want to handle this case accordingly
    captcha_text = 'OCR_FAILED'

# Print the CAPTCHA text for verification
print("CAPTCHA Text:", captcha_text)

# Close the browser
driver.quit()
