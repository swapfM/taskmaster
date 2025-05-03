import requests
from dotenv import load_dotenv
import os

load_dotenv()


url = "https://iam.cloud.ibm.com/identity/token"

api_key = os.getenv("API_KEY")

data = {
    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    "apikey": api_key,
}

headers = {"Content-Type": "application/x-www-form-urlencoded"}

response = requests.post(url, data=data, headers=headers)

if response.status_code == 200:
    token_info = response.json()
    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")
    token_type = token_info.get("token_type")
    expires_in = token_info.get("expires_in")

    # Write to file
    with open("token_info.txt", "w") as f:
        f.write(f"Access Token: {access_token}\n")
        f.write(f"Refresh Token: {refresh_token}\n")
        f.write(f"Token Type: {token_type}\n")
        f.write(f"Expires In: {expires_in} seconds\n")

    print("Token information written to token_info.txt")
else:
    with open("token_info.txt", "w") as f:
        f.write(f"Failed to obtain token: {response.status_code}\n")
        f.write(response.text)

    print("Error details written to token_info.txt")
