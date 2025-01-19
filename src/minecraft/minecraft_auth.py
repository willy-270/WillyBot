from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from urllib.parse import urlencode
from .consts import EMAIL, PASSWORD, CLIENT_SECRET, CLIENT_ID
import subprocess

scope = "Xboxlive.signin Xboxlive.offline_access"
redirect_uri = "http://localhost:4545"
authorization_endpoint = f'https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize'
token_endpoint = f'https://login.microsoftonline.com/consumers/oauth2/v2.0/token'

xblToken = "" 
uhs = ""

def xboxLiveAuth(access_token):
    payload = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": "d=" + access_token,
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
    }

    r = requests.post("https://user.auth.xboxlive.com/user/authenticate", json=payload)
    r = r.json()

    global xblToken 
    global uhs

    xblToken = r["Token"]
    uhs = r["DisplayClaims"]["xui"][0]["uhs"]

def xstsAuth(xblToken):
    payload = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                xblToken,
            ],
        },
        "RelyingParty": "https://pocket.realms.minecraft.net/",
        "TokenType": "JWT",
    }

    r = requests.post("https://xsts.auth.xboxlive.com/xsts/authorize", json=payload)
    r = r.json()

    xstsToken = r["Token"]

    return xstsToken

def get_service_token():
    auth_url_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': scope,
    }

    server = subprocess.Popen(['python3', '-m', 'http.server', '4545'])

    auth_url = f'{authorization_endpoint}?{urlencode(auth_url_params)}'

    EMAILFIELD = (By.ID, "i0116")
    PASSWORDFIELD = (By.ID, "i0118")
    NEXTBUTTON = (By.ID, "idSIButton9")
    ACCEPTBUTTON = (By.ID, "acceptButton")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')  # Required in Docker
    chrome_options.add_argument('--disable-dev-shm-usage')  # Overcomes resource constraints
    chrome_options.add_argument('--disable-gpu')  # Avoid GPU usage
    chrome_options.add_argument('--window-size=1920x1080')  # Set a fixed window size

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(auth_url)

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(EMAILFIELD)).send_keys(EMAIL)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(NEXTBUTTON)).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(PASSWORDFIELD)).send_keys(PASSWORD)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(NEXTBUTTON)).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(ACCEPTBUTTON)).click()

    redirected_url = driver.current_url
    auth_code = redirected_url.split('code=')[1].split('&')[0]

    driver.quit()
    server.terminate()

    token_request_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'code': auth_code,
        'grant_type': 'authorization_code',
    }

    token_response = requests.post(token_endpoint, data=token_request_data)
    token_data = token_response.json()
    access_token = token_data['access_token']

    xboxLiveAuth(access_token)
    xstsToken = xstsAuth(xblToken)

    service_token = uhs + ";" + xstsToken
    return service_token