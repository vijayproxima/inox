import cv2
from pytesseract import pytesseract
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import numpy as np
from PIL import Image, ImageOps
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

image=Image.open(screenshot_path)
threshold_value = 143
image=image.point(lambda x:0 if x < threshold_value else 255)
borederImage=ImageOps.expand(image,border=30,fill="white")
borederImage.save(screenshot_path)

# Preprocess the image (resize, grayscale, thresholding)
captcha_image = cv2.resize(captcha_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
#gray = cv2.cvtColor(captcha_image, cv2.COLOR_BGR2GRAY)
#gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

gray = cv2.cvtColor(np.array(captcha_image), cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (3, 3), 0)
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
invert = 255 - opening

# Use Tesseract OCR to perform OCR on the image with custom configuration
#captcha_text = pytesseract.image_to_string(gray, config='--psm 6')
    # Perform text extraction
data = re.sub('[ ]*', '', pytesseract.image_to_string(invert, lang='eng', config='--psm 6')).upper()
#captcha_text = re.findall('[a-zA-Z]{6}', data)[0] if len(re.findall('[a-zA-Z]{6}', data)) else 'ABCD'
#captcha_text = re.findall('[a-zA-Z0-9]{6}', data)[0] if len(re.findall('[a-zA-Z0-9]{6}', data)) else 'ABCD'
captcha_text = re.findall(r'\b[a-zA-Z0-9]{4,6}\b', data)

if captcha_text:
    # Ensure at least one letter and one number are present
    for text in captcha_text:
        if any(c.isalpha() for c in text) and any(c.isdigit() for c in text):
            captcha_text = text
            break
    else:
        captcha_text = 'ABCD'
else:
    captcha_text = 'ABCD'

# Print the CAPTCHA text for verification
print("CAPTCHA Text:", captcha_text)


# Close the browser
driver.quit()
