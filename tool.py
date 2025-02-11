import requests
from bs4 import BeautifulSoup
from google import genai
from urllib.parse import urlparse
from typing import List, Optional
import re

# Initialize Gemini API using official docs
API_KEY = ""
client = genai.Client(api_key=API_KEY)

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
    Current task details: "{task_details}"

    Check for REQUIRED information:
    1. Subject Area:
       - What specific subject?
       - Which specific topic/subtopic?
    2. Task Details:
       - What type of task?
       - Which specific problems/concepts?
    3. Context:
       - What is current knowledge level?
       - What are the learning goals?
    4. Resource Needs:
       - What type of help is needed?
       - Any specific format requirements?

    Generate questions for ALL missing required information.
    Ignore information we already have.
    Questions must be specific and build on previous answers.

    Format:
    MISSING_CATEGORIES: (list categories with missing info)
    QUESTIONS: (one question per line)
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        response_text = response.text.strip()
        
        # Parse sections
        sections = {}
        current_section = None
        for line in response_text.split('\n'):
            if line.startswith(('HAVE:', 'MISSING:', 'QUESTIONS:')):
                current_section = line.split(':')[0]
                sections[current_section] = []
            elif current_section and line.strip():
                sections[current_section].append(line.strip())
        
        # If we have everything we need (no MISSING items), return no questions
        if 'MISSING' in sections and not sections['MISSING']:
            return []
            
        # Only return questions if we're missing critical information
        if 'QUESTIONS' in sections:
            return [Question(q) for q in sections['QUESTIONS'] if '?' in q]
        return []
        
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return []

