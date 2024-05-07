from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image, ImageOps
import pytesseract
import subprocess

# Initialize Selenium WebDriver
driver = webdriver.Chrome()

# Open the website URL
website_url = "https://online.peso.gov.in/PublicDomain/"
driver.get(website_url)

# Wait for the page to load completely
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.XPATH, "//img[@id='IMG1']")))

# Find the CAPTCHA image element
captcha_element = driver.find_element(By.XPATH, "//img[@id='IMG1']")

# Wait for a few seconds to ensure the CAPTCHA image is fully loaded (adjust as needed)
time.sleep(5)

# Save a screenshot of the CAPTCHA image
screenshot_path = "captcha.png"  # Adjust the path and filename as needed
captcha_element.screenshot(screenshot_path)

image=Image.open(screenshot_path)
threshold_value = 143
image=image.point(lambda x:0 if x < threshold_value else 255)
borederImage=ImageOps.expand(image,border=30,fill="white")
borederImage.save(screenshot_path)


# Use OCR to recognize the CAPTCHA text
#captcha_text = pytesseract.image_to_string(Image.open(screenshot_path))

p=subprocess.Popen(['tesseract','captcha.png',"captcha"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p.wait()
f=open('captcha.txt','r')
captchaResponse=f.read().replace(" ","").replace("\n","")
print("captcha responce attempt "+ captchaResponse+"\n\n")
try:
    print (captchaResponse)
    print (len(captchaResponse))
    print (type(captchaResponse))
except:  # noqa: E722
    print ("No way")
    
# Print the CAPTCHA text for verification
#print("CAPTCHA Text:", captcha_text)



# Close the browser
driver.quit()
