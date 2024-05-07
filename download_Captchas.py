from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
# from PIL import Image, ImageOps

driver = webdriver.Chrome()

if not os.path.exists("images"):
    os.makedirs("images")
if not os.path.exists("cleaned_images"):
    os.makedirs("cleaned_images")  
cleaned_images_folder = "cleaned_images"

website_url = "https://online.peso.gov.in/PublicDomain/"
driver.get(website_url)

# Wait for the page to load completely
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.XPATH, "//img[@id='IMG1']")))

# Define the number of captcha images to capture
num_captchas = 1000 # Adjust as needed

for i in range(num_captchas):
    # Refresh the page to get a new captcha
    driver.refresh()
    print(i)
    # Wait for the page to load completely
    wait.until(EC.presence_of_element_located((By.XPATH, "//img[@id='IMG1']")))

    # Find the CAPTCHA image element
    captcha_element = driver.find_element(By.XPATH, "//img[@id='IMG1']")

    # Wait for a few seconds to ensure the CAPTCHA image is fully loaded (adjust as needed)
    time.sleep(0.6)

    # Save a screenshot of the CAPTCHA image
    screenshot_path = f"images/captcha_{i+1}.png"  # Adjust the path and filename as needed
    captcha_element.screenshot(screenshot_path)
    # try:
    #     # Open the captured image
    #     image = Image.open(screenshot_path)

    #     # Apply thresholding to clean the image
    #     image = image.point(lambda x: 0 if x < 143 else 255)

    #     # Expand the border to ensure complete characters are captured
    #     border_image = ImageOps.expand(image, border=30, fill="white")

    #     # Save the cleaned image
    #     cleaned_image_path = os.path.join(cleaned_images_folder, f"cleaned_captcha_{i+1}.png")
    #     border_image.save(cleaned_image_path,"PNG")
    #     print(screenshot_path)
    #     print(f"Image {i+1} saved successfully.")

    # except Exception as e:
    #     print(f"Error processing image {i+1}: {e}")
# Close the WebDriver
driver.quit()