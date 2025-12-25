from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from urllib.parse import urlencode
import time, secrets, base64, json
from selenium.webdriver.firefox.options import Options
import os

options = Options()
#options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
#service=Service("./geckodriver.exe")

auth = "auth.sparx-learning.com/oauth2/auth?"

driver = webdriver.Firefox()
#driver.minimize_window()

def formUrl(hd=None, p=None):
    baseUrl = "https://auth.sparx-learning.com/oauth2/auth"
    clientId = "sparx-learning"
    redirectUri = "https://api.sparx-learning.com/oauth2/callback/sparx"
    random_bytes = secrets.token_bytes(32)
    state = base64.urlsafe_b64encode(random_bytes).rstrip(b'=').decode()
    ts = int(time.time())
    params = {
        "client_id": clientId,
        "redirect_uri": redirectUri,
        "response_type": "code",
        "scope": "openid profile email",
        "state": state,
        "ts": ts
    }
    if hd: params["hd"] = hd
    if p: params["p"] = p
    return f"{baseUrl}?{urlencode(params)}"

def parseUrl(url: str):
    if url.startswith("https://") or url.startswith("http://"):
        return url
    else:
        return "http://" + url

def clickButton(obj: object = False, method: By = False, value: str = False):
    try:
        if not obj:
            b = driver.find_element(method, value)
        else:
            b = obj
        b.click()
        return b
    except Exception as e:
        return False, e

def parseTaskUrl(url: str):
    # https://science.sparx-learning.com/packages/475d5209-8157-4642-b26c-b6a613842b4e/tasks/f0aea2c0-1f42-4d87-a91a-e576372fde5a/1
    # https://science.sparx-learning.com/packages/475d5209-8157-4642-b26c-b6a613842b4e/tasks/893c3163-7ff0-47e5-991b-76aad1c46a54/2
    parts = url.split("/")
    f = {
        "platform": parts[2],
        "packageId": parts[4],
        "taskId": parts[6],
        "questionNm": parts[7]
    }
    return f

def wait_for_stable_position(driver, selector, timeout=10, interval=0.1):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )
    element = driver.find_element(By.CSS_SELECTOR, selector)
    last_location = element.location
    stable_counter = 0
    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(interval)
        current_location = element.location
        if current_location == last_location:
            stable_counter += 1
            if stable_counter >= 3:  # position hasn't changed 3 intervals in a row
                return element
        else:
            stable_counter = 0
        last_location = current_location
    return element

with open("schools.json", "r") as f:
    schools = json.load(f)

TMP_DIR = "./tmp"
PROGRESS_FILE = "./progress.json"
os.makedirs(TMP_DIR, exist_ok=True)

# Load progress
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)
else:
    progress = {}  # {"taskId": last_question_completed}

def save_progress(task_id, question_num):
    progress[task_id] = question_num
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


# the kingston academy
hd = schools["The Kingston Academy"]
email = "j.ng22@thekingstonacademy.org"


# form url for auth.sparx-learning.com
driver.get(formUrl(hd=hd, p="1"))

# reject cookies

WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.ID, "cookiescript_reject"))
)

try:
    clickButton(False, By.ID, "cookiescript_reject")
    loginButton= clickButton(False, By.CSS_SELECTOR, "div.sm-button.sso-login-button")
    driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, "div.sm-button.sso-login-button"))
except Exception as e:
    print(f"[E] error: error clicking signin:", e)

# accounts.google.com
try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "identifierId"))
    )
    loginfield = driver.find_element(By.ID, "identifierId")
    loginfield.send_keys(email)
    #driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "identifierNext"))
    driver.execute_script("document.getElementById('identifierNext').click();")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    passwfield = driver.find_element(By.ID, "password")
    driver.execute_script("alert('Please enter your password manually');")
    #driver.execute_script("document.getElementById('passwordNext').click();")
except Exception as e:
    print(f"[E] error: timeout waiting for google signin:", e)

# manual login
#driver.maximize_window()
input("[-] Press Enter to continue after completing the login...")
driver.minimize_window()
print("[+] Login complete, attempting to reach sparx-learning API...")

# sparx-learning home page
try:
    driver.get(parseUrl(f"https://api.sparx-learning.com/oauth2/login?route=https://app.sparx-learning.com/&school={hd}"))
except Exception as e:
    print(f"[E] error: cannot reach auth.sparx-learning.com:", e)

