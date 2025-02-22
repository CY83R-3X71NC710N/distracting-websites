# Possible AI Adaption:
One way to accelerate this project would be to use AI. This originally would have been something that was impossible to have a list of every addicting site. However, if you find a way to utilize existing-developed AI tools to detect whether a site is distracting or not, you could accelerate this project significantly. This would make the list adaptable, which is crucial for detecting whether a site is distracting or not. Another factor to take into account would be how the user is using the website. This could be provided to the AI by telling it what your use-case is and having an adaptable list based on that, blocking websites that are not relevant to the task.

# Initial Hurdle:
Real-time content analysis and categorization is required.

# What exists now:

* Website Categorization APIs: Several APIs (like Google Cloud's Natural Language API, Amazon Comprehend, or specialized website categorization services) can analyze website content and attempt to categorize it (e.g., news, social media, shopping). These are a good starting point but aren't perfect at detecting "distraction" as it's subjective.
* Browser Extensions with Blocking Features: Many browser extensions (like StayFocusd, LeechBlock, or similar) allow you to block websites based on lists or schedules. These are powerful but rely on manually curated lists.
* Focus Apps: Apps like Freedom or Cold Turkey can block distracting apps and websites across devices, often with scheduling features. Again, they usually rely on pre-defined lists.
* User Input Prompt: The tool now asks the user for the task they want to achieve before determining if a website is productive. This user input is used by the AI to determine the relevance of websites.

# Privacy/Security Issues:
Manual lists can be used and input by the user for sites the AI should not analyze. These include banking sites, etc. Or... Another solution would be completely running the AI locally. This would slow down the computer and likely have safety issues if local files are deleted using urandom overwrite. Obviously, it would be much faster to find a middle ground and just not scan sites that contain sensitive data. However, as computers evolve, this task becomes more trivial and more security-focused.

# Ambitious. Is it achievable?

Yes, this project is fully achievable considering the technology that is available today. It just has to be done. I currently lack the time to put this into practicality. However, soon I will have the time, and then I will develop this project.

# The Issue:
Currently, websites are not the only distracting element of computers; there are also apps. AI-detection of apps is where the practicality of the project goes down, so I am actively brainstorming solutions to this dilemma.

# My Take On Existing Tools:
They are not effective considering the adaptable nature of websites. However, with the rise of AI, this can be resolved.

# What could a tool like this do?:

A tool like this that combines both browser blocking functionality (websites) and app blocking functionality (TBD) would be game-changing for productivity both in schools, the workplace, and overall more healthy use of computers in an information-overloaded society. Having the AI determine what is useful for the given task and blocking what is not is not just a tool at this point. It is freedom to have computers be your asset, not your liability. This would revolutionize computers once again, allowing distractions to be eliminated. When tools are properly utilized, I would expect workplace productivity to skyrocket to rates that have not been seen before. Higher workflow economy means higher GDP, which means a healthier life according to the HDI index. The new feature of asking the user for their task before determining if a website is productive enhances the tool's ability to block irrelevant websites and improve productivity.

# Power of Audio in Computers.

Your eyes control your focus; this has been backed by neuroscientific studies. However, audio remains the key issue when it comes to distractions. Audio is the most distracting of the five senses, which is why when using a computer, it is effective to use a tool like brain.fm or endel to create a personalized focus environment. So by blocking websites and apps, the eyes are controlled. By using the audio, the ears are controlled. By using the keyboard, the tactile senses are controlled. This would create the most productive computer in the world. The next task would be using AI to assist with what to spend time on, not how you spend the time.

# Eventually Integration

I will integrate the tool with todoist to have it automatically use the API to fetch the tasks and update the tool to tell you the current task based on what you have in todoist and block until the task is done.

# New Feature: User Input for Task

The tool now includes a feature that asks the user for the task they want to achieve before determining if a website is productive. This user input is used by the AI to determine the relevance of websites, making the tool more effective in blocking irrelevant websites and improving productivity.

# New Feature: Obtaining Information Directly from Websites

The tool now includes a feature that obtains information directly from the website to determine its relevance for the task. This allows the AI to make more informed decisions about whether a website is productive or not, improving the accuracy of the tool.

# New Feature: Asking Additional Questions

The tool now includes a feature that asks the user additional questions if the task they provide is too general. This helps the AI to better understand the user's needs and make more accurate determinations about the relevance of websites.

# TODO:
The AI needs to ask additional questions about their task if they provide a task too general, and it needs to find information directly from the website to determine if it is productive for the task.

# Installation

To use the Gemini API, you need to install the `google-genai` package. You can do this using pip:

```sh
pip install -q -U google-genai
```

# Obtaining a Gemini API Key

To use the Gemini API, you need to obtain an API key from Google AI Studio. Follow these steps:

1. Go to the [Google AI Studio](https://ai.google.com/studio) website.
2. Sign in with your Google account.
3. Navigate to the API section and generate a new API key.
4. Copy the API key and use it in your code.

# Example Code

Here is an example of how to use the Gemini API to generate content:

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works"
)
print(response.text)
```

# Further Goals
Develop a browser extension which integrates with our python and only allows you to use the browser once you have answered the questions, additionally, it should display block screens for websites you cannot use and a splash screen while the content is being filtered.