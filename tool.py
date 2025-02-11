import requests
from bs4 import BeautifulSoup
from google import genai
from urllib.parse import urlparse

def get_user_task():
    initial_task = input("Please enter the task you want to achieve: ")
    return ask_additional_questions(initial_task)

def get_specific_questions(task_details):
    prompt = f"""
    Based on these task details: "{task_details}"
    
    Generate detailed questions to understand the user's exact needs.
    Focus on:
    - Technical requirements
    - Skill level and background
    - Specific goals and outcomes
    - Time constraints
    - Required resources
    - Practical use cases
    
    Format: Generate 3-5 specific, detailed questions that haven't been asked before.
    If the task is already specific enough, respond with "SUFFICIENT_DETAIL".
    """
    
    try:
        client = genai.Client(api_key="YOUR_API_KEY")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def is_task_specific_enough(task_details):
    prompt = f"""
    Analyze the following task details:
    {task_details}

    Evaluate if we have enough specific information to judge website relevance with high accuracy.
    Consider if we know:
    1. Exact technical requirements
    2. User's skill level
    3. Specific goals
    4. Time constraints
    5. Required resources
    6. Practical applications

    Respond with exactly 'yes' if we have sufficient detail, 'no' if we need more information.
    """
    
    try:
        client = genai.Client(api_key="YOUR_API_KEY")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip().lower() == "yes"
    except Exception as e:
        print(f"Error checking task specificity: {e}")
        return False

def ask_additional_questions(task_details):
    while not is_task_specific_enough(task_details):
        print("\nLet's gather more specific information:")
        questions = get_specific_questions(task_details)
        
        if questions == "SUFFICIENT_DETAIL":
            break
            
        if isinstance(questions, str):
            questions = questions.split('\n')
        
        new_answers = []
        for question in questions:
            if question and len(question.strip()) > 0:
                answer = input(f"{question.strip()}\nYour answer: ")
                new_answers.append(f"{question.strip()}: {answer}")
        
        task_details = f"{task_details}\nAdditional Details: {'; '.join(new_answers)}"
        print("\nAnalyzing if we need more information...")
    
    return task_details

def get_website_info(website):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(website, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all text content
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Extract key information
        title = soup.title.string if soup.title else ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else ""
        
        # Get main content and important headers
        headers = [h.text for h in soup.find_all(['h1', 'h2', 'h3'])]
        paragraphs = [p.text.strip() for p in soup.find_all('p') if len(p.text.strip()) > 50]
        
        content_summary = "\n".join([
            f"Title: {title}",
            f"Description: {description}",
            "Main Headers: " + " | ".join(headers[:5]),
            "Content Excerpts: " + " ".join(paragraphs[:3])
        ])
        
        return content_summary
    except Exception as e:
        print(f"Error fetching website info: {e}")
        return ""

def determine_relevance(task_details, website):
    website_info = get_website_info(website)
    
    prompt = f"""
    Detailed Task Requirements:
    {task_details}
    
    Website URL: {website}
    Website Content:
    {website_info}
    
    Analyze the website's productivity value for this specific task:
    1. How well does it match the exact technical requirements?
    2. Is it appropriate for the user's stated skill level?
    3. Does it help achieve the specific goals mentioned?
    4. Does it fit within the time constraints?
    5. Does it provide the required resources?
    6. Is it practical for the stated use cases?
    
    Provide a 'yes' only if the website is highly relevant and productive for these specific needs.
    Otherwise respond with 'no'.
    """
    
    try:
        client = genai.Client(api_key="YOUR_API_KEY")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        # Check if the response is valid
        if response and hasattr(response, 'text'):
            return response.text.strip().lower() == "yes"
        return False
        
    except Exception as e:
        print(f"Error determining relevance: {e}")
        return False

def main():
    task = get_user_task()
    website = input("Enter the website URL to analyze: ")
    
    print(f"\nAnalyzing {website} for productivity...")
    if determine_relevance(task, website):
        print(f"\n✅ {website} is productive for your task.")
    else:
        print(f"\n❌ {website} is not productive for your task.")

if __name__ == "__main__":
    main()
