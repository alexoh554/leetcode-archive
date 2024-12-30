import os
import requests
import json
import time

LEETCODE_USERNAME = "bigfella123"
MAX_SUBMISSIONS = 5
MAX_RETRIES = 10
NEW_SESSION_NAME = "Session1"

GRAPHQL_URL = "https://leetcode.com/graphql"

def load_graphql_query(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def send_graphql_request(session, query, variables):
    payload = {
        "query": query,
        "variables": variables
    }
    
    response = session.post(GRAPHQL_URL, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def create_new_session(session):
    url = "https://leetcode.com/session/"
    headers = {
        "Content-Type": "application/json",
        "x-csrftoken": session.cookies.get('csrftoken'),
        "x-requested-with": "XMLHttpRequest",
    }
    body = {
        "func": "create",
        "name": NEW_SESSION_NAME
    }
    for attempt in range(MAX_RETRIES):
        try:
            response = session.put(url, headers=headers, json=body)
            if response.status_code == 200:
                print("Session created successfully!")
                return response.json()
            else:
                print("Session creation failed. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Error during session creation: {e}. Retrying...")
        time.sleep(2)  # Sleep before retrying
    raise Exception("Failed to create session after multiple attempts.")

def fetch_submission_code(session, submission_slug):
    submission_url = f"https://leetcode.com/api/submissions/{submission_slug}/"
    response = session.get(submission_url)
    if response.status_code == 200:
        return response.json().get('code', 'No code available')
    else:
        raise Exception(f"Error fetching code for submission {submission_slug}: {response.status_code}")

def extract_submission_data(session, response_data):
    submissions = response_data.get("data", {}).get("recentSubmissionList", [])
    
    formatted_data = []
    num_submissions = 0
    for submission in submissions:
        submission_slug = submission.get("titleSlug")
        try:
            code = fetch_submission_code(session, submission_slug)
        except Exception as e:
            code = f"Error fetching code: {e}"

        formatted_data.append({
            "id": submission.get("id"),
            "url": submission.get("url"),
            "title": submission.get("title"),
            "slug": submission.get("titleSlug"),
            "timestamp": submission.get("timestamp"),
            "status": submission.get("statusDisplay"),
            "lang": submission.get("lang"),
            "code": code,
            "result": submission.get("statusDisplay")
        })

        num_submissions += 1
        if num_submissions >= MAX_SUBMISSIONS:
            break
    
    return formatted_data

def print_submission_data(submission_data):
    for submission in submission_data:
        print(f"Id: {submission['id']}")
        print(f"Url: {submission['url']}")
        print(f"Title: {submission['title']}")
        print(f"Slug: {submission['slug']}")
        print(f"Timestamp: {submission['timestamp']}")
        print(f"Status: {submission['status']}")
        print(f"Language: {submission['lang']}")
        print(f"Code: {submission['code']}")
        print(f"Result: {submission['result']}")
        print("-" * 40)

def main():
    session = requests.Session()
    query_file = "query.graphql"
    graphql_query = load_graphql_query(query_file)

    session.headers.update({
        "Content-Type": "application/json",
    })

    variables = {
        "username": LEETCODE_USERNAME
    }

    try:
        create_new_session(session)

        response_data = send_graphql_request(session, graphql_query, variables)

        submission_data = extract_submission_data(session, response_data)

        print_submission_data(submission_data)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
