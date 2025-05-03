import os
import requests
from dotenv import load_dotenv

load_dotenv()


def granite_result(title: str, description: str, employees: list) -> int:
    token = os.getenv("ACCESS_TOKEN")
    project_id = os.getenv("PROJECT_ID")

    prompt = f"""
You are TaskMaster AI. Your job is to assign the following task to the most suitable employee based on their skills.

Task:
Title: {title}
Description: {description}

Employees:
{employees}

Respond with only the user_id as a number. Do not return any explanation or text.
"""

    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 3,
        },
        "model_id": "ibm/granite-3-8b-instruct",
        "project_id": project_id,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.post(
        "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29",
        headers=headers,
        json=body,
    )

    if response.status_code != 200:
        raise Exception(f"Granite API Error: {response.status_code} - {response.text}")

    ai_output = response.json()
    user_id_str = ai_output.get("results", [{}])[0].get("generated_text", "").strip()

    try:
        return int(user_id_str)
    except ValueError:
        raise Exception(f"Invalid user_id returned by AI: {user_id_str}")
