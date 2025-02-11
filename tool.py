import openai
import requests
from bs4 import BeautifulSoup

def get_user_task():
    task = input("Please enter the task you want to achieve: ")
    if is_task_too_general(task):
        task = ask_additional_questions(task)
    return task

def is_task_too_general(task):
    # Placeholder for logic to determine if the task is too general
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Is the task '{task}' too general?",
        max_tokens=10
    )
    return response.choices[0].text.strip().lower() == "yes"

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
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Is the website {website} relevant for the task {task}? Here is some information from the website: {website_info}",
        max_tokens=10
    )
    relevance = response.choices[0].text.strip().lower()
    return relevance == "yes"

def main():
    task = get_user_task()
    websites = ["https://example.com", "https://anotherexample.com"]  # Replace with actual list of websites
    productive_websites = []

    for website in websites:
        if determine_relevance(task, website):
            productive_websites.append(website)

    print("Productive websites for your task:", productive_websites)

if __name__ == "__main__":
    main()