print("Please type A for science, B for maths.")
u = input("[.] Waiting for user input.")
if u.strip().upper() == "A":
    driver.get("https://science.sparx-learning.com/")
    homeworks = []
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".chakra-linkbox.css-1m3w3t0"))
    )
    
    #remove past homework section
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".chakra-accordion__item.css-1t7rcca"))
    )
    driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
    """, driver.find_element(By.CSS_SELECTOR, ".chakra-accordion__item.css-1t7rcca"))

    boxes = driver.find_elements(By.CSS_SELECTOR, ".chakra-linkbox.css-1m3w3t0")
    print("[-] Finding homework...")
    for box in boxes:
        due = box.find_element(By.CSS_SELECTOR, ".chakra-text.css-ryyl7k").text
        #title_tag = box.find_element(By.CSS_SELECTOR, ".chakra-linkbox__overlay")
        #title = title_tag.text
        link = box.find_element(By.CSS_SELECTOR, ".chakra-linkbox__overlay").get_attribute("href")
        percent_elements = box.find_elements(By.XPATH, ".//p[contains(text(), '%')]")
        percent = percent_elements[0].text if percent_elements else "0%"
        status_elements = box.find_elements(By.CSS_SELECTOR, ".chakra-text.css-nuncn2")
        status = status_elements[0].text if status_elements else "Not started"
        homeworks.append({
            "link": link,
            "due": due,
            "percent": percent,
            "status": status
        })
    for index,homework in enumerate(homeworks, start=1):
        print(f"[I] ({index}) Title: {homework['link']} Due: {homework['due']} Progress: {homework['percent']} Status: {homework['status']}\n")
    u = int(input("[+] Choose homework to open by typing the index number and pressing Enter: "))
    
    # open selected homework
    driver.get(homeworks[u-1]['link'])

    # extract title and percent complete for selected homework
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.chakra-linkbox"))
    )
    cards = driver.find_elements(By.CSS_SELECTOR, "div.chakra-linkbox")
    tasks = []
    for card in cards:
        title = card.find_element(By.CSS_SELECTOR, ".chakra-linkbox__overlay").text.strip()
        # green: css-1sp49pi yellow: css-o9xe7x
        percent_elements = card.find_elements(By.CSS_SELECTOR, ".chakra-text.css-1sp49pi, .chakra-text.css-o9xe7x")
        #print("percent elements:", percent_elements)
        percent = percent_elements[0].text if percent_elements else "0%"

        print(f"{title} - {percent}")
    
    # options
    u = input("Press A to complete task chromologically, B to complete all.")
    if u.strip().upper() == "A":
        tasks = driver.find_elements(By.CSS_SELECTOR, "div.chakra-linkbox")
        from science.parseQuestion import parseQuestion
        for index, task in enumerate(tasks, start=1):
            link = task.find_element(By.CSS_SELECTOR, ".chakra-linkbox__overlay").get_attribute("href")
            print(f"[+] Opening task: {link}")
            driver.get(link)
            WebDriverWait(driver, 10).until(lambda d: d.current_url != link)

            container = driver.find_element(By.CSS_SELECTOR, ".chakra-stack._NavStack_1xysh_45.css-4fq1ik.indiana-scroll-container")
            buttons = container.find_elements(By.TAG_NAME, "button")
            buttons.pop()  # removes "results" button at end

            task_info = parseTaskUrl(f"{link}/0")
            last_completed = int(progress.get(task_info["taskId"], 0))
            print(f"[+] Found {len(buttons)} questions. Last completed: {last_completed}")

        for qid, qu in enumerate(buttons, start=1):
            if qid <= last_completed:
                print(f"[!] Question {qid} already done, skipping.")
                continue

            # Click the question button to navigate to that question
            qu.click()

            # Wait until the page URL shows the correct question number
            WebDriverWait(driver, 10).until(
                lambda d: str(parseTaskUrl(d.current_url)['questionNm']) == str(qid)
            )

            c = parseTaskUrl(driver.current_url)
            print(f"[+] Task {index} Question {c['questionNm']}")

            os.makedirs(TMP_DIR, exist_ok=True)
            path = os.path.join(TMP_DIR, f"{c['platform']}-{c['taskId']}-{c['questionNm']}.png")
            wait_for_stable_position(driver, ".css-d8p915")
            driver.save_screenshot(path)
            print(f"[+] Screenshot saved to {path}")

            # Extract answer
            answer = parseQuestion(image_path=path)
            print(f"[+] Answer: {answer}")

            # Save progress
            save_progress(c['taskId'], qid)
    elif u.strip().upper() == "B":
        tasks = driver.find_elements(By.CSS_SELECTOR, "div.chakra-linkbox")
        for task in tasks:
            link = task.find_element(By.CSS_SELECTOR, ".chakra-linkbox__overlay").get_attribute("href")
            print(f"[+] Opening task: {link}")
            driver.get(link)
            input("[-] Press Enter to continue to the next task...")
    

elif u.strip().upper() == "B":
    driver.get("https://maths.sparx-learning.com/")
else:
    print("Invalid input, exiting.")
    driver.quit()
    exit(1)

input()
driver.quit()