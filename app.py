import streamlit as st
import os
import google.api_core.exceptions
import ai_module
from resume_parser import extract_text_and_images_from_pdf
from utils import is_safe
import base64
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="CareerCraft - AI Career Guide",
    page_icon="💼",
    layout="wide",
)

# --- Custom Styling (Creative UI & Navigation) ---
st.markdown("""
<style>
    /* Main app container */
    .stApp {
        background: linear-gradient(135deg, #0a192f, #1b2735);
        color: #e6e6e6;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Fixed Top Navigation Bar */
    .navbar {
        display: flex;
        justify-content: center;
        background-color: #0a192f; /* Dark background for navbar */
        padding: 1rem 0;
        gap: 20px;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }
    .navbar a {
        color: #ccd6f6;
        text-decoration: none;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        padding: 10px 15px;
        border-radius: 5px;
    }
    .navbar a:hover {
        color: #64ffda;
        background-color: rgba(100, 255, 218, 0.1);
        transform: translateY(-2px);
    }

    /* Main content block container */
    .main .block-container {
        max-width: 1200px;
        padding-top: 3rem;
        padding-bottom: 3rem;
        background: rgba(30, 41, 59, 0.9);
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-top: 20px;
    }
    
    /* Title and text styling */
    h1 {
        font-size: 7rem; /* Increased font size for h1 */
        color: #64ffda;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
        margin-bottom: 0.5rem;
    }
    h3 {
        color: #64ffda;
        border-left: 5px solid #64ffda;
        padding-left: 10px;
    }
    p {
        color: #ccd6f6;
        font-size: 1.2rem;
    }

    /* Buttons */
    .stButton>button {
        background-color: #172a45; /* Dark background for visibility */
        color: #ccd6f6; /* Lighter text for contrast */
        border-radius: 50px;
        border: none;
        padding: 12px 30px;
        font-size: 1.1rem;
        font-weight: bold;
        box-shadow: 0 5px 15px rgba(100, 255, 218, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #51e6b3;
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(100, 255, 218, 0.3);
    }
    .stButton>button:active {
        transform: translateY(0);
    }

    /* Input text boxes */
    .stTextInput>div>div>input {
        border-radius: 12px;
        background-color: #172a45;
        color: #ccd6f6;
        border: 1px solid #64ffda;
    }
    
    /* Star Rating CSS */
    .star-rating {
      display: flex;
      flex-direction: row-reverse;
      justify-content: center;
      font-size: 2rem;
      color: #999;
      cursor: pointer;
    }
    .star-rating input {
      display: none;
    }
    .star-rating label {
      color: #999;
      transition: color 0.2s;
    }
    .star-rating input:checked ~ label {
      color: #ffc700;
    }
    .star-rating label:hover,
    .star-rating label:hover ~ label {
      color: #ffc700;
    }

    /* Animation for the new caption */
    @keyframes highlight {
        0%   {color: #ccd6f6;}
        50%  {color: #64ffda; text-shadow: 0 0 5px #64ffda;}
        100% {color: #ccd6f6;}
    }
    .animated-caption {
        font-size: 2.8rem; /* Increased font size for animated caption */
        font-weight: bold;
        animation: highlight 3s infinite;
    }
    .header-logo-title {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        padding-top: 20px;
        padding-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize a session state variable to keep track of resumes analyzed.
if 'resume_count' not in st.session_state:
    st.session_state.resume_count = 0

# Use a column to place the metric at the top-left of the main content
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.metric("Resumes Analyzed", st.session_state.resume_count)

# --- Top Section: Logo + Title Above Navbar ---
with col2:
    st.markdown("<div id='home-section'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align:center;">
            <div class="header-logo-title">
                <img src="https://placehold.co/120x120/172a45/64ffda?text=CC" alt="CareerCraft Logo" style="border-radius: 50%; width: 120px; height: 120px;">
                <h1>CareerCraft</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)

# New section for the animated caption
with col2:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <p class="animated-caption">Your Future Starts Today.</p>
        </div>
    """, unsafe_allow_html=True)

# --- Top Navigation Bar ---
# Added HTML with anchor links
st.markdown("""
<div class="navbar">
    <a href="#about-section">About</a>
    <a href="#career-guidance-section">Career Guidance</a>
    <a href="#mock-interview-section">Mock Interview</a>
    <a href="#trends-section">Industry Trends</a>
    <a href="#image-captioning-section">Image Captioner</a>
    <a href="#sdlc-section">Project Planner</a>
    <a href="#feedback-section">Feedback</a>
</div>
""", unsafe_allow_html=True)

