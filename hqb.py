import requests
from datetime import datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode

# path to ChromeDriver
service = Service(r"/usr/bin/chromedriver")
# initialize the driver
driver = webdriver.Chrome(service=service, options=chrome_options)

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

# choose a specific DMV
selected_dmv = driver.find_element(By.XPATH, '/html/body/span/span/span[2]/ul/li/ul/li[7]')
selected_dmv.click()

# wait for the month container to load
month_container_xpath = '/html/body/div/main/div[2]/div/div/div[2]/form/div[4]/div[1]/div[2]/div/div[2]/div'
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, month_container_xpath))
)

# get the button that shifts to the next month
next_month = driver.find_element(By.XPATH, '/html/body/div/main/div[2]/div/div/div[2]/form/div[4]/div[1]/div[1]/span[2]')

def to_dtdate(date):
    '''Convert the date strings to datetime.date objects, with translating beforehand if necessary'''

    translate_dict = {'Հունվար': 'January', 'Փետրվար': 'February', 'Մարտ': 'March', 'Ապրիլ': 'April',
                      'Մայիս': 'May', 'Հունիս': 'June', 'Հուլիս': 'July', 'Օգոստոս': 'August', 
                      'Սեպտեմբեր': 'September', 'Հոկտեմբեր': 'October', 'Նոյեմբեր': 'November', 'Դեկտեմբեր': 'December'}

    words = date.split()
    # if the input was English from the start, no changes will be made
    for AM, ENG in translate_dict.items():
        if words[0] == AM:
            words[0] = ENG
    return datetime.strptime(' '.join(words), '%B %d, %Y').date()


def scan(current_test_date):
    '''Scan the days until found a free day while keeping in mind the current test day'''
    # get the current date in local timezone and the current test date as date objects
    today = (datetime.now(timezone.utc) + timedelta(hours=4)).date()
    cur_test_dt = to_dtdate(current_test_date)
    # scan the months starting from the current one
    flag = True
    while flag:
        # access the container containing the data for the current month
        container = driver.find_element(By.XPATH, month_container_xpath)
        # get the list of days in the current month
        current_month_elements = container.find_elements(By.TAG_NAME, 'span')
        for element in current_month_elements:
            # access the date in Armenian and convert to date object
            date_arm = element.get_attribute('aria-label')
            date_dt = to_dtdate(date_arm)
            # stop iterating if:
            # - found a free day which is in the future
            # - we got / passed the current test day (no sooner day was found)
            if ('flatpickr-disabled' not in element.get_attribute('class') and date_dt >= today) or date_dt >= cur_test_dt:
                # assign nothing to free_date if we got to the current test day
                free_date = date_arm if date_dt < cur_test_dt else None
                flag = False
                break
        # shift to the next month
        next_month.click()

    return free_date

# scan with current test date as input
# the input should be Armenian or English and follow this format: '%B %d, %Y' 
current_testdate = 'Ապրիլ 24, 2025'
available_date = scan(current_testdate)

# Close the browser
driver.quit()

# send a notification if theres an available date
if available_date:

    message = f"An earlier driving test day is available: {available_date}"
    # use ntfy.sh for sending push notifications using Python completely free
    url = "https://ntfy.sh/hqb"
    # Send the notification
    response = requests.post(url, data=message, headers={'Priority': '5'})

    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print(f"Failed to send notification: {response.status_code}")


print(available_date)