def is_task_specific_enough(task_details):
    prompt = f"""
    Analyze task details: {task_details}

    Required Information Check:
    1. Subject Area (0-25):
       - Specific subject identified? (15)
       - Specific topic/subtopic clear? (10)
    
    2. Task Details (0-25):
       - Clear task type (homework, study, practice)? (15)
       - Specific problem/concept identified? (10)
    
    3. Context (0-25):
       - Current knowledge/level clear? (10)
       - Learning goals identified? (15)
    
    4. Resource Needs (0-25):
       - Type of help needed clear? (15)
       - Format/requirements specified? (10)

    Score each category and sum total (0-100).
    Task is specific enough only if ALL categories have points.
    Respond with only the number.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        cleaned_response = ''.join(filter(str.isdigit, response.text.strip()))
        if not cleaned_response:
            return False
            
        confidence = int(cleaned_response)
        # Require at least 20 points in each category (80 total)
        return confidence >= 80
    except Exception as e:
        print(f"Error checking task specificity: {str(e)}")
        return False

def ask_additional_questions(task_details: str) -> str:
    required_info_gathered = False
    iteration = 0
    max_iterations = 10  # Increased max iterations
    
    while not required_info_gathered and iteration < max_iterations:
        if is_task_specific_enough(task_details):
            required_info_gathered = True
            break
            
        questions = get_specific_questions(task_details)
        if not questions:
            # If no questions but not specific enough, generate fallback questions
            questions = [
                Question("What specific subject and topic is this for?"),
                Question("What exactly do you need to do?"),
                Question("What kind of help do you need?")
            ]
            
        print("\nLet's get more specific details about your task:")
        answers = []
        for question in questions:
            answer = question.ask()
            if not answer:  # If user doesn't provide answer, stop asking
                return task_details
            answers.append(f"{question.text}: {answer}")
        
        task_details = f"{task_details}\nAdditional Details: {'; '.join(answers)}"
        iteration += 1
    
    return task_details

def get_website_info(website):
    # Known educational platforms that might block scraping
    known_edu_platforms = {
        'classroom.google.com': {
            'title': 'Google Classroom',
            'description': 'Educational learning management system for schools',
            'type': 'lms',
            'features': ['assignments', 'course materials', 'teacher communication']
        },
        'khanacademy.org': {
            'title': 'Khan Academy',
            'description': 'Free educational resources and practice exercises',
            'type': 'learning',
            'features': ['lessons', 'practice', 'videos']
        },
        # Add more known platforms as needed
    }

    # Check if it's a known platform first
    parsed_url = urlparse(website)
    domain = parsed_url.netloc.lower()
    
    if domain in known_edu_platforms:
        platform = known_edu_platforms[domain]
        return "\n".join([
            f"Title: {platform['title']}",
            f"Description: {platform['description']}",
            f"Platform Type: {platform['type']}",
            f"Features: {', '.join(platform['features'])}",
            "Domain Analysis: educational: Yes",
            "Educational Platform: Yes",
            "Distraction Level: 0.1",  # Low distraction for dedicated edu platforms
            "Entertainment Elements: False",
            "Social Elements: Limited",
            "Advertisement Level: False"
        ])

    # Regular website analysis for unknown sites
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(website, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all text content
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Enhanced extraction of key information
        title = soup.title.string if soup.title else ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc else ""
        
        # Get main content safely
        headers = []
        try:
            headers = [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3']) if h.text.strip()][:5]
        except:
            headers = []
            
        paragraphs = []
        try:
            paragraphs = [p.text.strip() for p in soup.find_all('p') if p.text.strip()][:3]
        except:
            paragraphs = []
        
        # Domain analysis
        domain_indicators = {
            'educational': {
                'domains': ['classroom.google.com', 'khanacademy.org', 'quizlet.com', 
                          'education', 'learn', 'study', 'school', 'academic', 'math'],
                'keywords': ['math', 'learn', 'course', 'education', 'study', 'practice']
            },
            'professional': {
                'domains': ['github.com', 'gitlab.com', 'bitbucket.org', 'jira.com', 'confluence', 'docs.'],
                'keywords': ['documentation', 'repository', 'project', 'workflow', 'professional', 'enterprise']
            },
            'development': {
                'domains': ['stackoverflow.com', 'developer.', 'docs.', '.dev', 'api.'],
                'keywords': ['code', 'programming', 'developer', 'api', 'documentation', 'framework']
            },
            'creative': {
                'domains': ['behance.net', 'dribbble.com', 'adobe.', 'figma.com', 'canva.com'],
                'keywords': ['design', 'creative', 'artwork', 'portfolio', 'sketch', 'prototype']
            },
            'productivity': {
                'domains': ['notion.so', 'trello.com', 'asana.com', 'monday.com', 'clickup.com'],
                'keywords': ['task', 'project', 'organize', 'plan', 'collaborate', 'manage']
            }
        }

        # Safe domain checking
        domain_matches = {}
        try:
            for domain_type, indicators in domain_indicators.items():
                domain_match = any(d in website.lower() for d in indicators['domains'])
                keyword_match = any(word in str(soup).lower() for word in indicators['keywords'])
                domain_matches[domain_type] = {
                    'domain_match': domain_match,
                    'keyword_match': keyword_match
                }
        except:
            domain_matches = {'error': {'domain_match': False, 'keyword_match': False}}

        # Add distraction indicators
        distraction_indicators = {
            'entertainment': ['video', 'gaming', 'play', 'watch', 'stream', 'subscribe', 'channel'],
            'social': ['share', 'like', 'comment', 'follow', 'social', 'friend', 'community'],
            'ads': ['advertisement', 'sponsored', 'promotion', 'buy', 'shop', 'product'],
            'recommendations': ['recommended', 'suggested', 'trending', 'popular', 'for you']
        }
        
        # Count distracting vs productive elements
        distraction_count = 0
        total_elements = 0
        page_text = str(soup).lower()
        
        for category, keywords in distraction_indicators.items():
            for keyword in keywords:
                distraction_count += page_text.count(keyword)
                total_elements += 1
        
        # Calculate distraction ratio
        distraction_ratio = distraction_count / max(total_elements, 1)
        
        # Safer content summary construction
        content_parts = [
            f"Title: {title[:500] if title else 'No title'}",
            f"Description: {description[:500] if description else 'No description'}",
            "Headers: " + " | ".join(headers) if headers else "No headers found",
            "Content: " + " ".join(paragraphs) if paragraphs else "No content found",
            "Domain Analysis: " + ", ".join([
                f"{domain}: {'Yes' if matches['domain_match'] or matches['keyword_match'] else 'No'}"
                for domain, matches in domain_matches.items()
            ]),
            f"Distraction Level: {distraction_ratio:.2f}",
            f"Entertainment Elements: {any(word in page_text for word in distraction_indicators['entertainment'])}",
            f"Social Elements: {any(word in page_text for word in distraction_indicators['social'])}",
            f"Advertisement Level: {any(word in page_text for word in distraction_indicators['ads'])}"
        ]
        
        return "\n".join(content_parts)
        
    except Exception as e:
        print(f"Warning: Limited website info available - {str(e)}")
        return f"URL: {website}\nNote: Could not fetch complete information"

def determine_relevance(task_details, website):
    # Known educational platform scoring
    known_edu_platforms = {
        'classroom.google.com': 90,  # Very high base score for LMS
        'khanacademy.org': 85,
        'quizlet.com': 80,
        'desmos.com': 85,
        'purplemath.com': 80,
        'wolframalpha.com': 85,
        'ixl.com': 80
    }
    
    parsed_url = urlparse(website)
    domain = parsed_url.netloc.lower()
    
    # Special handling for known educational platforms
    if domain in known_edu_platforms:
        base_score = known_edu_platforms[domain]
        # Only adjust score down if task is clearly unrelated to platform's purpose
        if "math" in task_details.lower() and domain in ['classroom.google.com', 'khanacademy.org']:
            return True
        # For other cases, use the base score
        return base_score >= 75

    # Regular website analysis
    website_info = get_website_info(website)
    if not website_info or website_info.startswith("URL:"):
        return False

    # High-risk sites that require extra scrutiny
    high_distraction_domains = {
        'youtube.com': 0.8,  # Needs 80% confidence to be considered productive
        'facebook.com': 0.9,
        'twitter.com': 0.9,
        'instagram.com': 0.9,
        'tiktok.com': 0.9,
        'reddit.com': 0.85
    }
    
    threshold_modifier = 1.0
    for domain, required_confidence in high_distraction_domains.items():
        if domain in website.lower():
            threshold_modifier = required_confidence
            break

    prompt = f"""
    Task Requirements:
    {task_details}
    
    Website Analysis:
    {website_info}
    
    Evaluate this website carefully considering:
    
    1. Content Assessment (0-40 points):
    - Directly relevant content availability (+20)
    - Content quality and accuracy (+10)
    - Appropriate difficulty level (+10)
    
    2. Distraction Analysis (0-30 points):
    - Low presence of unrelated content (+10)
    - Minimal advertisements/promotions (+10)
    - Focus on educational/productive content (+10)
    
    3. Usability for Task (0-30 points):
    - Easy access to relevant content (+10)
    - Clear navigation to needed materials (+10)
    - Efficient use of time (+10)
    
    Important Rules:
    - Websites with high distraction ratios need exceptional educational value
    - Entertainment/social platforms must demonstrate clear educational focus
    - Consider the ratio of relevant vs irrelevant content
    - Account for potential time waste on unrelated content
    
    Respond with only a number 0-100 representing overall productivity score.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        base_confidence = int(response.text.strip())
        
        # Apply threshold modifier for high-distraction sites
        final_confidence = base_confidence * threshold_modifier
        
        return final_confidence >= 75  # Increased base threshold
    except Exception as e:
        print(f"Error determining relevance: {e}")
        return False

def main():
    print("\n" + "=" * 80)
    print("Website Productivity Analyzer".center(80))
    print("=" * 80 + "\n")
    
    task = get_user_task()
    while True:
        website = input("\nEnter the website URL to analyze (or 'exit' to quit): ")
        if website.lower() in ['exit', 'quit']:
            break
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