# Use an environment variable for the API key instead of a text input
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API key not found. Please set the GEMINI_API_KEY environment variable.")
    st.info("Example for Windows: `setx GEMINI_API_KEY \"YOUR_KEY_HERE\"`")
    st.info("Example for Mac/Linux: `export GEMINI_API_KEY=\"YOUR_KEY_HERE\"`")
    st.stop()


model = ai_module.setup_model(api_key)

# --- About Section ---
st.markdown("<div id='about-section'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("ℹ️ About CareerCraft")
st.markdown("""
### Project Overview

CareerCraft is a Generative AI-powered web application designed to assist students and professionals in their career journey. It leverages Google's Gemini API to provide intelligent and personalized guidance.

### Key Features
- **Enhanced Resume Analysis:** Get tailored career path suggestions based on both text and visual data (like charts and images) from your resume.
- **Mock Interview Practice:** Prepare for job interviews with dynamically generated questions and ideal answers on any topic.
- **Industry Trends:** Stay updated with the latest industry trends and get course recommendations to enhance your skills.
- **Image Captioning:** Use AI to generate descriptive captions for your images.
- **Project Planner:** Get a complete plan for your next software development project.
- **Responsible AI Features:** Interpret AI reasoning and check for potential biases in the advice.

### Technology Stack
- **Frontend:** Streamlit for a fast and interactive web interface.
- **Backend/AI:** Google Gemini API for powerful text generation and analysis.
- **Data Processing:** PyMuPDF and Pillow for robust PDF resume parsing including text and images.
- **Responsible AI:** Custom features to ensure the quality and appropriateness of the generated content.
""")


# --- Career Guidance Section ---
st.markdown("<div id='career-guidance-section'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("📄 Career-Based Guidance")
st.markdown("Upload your resume and get tailored advice on career paths and skill development.")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=['pdf'])

# Add a checkbox for the new responsible AI feature
use_responsible_ai = st.checkbox("Enable Responsible AI Features (Interpretability & Bias Check)")

if uploaded_file:
    # Use the new function to get both text and images
    resume_text, resume_images = extract_text_and_images_from_pdf(uploaded_file)

    st.info("Resume Preview:")
    st.text_area("Extracted Text:", resume_text, height=200)

    advice_type = st.radio("Choose advice length:", ("Detailed", "Short"))

    if st.button("Get Career Guidance"):
        with st.spinner("Generating personalized advice..."):
            try:
                # Conditionally call the appropriate function based on the checkbox
                if use_responsible_ai:
                    advice = ai_module.get_interpretable_and_fair_advice(model, resume_text)
                elif advice_type == "Detailed":
                    advice = ai_module.get_career_advice(model, resume_text)
                else:
                    advice = ai_module.get_short_career_advice(model, resume_text)

                if is_safe(advice):
                    st.success("🎓 Career Advice")
                    st.write(advice)
                    st.session_state.resume_count += 1
                else:
                    st.error("Inappropriate content detected in the response. Try with a different input.")
            except google.api_core.exceptions.ResourceExhausted:
                st.error("You've exceeded your API quota. Please try again in a few minutes.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# --- Mock Interview Section ---
st.markdown("<div id='mock-interview-section'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("🗣️ Mock Interview Practice")
st.markdown("Practice for your next interview by generating questions based on any topic.")
interview_topic = st.text_input("Enter a topic (e.g., 'Python data structures', 'Cloud computing'):")
if st.button("Start Mock Interview"):
    if interview_topic:
        with st.spinner(f"Generating a question on '{interview_topic}'..."):
            try:
                interview_response = ai_module.mock_interview(model, interview_topic)
                if is_safe(interview_response):
                    st.info("Here is your mock interview question and an ideal answer:")
                    st.write(interview_response)
                else:
                    st.error("Inappropriate content detected.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic to start the interview.")

# --- Industry Trends & Courses Section ---
st.markdown("<div id='trends-section'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("📈 Industry Trends & Courses")
st.markdown("Discover the latest trends and get course suggestions in your area of interest.")
interest_area = st.text_input("Enter an area of interest (e.g., 'Generative AI', 'Cybersecurity'):")
if st.button("Get Trends & Courses"):
    if interest_area:
        with st.spinner(f"Searching for trends in '{interest_area}'..."):
            try:
                trends_response = ai_module.get_trends_and_courses(model, interest_area)
                if is_safe(trends_response):
                    st.info("Here are the latest trends and course suggestions:")
                    st.write(trends_response)
                else:
                    st.error("Inappropriate content detected.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter an area of interest.")

# --- Image Captioning Section ---
st.markdown("<div id='image-captioning-section'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("📸 Image Captioning")
st.markdown("Upload an image and let AI describe it for you.")

uploaded_image = st.file_uploader("Upload an image (JPG, PNG)", type=['jpg', 'jpeg', 'png'])
if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", width=500)
    if st.button("Generate Caption"):
        with st.spinner("Generating caption..."):
            try:
                image_bytes = uploaded_image.getvalue()
                caption = ai_module.create_image_caption(model, image_bytes)
                if is_safe(caption):
                    st.success("📝 Image Caption")
                    st.write(caption)
                else:
                    st.error("Inappropriate content detected.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- End-to-End SDLC Project Planner Section ---
st.markdown("<div id='sdlc-section'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("⚙️ End-to-End SDLC Project Planner")
st.markdown("Get a complete project plan, from requirements to code, for your next idea.")

project_idea = st.text_input("Enter your project idea (e.g., 'a weather forecast app'):")

if st.button("Generate Project Plan"):
    if project_idea:
        with st.spinner(f"Generating a plan for '{project_idea}'..."):
            try:
                plan = ai_module.plan_sdlc_project(model, project_idea)
                if is_safe(plan):
                    st.success("✅ Project Plan Generated")
                    st.write(plan)
                else:
                    st.error("Inappropriate content detected.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a project idea.")

# --- Feedback Section ---
st.markdown("<div id='feedback-section'></div>", unsafe_allow_html=True)
st.markdown("---")
st.header("💌 Provide Feedback")
st.markdown("Help us improve the quality of the advice by providing your feedback.")
with st.form("feedback_form"):
    st.subheader("Your Feedback")
    user_name = st.text_input("Your Name (Optional):")
    feedback = st.text_area("Your feedback on the generated response:")
    
    # New star rating system using custom CSS
    st.markdown("""
        <div class="star-rating">
            <input type="radio" id="star5" name="rating" value="5" /><label for="star5" title="5 stars">★</label>
            <input type="radio" id="star4" name="rating" value="4" /><label for="star4" title="4 stars">★</label>
            <input type="radio" id="star3" name="rating" value="3" /><label for="star3" title="3 stars">★</label>
            <input type="radio" id="star2" name="rating" value="2" /><label for="star2" title="2 stars">★</label>
            <input type="radio" id="star1" name="rating" value="1" /><label for="star1" title="1 star">★</label>
        </div>
    """, unsafe_allow_html=True)
    
    submit_button = st.form_submit_button("Submit Feedback")

    if submit_button:
        if feedback:
            st.success("Thank you for your feedback! It has been submitted.")
            st.markdown(f"**Name:** {user_name if user_name else 'Anonymous'}")
            st.markdown("**Rating:** We appreciate your rating!")
            st.markdown(f"**Feedback:** {feedback}")
        else:
            st.warning("Please enter some feedback before submitting.")




# import streamlit as st
# import os
# import google.api_core.exceptions
# import ai_module
# from resume_parser import extract_text_and_images_from_pdf
# from utils import is_safe

# # ------------------ PAGE CONFIG ------------------
# st.set_page_config(
#     page_title="CareerCraft - AI Career Guide",
#     page_icon="💼",
#     layout="wide",
# )

# # ------------------ CUSTOM STYLING ------------------
# st.markdown("""
# <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
# <style>
#     body, .stApp {
#         font-family: 'Poppins', sans-serif;
#         background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
#         color: #fff;
#     }
#     /* Navbar */
#     .navbar {
#         display: flex;
#         justify-content: center;
#         align-items: center;
#         gap: 25px;
#         padding: 1rem 0;
#         position: sticky;
#         top: 0;
#         background: rgba(15, 32, 39, 0.85);
#         backdrop-filter: blur(10px);
#         z-index: 999;
#         border-bottom: 1px solid rgba(255,255,255,0.1);
#     }
#     .navbar a {
#         text-decoration: none;
#         font-weight: 600;
#         color: #ccc;
#         transition: all 0.3s ease;
#         padding: 8px 14px;
#         border-radius: 8px;
#     }
#     .navbar a:hover {
#         background: rgba(255,255,255,0.1);
#         color: #64ffda;
#     }
#     /* Hero Section */
#     .hero {
#         text-align: center;
#         padding: 60px 20px;
#         background: rgba(255,255,255,0.05);
#         border-radius: 20px;
#         margin-top: 20px;
#         animation: fadeIn 1s ease-in-out;
#     }
#     .hero h1 {
#         font-size: 4rem;
#         font-weight: 700;
#         color: #64ffda;
#         margin-bottom: 15px;
#     }
#     .hero p {
#         font-size: 1.3rem;
#         color: #ddd;
#         max-width: 700px;
#         margin: 0 auto;
#         margin-bottom: 25px;
#     }
#     /* Cards */
#     .card {
#         background: rgba(255,255,255,0.07);
#         padding: 25px;
#         border-radius: 16px;
#         backdrop-filter: blur(10px);
#         box-shadow: 0 6px 20px rgba(0,0,0,0.2);
#         transition: all 0.3s ease;
#         margin-bottom: 25px;
#     }
#     .card:hover {
#         transform: translateY(-5px);
#         box-shadow: 0 8px 25px rgba(0,0,0,0.3);
#     }
#     /* Star Rating */
#     .star-rating {
#       display: flex;
#       flex-direction: row-reverse;
#       justify-content: center;
#       font-size: 2rem;
#       color: #999;
#       cursor: pointer;
#     }
#     .star-rating input { display: none; }
#     .star-rating label {
#       color: #999;
#       transition: color 0.2s;
#     }
#     .star-rating input:checked ~ label {
#       color: #ffc700;
#     }
#     .star-rating label:hover,
#     .star-rating label:hover ~ label {
#       color: #ffc700;
#     }
#     /* Animation */
#     @keyframes fadeIn {
#         from { opacity: 0; transform: translateY(15px); }
#         to { opacity: 1; transform: translateY(0); }
#     }
# </style>
# """, unsafe_allow_html=True)

# # ------------------ NAVBAR ------------------
# st.markdown("""
# <div class="navbar">
#     <a href="#about-section">ℹ️ About</a>
#     <a href="#career-guidance-section">📄 Career Guidance</a>
#     <a href="#mock-interview-section">🎤 Mock Interview</a>
#     <a href="#trends-section">📈 Trends</a>
#     <a href="#image-captioning-section">🖼 Captioner</a>
#     <a href="#sdlc-section">⚙️ Planner</a>
#     <a href="#feedback-section">💌 Feedback</a>
# </div>
# """, unsafe_allow_html=True)

# # ------------------ HERO SECTION ------------------
# st.markdown("""
# <div class="hero">
#     <h1>CareerCraft</h1>
#     <p>Your AI Career Companion – get personalized career guidance, practice interviews, explore trends, and plan projects with ease.</p>
# </div>
# """, unsafe_allow_html=True)

# # ------------------ API KEY ------------------
# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     st.error("API key not found. Please set the GEMINI_API_KEY environment variable.")
#     st.stop()

# model = ai_module.setup_model(api_key)

# # ------------------ ABOUT ------------------
# st.markdown("<div id='about-section'></div>", unsafe_allow_html=True)
# st.subheader("ℹ️ About CareerCraft")
# st.markdown("""
# CareerCraft is a Generative AI-powered web application designed to assist students and professionals in their career journey.
# It leverages Google's Gemini API to provide intelligent and personalized guidance.

# **Key Features**
# - Enhanced Resume Analysis
# - Mock Interview Practice
# - Industry Trends Insights
# - AI Image Captioning
# - End-to-End Project Planner
# """)

# # ------------------ CAREER GUIDANCE ------------------
# st.markdown("<div id='career-guidance-section'></div>", unsafe_allow_html=True)
# st.subheader("📄 Career-Based Guidance")
# st.markdown("Upload your resume and get tailored advice on career paths and skill development.")
# with st.container():
#     st.markdown('<div class="card">', unsafe_allow_html=True)
#     uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=['pdf'])
#     use_responsible_ai = st.checkbox("Enable Responsible AI Features")
#     if uploaded_file:
#         resume_text, resume_images = extract_text_and_images_from_pdf(uploaded_file)
#         st.text_area("Extracted Text", resume_text, height=200)
#         advice_type = st.radio("Choose advice length:", ("Detailed", "Short"))
#         if st.button("Get Career Guidance"):
#             with st.spinner("Generating advice..."):
#                 try:
#                     if use_responsible_ai:
#                         advice = ai_module.get_interpretable_and_fair_advice(model, resume_text)
#                     elif advice_type == "Detailed":
#                         advice = ai_module.get_career_advice(model, resume_text)
#                     else:
#                         advice = ai_module.get_short_career_advice(model, resume_text)
#                     if is_safe(advice):
#                         st.success("🎓 Career Advice")
#                         st.write(advice)
#                     else:
#                         st.error("Inappropriate content detected.")
#                 except Exception as e:
#                     st.error(f"Error: {e}")
#     st.markdown('</div>', unsafe_allow_html=True)

# # ------------------ MOCK INTERVIEW ------------------
# st.markdown("<div id='mock-interview-section'></div>", unsafe_allow_html=True)
# st.subheader("🎤 Mock Interview Practice")
# st.markdown("Practice for your next interview by generating questions based on any topic.")
# with st.container():
#     st.markdown('<div class="card">', unsafe_allow_html=True)
#     interview_topic = st.text_input("Enter a topic:")
#     if st.button("Start Mock Interview"):
#         if interview_topic:
#             try:
#                 response = ai_module.mock_interview(model, interview_topic)
#                 if is_safe(response):
#                     st.info(response)
#                 else:
#                     st.error("Inappropriate content detected.")
#             except Exception as e:
#                 st.error(e)
#     st.markdown('</div>', unsafe_allow_html=True)

# # ------------------ TRENDS ------------------
# st.markdown("<div id='trends-section'></div>", unsafe_allow_html=True)
# st.subheader("📈 Industry Trends & Courses")
# st.markdown("Discover the latest trends and get course suggestions in your area of interest.")
# with st.container():
#     st.markdown('<div class="card">', unsafe_allow_html=True)
#     interest_area = st.text_input("Enter an area of interest:")
#     if st.button("Get Trends & Courses"):
#         if interest_area:
#             try:
#                 trends = ai_module.get_trends_and_courses(model, interest_area)
#                 if is_safe(trends):
#                     st.info(trends)
#                 else:
#                     st.error("Inappropriate content detected.")
#             except Exception as e:
#                 st.error(e)
#     st.markdown('</div>', unsafe_allow_html=True)

# # ------------------ IMAGE CAPTIONING ------------------
# st.markdown("<div id='image-captioning-section'></div>", unsafe_allow_html=True)
# st.subheader("🖼 Image Captioning")
# st.markdown("Upload an image and let AI describe it for you.")
# with st.container():
#     st.markdown('<div class="card">', unsafe_allow_html=True)
#     uploaded_image = st.file_uploader("Upload an image", type=['jpg','jpeg','png'])
#     if uploaded_image:
#         st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
#         if st.button("Generate Caption"):
#             try:
#                 caption = ai_module.create_image_caption(model, uploaded_image.getvalue())
#                 if is_safe(caption):
#                     st.success(caption)
#                 else:
#                     st.error("Inappropriate content detected.")
#             except Exception as e:
#                 st.error(e)
#     st.markdown('</div>', unsafe_allow_html=True)

# # ------------------ SDLC PLANNER ------------------
# st.markdown("<div id='sdlc-section'></div>", unsafe_allow_html=True)
# st.subheader("⚙️ End-to-End SDLC Project Planner")
# st.markdown("Get a complete project plan, from requirements to code, for your next idea.")
# with st.container():
#     st.markdown('<div class="card">', unsafe_allow_html=True)
#     project_idea = st.text_input("Enter your project idea:")
#     if st.button("Generate Project Plan"):
#         if project_idea:
#             try:
#                 plan = ai_module.plan_sdlc_project(model, project_idea)
#                 if is_safe(plan):
#                     st.success(plan)
#                 else:
#                     st.error("Inappropriate content detected.")
#             except Exception as e:
#                 st.error(e)
#     st.markdown('</div>', unsafe_allow_html=True)

# # ------------------ FEEDBACK ------------------
# st.markdown("<div id='feedback-section'></div>", unsafe_allow_html=True)
# st.subheader("💌 Provide Feedback")
# st.markdown("Help us improve the quality of the advice by providing your feedback.")
# with st.container():
#     st.markdown('<div class="card">', unsafe_allow_html=True)
#     with st.form("feedback_form"):
#         user_name = st.text_input("Your Name (Optional):")
#         feedback = st.text_area("Your Feedback:")
#         st.markdown("""
#         <div class="star-rating">
#             <input type="radio" id="star5" name="rating" value="5" /><label for="star5" title="5 stars">★</label>
#             <input type="radio" id="star4" name="rating" value="4" /><label for="star4" title="4 stars">★</label>
#             <input type="radio" id="star3" name="rating" value="3" /><label for="star3" title="3 stars">★</label>
#             <input type="radio" id="star2" name="rating" value="2" /><label for="star2" title="2 stars">★</label>
#             <input type="radio" id="star1" name="rating" value="1" /><label for="star1" title="1 star">★</label>
#         </div>
#         """, unsafe_allow_html=True)
#         submit_button = st.form_submit_button("Submit Feedback")
#         if submit_button:
#             if feedback:
#                 st.success("Thank you for your feedback!")
#                 st.write(f"Name: {user_name if user_name else 'Anonymous'}")
#                 st.write(f"Feedback: {feedback}")
#             else:
#                 st.warning("Please enter some feedback before submitting.")
#     st.markdown('</div>', unsafe_allow_html=True)
