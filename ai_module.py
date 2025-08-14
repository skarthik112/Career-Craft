import google.generativeai as genai
import streamlit as st
import PIL.Image  # Import the Image processing library
from io import BytesIO  # Import BytesIO to handle image data
import base64
import json
import requests
import time

def setup_model(api_key):
    """
    Configures the Gemini API with the provided key and initializes the
    GenerativeModel.

    Args:
        api_key (str): The Gemini API key.
    
    Returns:
        genai.GenerativeModel: The initialized Gemini model.
    """
    genai.configure(api_key=api_key)
    # Using 'gemini-1.5-flash-latest' as a reliable and widely available model.
    return genai.GenerativeModel('gemini-1.5-flash-latest') 

@st.cache_data
def get_career_advice(_model, resume_text):
    """
    Generates detailed career advice based on the provided resume text using the model.
    
    Args:
        _model (genai.GenerativeModel): The initialized Gemini model.
        resume_text (str): The text extracted from the user's resume.

    Returns:
        str: The generated career advice.
    """
    prompt = f"""
    Based on this resume:
    {resume_text}

    1. Suggest 3 ideal career paths.
    2. Identify missing or weak skills.
    3. Recommend improvement areas.
    """
    response = _model.generate_content(prompt)
    return response.text

@st.cache_data
def get_short_career_advice(_model, resume_text):
    """
    Generates a brief summary of career advice.
    """
    prompt = f"""
    Based on this resume, provide a brief summary (in 2-3 sentences) of:
    1. The most suitable career path.
    2. The single most important skill to improve.
    """
    response = _model.generate_content(prompt)
    return response.text

@st.cache_data
def mock_interview(_model, user_input):
    """
    Generates a mock interview question and an ideal answer based on a given topic.
    """
    prompt = f"""
    Pretend you're an interviewer. Ask a technical question about '{user_input}' and provide an ideal answer.
    """
    response = _model.generate_content(prompt)
    return response.text

@st.cache_data
def get_trends_and_courses(_model, interest_area):
    """
    Generates current industry trends and top courses for a given area.
    """
    prompt = f"""
    What are current industry trends and top courses for {interest_area}?
    """
    response = _model.generate_content(prompt)
    return response.text

@st.cache_data
def find_similar_job_descriptions(_model, resume_text):
    """
    Simulates finding similar job descriptions using a prompt that acts like vector search.
    This demonstrates the concept without needing a full vector database.
    """
    prompt = f"""
    Given the following resume, generate 3 hypothetical job descriptions that have similar skills and requirements.
    This is a demonstration of how a vector search might work to find matching jobs.

    Resume:
    {resume_text}
    """
    response = _model.generate_content(prompt)
    return response.text

@st.cache_data
def create_image_caption(_model, image_bytes, prompt="Caption this image."):
    """
    Generates a caption for an uploaded image using a multimodal model.
    """
    img = PIL.Image.open(BytesIO(image_bytes))
    response = _model.generate_content([prompt, img])
    return response.text

@st.cache_data
def plan_sdlc_project(_model, project_idea):
    """
    Helps plan an end-to-end software development project.
    """
    prompt = f"""
    You are an expert DevOps and Application Developer.
    Based on this project idea: '{project_idea}', provide a detailed plan for the end-to-end Software Development Life Cycle (SDLC).
    The plan should include:
    1. A brief description of the user requirements.
    2. A suggested technology stack (e.g., Python, Streamlit, Gemini API).
    3. An outline of the project's key features.
    4. An initial code structure or a code snippet for a core component.
    5. A simple test plan for the application.
    """
    response = _model.generate_content(prompt)
    return response.text

@st.cache_data
def get_multimodal_career_advice(_model, resume_text, resume_images):
    """
    Generates detailed career advice based on the provided resume's text and images.
    
    This implements the "Inspect Rich Documents with Gemini Multimodality" badge.
    """
    prompt_parts = [
        f"""
        Based on this resume, which includes both text and images, charts, and tables,
        provide a detailed analysis. Your analysis should:

        1. Suggest 3 ideal career paths based on skills and experiences mentioned in the text and visuals.
        2. Identify missing or weak skills.
        3. Recommend improvement areas, referencing specific data from the resume where appropriate.
        """
    ]
    
    # Add image parts to the prompt_parts list
    for img_bytes in resume_images:
        img = PIL.Image.open(BytesIO(img_bytes))
        prompt_parts.append(img)
        
    response = _model.generate_content(prompt_parts)
    return response.text

@st.cache_data
def get_interpretable_and_fair_advice(_model, resume_text):
    """
    Generates career advice with an explanation and a fairness check.
    
    This implements the "Interpretability & Transparency" and "Fairness & Bias" badges.
    """
    prompt = f"""
    Based on the following resume:
    {resume_text}

    Please provide a detailed career analysis that includes:
    
    1.  **Career Advice**: Suggest 3 ideal career paths, identify missing skills, and recommend improvement areas.
    
    2.  **Reasoning**: Explain the specific reasons for your advice, referencing skills or experiences in the resume that led to each recommendation.
    
    3.  **Fairness Check**: Analyze your own advice for potential biases. Specifically, comment on whether the advice is fair and inclusive, and if it avoids making assumptions based on gender, age, or background.
    """
    response = _model.generate_content(prompt)
    return response.text

@st.cache_data
def generate_image_from_prompt(_prompt):
    """
    Generates an image from a text prompt using the gemini-2.0-flash-preview-image-generation model.

    This implements the "Introduction to Image Generation" badge.
    """
    import base64
    import json
    import requests
    import time
    
    payload = {
        "contents": [{
            "parts": [{ "text": _prompt }]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        },
    }
    
    api_key = "" # Leave this as an empty string.
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={api_key}"
    
    # The fetch call with exponential backoff
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            response.raise_for_status() # Raise an exception for bad status codes
            result = response.json()
            if result.get("candidates") and len(result["candidates"]) > 0:
                parts = result["candidates"][0]["content"]["parts"]
                for part in parts:
                    if "inlineData" in part:
                        base64_data = part["inlineData"]["data"]
                        # Create a data URL to display the image
                        return f"data:image/png;base64,{base64_data}"
                return None
            else:
                return None
        except requests.exceptions.RequestException as e:
            retries += 1
            delay = 2**retries  # Exponential backoff
            time.sleep(delay)
    
    return None
