import requests
from bs4 import BeautifulSoup
from google import genai
from urllib.parse import urlparse
from typing import List, Optional
import re

class Question:
    def __init__(self, text: str):
        self.text = self.clean_question(text)
    
    @staticmethod
    def clean_question(text: str) -> str:
        # Remove markdown, numbering, and extra spaces
        text = re.sub(r'\*\*|\d+\.\s+', '', text)
        return text.strip()
    
    def ask(self) -> str:
        print("\n" + "-" * 80)
        print(f"Question: {self.text}")
        print("-" * 80)
        return input("Your answer: ").strip()

def get_user_task():
    initial_task = input("Please enter the task you want to achieve: ")
    return ask_additional_questions(initial_task)

def get_specific_questions(task_details: str) -> List[Question]:
    prompt = f"""
    Based on these task details: "{task_details}"
    
    Generate 3 concise but specific questions about:
    1. The exact goal/output needed
    2. Technical requirements or constraints
    3. User's background/experience level
    
    Format: Return only the questions, one per line.
    Each question should be clear, direct, and require a specific answer.
    If task is already specific enough, respond with exactly "SUFFICIENT_DETAIL"
    """
    
    try:
        client = genai.Client(api_key="YOUR_API_KEY")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        response_text = response.text.strip()
        
        if response_text == "SUFFICIENT_DETAIL":
            return []
            
        # Filter out empty lines and create Question objects
        questions = [Question(q) for q in response_text.split('\n') if q.strip()]
        return questions[:3]  # Limit to 3 questions
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

def ask_additional_questions(task_details: str) -> str:
    iteration = 1
    max_iterations = 3
    
    while iteration <= max_iterations:
        print(f"\n[Round {iteration}/{max_iterations}] Analyzing task specificity...")
        
        questions = get_specific_questions(task_details)
        if not questions:
            print("\n✅ Task is now specific enough!")
            break
            
        print("\nLet's get more specific details about your task:")
        answers = []
        for question in questions:
            answer = question.ask()
            if answer:
                answers.append(f"{question.text}: {answer}")
        
        task_details = f"{task_details}\nDetails (Round {iteration}): {'; '.join(answers)}"
        iteration += 1
    
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
    print("\n" + "=" * 80)
    print("Website Productivity Analyzer".center(80))
    print("=" * 80 + "\n")
    
    task = get_user_task()
    website = input("\nEnter the website URL to analyze: ")
    
    print("\n" + "-" * 80)
    print(f"Analyzing {website} for productivity...")
    print("-" * 80)
    
    if determine_relevance(task, website):
        print(f"\n✅ {website} is productive for your task.")
    else:
        print(f"\n❌ {website} is not productive for your task.")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
