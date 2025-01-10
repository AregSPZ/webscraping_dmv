import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Setup the WebDriver 
service = Service(r"D:\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Open the URL
url = "https://roadpolice.am/hy/hqb"
driver.get(url)

# Wait for the page to load 
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="mx_theori_practic"]/label[2]'))
)

# choose Practic test type 
practic_button = driver.find_element(By.XPATH, '//*[@id="mx_theori_practic"]/label[2]')
practic_button.click()

# open DMVs
dmvs_xpath = '/html/body/div/main/div[2]/div/div/div[2]/form/div[3]/span/span[1]/span'
dmvs = driver.find_element(By.XPATH, dmvs_xpath)
dmvs.click()

# choose Artashat DMV
artashat_dmv = driver.find_element(By.XPATH, '/html/body/span/span/span[2]/ul/li/ul/li[7]')
artashat_dmv.click()


# wait for the month container to load
month_container_xpath = '/html/body/div/main/div[2]/div/div/div[2]/form/div[4]/div[1]/div[2]/div/div[2]/div'
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, month_container_xpath))
)

# get the button that shifts to the next month
next_month = driver.find_element(By.XPATH, '/html/body/div/main/div[2]/div/div/div[2]/form/div[4]/div[1]/div[1]/span[2]')


def scan(current_test_date):
    '''Scan the days until found a free day while keeping in mind the current test day'''

    flag = True
    while flag:
        # access the container containing the data for the current month
        container = driver.find_element(By.XPATH, month_container_xpath)
        # get the list of days in the current month
        current_month_elements = container.find_elements(By.TAG_NAME, 'span')

        for element in current_month_elements:

            # stop iterating if found a free day or we got to the current test day (no sooner day was found)
            if 'flatpickr-disabled' not in element.get_attribute('class') or element.get_attribute('aria-label') == current_test_date:
                # assign nothing to free_date if we got to the current test day
                free_date = element.get_attribute('aria-label') if element.get_attribute('aria-label') != current_test_date else None
                flag = False
                break
        
        # shift to the next month
        next_month.click()

    return free_date


# scan with current test date as input
# the date should follow this format and not be in the past
current_date = 'Մարտ 18, 2025'
available_date = scan(current_date)

# Close the browser
driver.quit()

# send a notification if theres an available date
if available_date:

    message = f"An earlier driving test day is available: {available_date}"

    url = "https://ntfy.sh/hqb"

    # Send the notification
    response = requests.post(url, data=message)

    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print(f"Failed to send notification: {response.status_code}")


print(available_date)
