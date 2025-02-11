import requests
from bs4 import BeautifulSoup
from google import genai

def get_user_task():
    task = input("Please enter the task you want to achieve: ")
    if is_task_too_general(task):
        task = ask_additional_questions(task)
    return task

def is_task_too_general(task):
    # Placeholder for logic to determine if the task is too general
    client = genai.Client(api_key="YOUR_API_KEY")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=f"Is the task '{task}' too general?"
    )
    return response.text.strip().lower() == "yes"

def ask_additional_questions(task):
    additional_info = input("Your task seems too general. Can you provide more details? ")
    return f"{task} - {additional_info}"

def get_website_info(website):
    try:
        response = requests.get(website)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except Exception as e:
        print(f"Error fetching website info: {e}")
        return ""

def determine_relevance(task, website):
    website_info = get_website_info(website)
    client = genai.Client(api_key="YOUR_API_KEY")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=f"Is the website {website} relevant for the task {task}? Here is some information from the website: {website_info}"
    )
    relevance = response.text.strip().lower()
    return relevance == "yes"

def main():
    task = get_user_task()
    websites = ["https://github.com"]  # Replace with actual list of websites
    productive_websites = []

    for website in websites:
        if determine_relevance(task, website):
            productive_websites.append(website)

    print("Productive websites for your task:", productive_websites)

if __name__ == "__main__":
    main()
