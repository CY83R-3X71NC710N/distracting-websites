import openai

def get_user_task():
    task = input("Please enter the task you want to achieve: ")
    return task

def determine_relevance(task, website):
    # Placeholder for AI logic to determine relevance based on task
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Is the website {website} relevant for the task {task}?",
        max_tokens=10
    )
    relevance = response.choices[0].text.strip().lower()
    return relevance == "yes"

def main():
    task = get_user_task()
    websites = ["example.com", "anotherexample.com"]  # Replace with actual list of websites
    productive_websites = []

    for website in websites:
        if determine_relevance(task, website):
            productive_websites.append(website)

    print("Productive websites for your task:", productive_websites)

if __name__ == "__main__":
    main()
