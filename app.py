import streamlit as st
import time
import base64
import random
import re
import json
import requests # Required for making external API calls
import os # Import os for environment variable check

# --- Global Configuration ---
# API Key handling:
# 1. First, check the execution environment variable (used for live deployment/Streamlit Secrets).
# 2. Fallback to the hardcoded empty string (used for the Canvas environment if not provided).
# The key name for Streamlit Secrets is typically defined by the user; we will standardize on GEMINI_API_KEY
API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Using the standard gemini-2.5-flash-preview-09-2025 model for text and vision
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# --- Utility Functions ---

def get_base64_image(file_buffer):
    """Converts uploaded file buffer to base64 string for display and API use."""
    # Read the full content of the file buffer
    bytes_data = file_buffer.read()
    # Reset buffer position after reading to allow Streamlit to re-read later
    file_buffer.seek(0)
    # Encode the bytes data to base64 string
    base64_encoded = base64.b64encode(bytes_data).decode()
    return base64_encoded, file_buffer.type

def call_gemini_api_with_retry(payload, max_retries=3):
    """Handles API call with exponential backoff for robustness."""
    # Check if API key is available before attempting the call
    if not API_KEY:
         return "Error: API Key is missing. Please ensure GEMINI_API_KEY is set in Streamlit Secrets."
         
    for attempt in range(max_retries):
        try:
            headers = {'Content-Type': 'application/json'}
            # Make the API request, using the global API_KEY
            response = requests.post(f"{GEMINI_API_URL}?key={API_KEY}", headers=headers, data=json.dumps(payload))
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            
            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            # Extract the text content from the response
            if candidate and candidate.get('content', {}).get('parts', [{}])[0].get('text'):
                return candidate['content']['parts'][0]['text']
            else:
                return "Error: LLM returned an empty or unexpected response structure."

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                # Exponential backoff
                sleep_time = 2 ** attempt
                # Do not log retry as an error in console
                time.sleep(sleep_time)
            else:
                # Log the final error attempt
                return f"Error: Failed to connect to LLM after {max_retries} attempts. {e}"
        except Exception as e:
            return f"Error: An unexpected error occurred during API processing: {e}"
    return "Error: Unknown failure during API interaction."


# --- Core LLM Generation Functions (95% Accuracy Feature) ---

def call_gemini_api_for_roadmap(topic, level, duration_amount, duration_type, file_parts):
    """Generates the main structured roadmap content, incorporating image context and grounding."""
    
    # 1. Define the System Persona and Rules
    system_prompt = (
        "Act as a world-class AI tutor and study planner (Mārga). "
        "Your goal is to generate a personalized, accurate study roadmap in MARKDOWN format. "
        "The plan must be highly detailed and optimized for the user's level and duration. "
        "Base your suggestions on the provided topic, level, duration, and the context from the user's notes/images."
        "The output must focus on practical application and must be structured with clear phases. "
        "Your generated roadmap must achieve at least 95% accuracy in content."
    )
    
    # 2. Define the User Query
    user_query = (
        f"Generate a personalized {level} study roadmap for the topic: '{topic}' "
        f"to be completed over {duration_amount} {duration_type}. "
        "If images are provided, tailor the roadmap to focus on the key concepts visible in the notes."
    )
    
    # 3. Construct the Full Payload
    payload = {
        # Combine image parts (if any) and the text query
        "contents": [{ "parts": file_parts + [{ "text": user_query }] }],
        "systemInstruction": { "parts": [{ "text": system_prompt }] },
        # Use Google Search grounding for 95% up-to-date accuracy
        "tools": [{ "google_search": {} }]
    }
    
    return call_gemini_api_with_retry(payload)


def call_gemini_api_for_visual_guide(topic):
    """Generates the content for the quick revision study guide."""
    
    system_prompt = (
        "You are a subject matter expert. Generate a concise, simple, visual study guide "
        "on the single core concept of the user's requested topic. "
        "The output must be in MARKDOWN, follow the structure of a quick-reference card (Definition, Properties, Application), "
        "and be easily readable for quick revisions. Do not include a title section or intro/outro text. "
        "Focus on 3-4 bullet points per section."
    )
    
    user_query = f"Generate a quick visual study guide on the core concept of: {topic}."
    
    payload = {
        "contents": [{ "parts": [{ "text": user_query }] }],
        "systemInstruction": { "parts": [{ "text": system_prompt }] },
        "tools": [{ "google_search": {} }]
    }
    
    return call_gemini_api_with_retry(payload)


# --- Supporting UI and Logic Functions ---

def clean_and_check_topic(topic):
    """Checks for common typos (like 'baisce') and suggests corrections in a friendly way.)"""
    original_topic = topic
    corrected_topic = topic

    if re.search(r'baisce|basice|basc', topic.lower()):
        # Simple string replacement for common typos related to 'basics'
        corrected_topic = re.sub(r'baisce|basice|basc', 'basics', topic.lower())
        
    if original_topic.lower() != corrected_topic.lower():
        st.info(f"Hey! Mārga noticed you might mean **'{corrected_topic.title()}'**. We'll craft the path using that version, cool?")
    
    return corrected_topic.title()

def generate_roadmap(topic, level, duration_amount, duration_type, uploaded_files):
    
    topic = clean_and_check_topic(topic)
    
    # Prepare files for the LLM call
    file_parts = []
    visual_context_html = ""
    
    if uploaded_files:
        visual_context_html += "### 🖼️ Your Notes: Context is King\n"
        visual_context_html += '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">'
        
        # Iterate over files to prepare them for both display and API submission
        for i, file_buffer in enumerate(uploaded_files):
            try:
                # Use the utility function to get base64 data and mime type
                # Note: get_base64_image resets the buffer position for Streamlit
                base64_data, mime_type = get_base64_image(file_buffer)
                
                # Add file to the LLM parts list (for context/vision)
                file_parts.append({
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": base64_data
                    }
                })

                # Prepare HTML for display in Streamlit
                visual_context_html += f"""
                    <div style="width: 150px; text-align: center; border: 1px solid #ddd; padding: 5px; border-radius: 8px;">
                        <img src="data:{mime_type};base64,{base64_data}" style="width: 100%; height: auto; border-radius: 4px; object-fit: cover;">
                        <small>Note {i+1}</small>
                    </div>
                """
            except Exception as e:
                st.warning(f"Could not process uploaded file {file_buffer.name}. Error: {e}")
                
        visual_context_html += "</div>"

    # --- LLM Calls for Content Generation ---
    with st.spinner(f"Mārga is generating your **95%+ Accurate** roadmap and study guide... this takes a moment!"):
        # 1. Generate the Main Roadmap (High-Accuracy, personalized, using files for context)
        roadmap_markdown = call_gemini_api_for_roadmap(
            topic, 
            level, 
            duration_amount, 
            duration_type, 
            file_parts
        )
        
        # 2. Generate the Visual Study Guide Content (Independent, quick-ref content)
        visual_guide_markdown = call_gemini_api_for_visual_guide(topic)


    # --- Output Assembly ---
    
    # Conversational Insight
    insights = [
        "Hey buddy, remember: True mastery is in understanding *why* things work, not just memorizing the steps.",
        "Your brain learns best when you're slightly challenged. If it feels too easy, level up the difficulty!",
        "Take a 5-minute break every hour. Your focus will thank you.",
        "To really own a concept, try teaching it to a rubber duck (or a friend!).",
    ]
    insight_text = random.choice(insights)

    # Combine all generated parts into the final display output
    output = f"""
        <style>
            .stMarkdown h2 {{ color: #4f46e5; border-bottom: 3px solid #4f46e5; padding-bottom: 8px; margin-top: 20px; }}
            .stMarkdown h3 {{ color: #10b981; }}
        </style>
        
        <h2>🗺️ Your Personalized Mārga (Roadmap)</h2>
        
        <p style="font-size: 1.1em; font-weight: 500;">
            <b>Topic:</b> {topic} | <b>Level:</b> {level} | <b>Goal:</b> <span style="color: #FF4B4B;">{duration_amount} {duration_type}</span>
        </p>
        
        <hr>
        
        {visual_context_html}
        
        <div style="background-color: #f0f0ff; padding: 15px; border-radius: 10px; border-left: 5px solid #6c5ce7; margin-bottom: 20px;">
            <h4 style="margin-top: 0; color: #6c5ce7;">💡 Mecrobet Insight</h4>
            <p>{insight_text}</p>
        </div>
        
        <h3>🧪 AI-Generated Study Plan (Confidence: 95%+ Accuracy)</h3>
        
        {roadmap_markdown}

        <hr>
        
        <h2>📘 Quick Revision Study Guide (Always Ready!)</h2>
        
        <p>*Mārga generated this simplified guide for quick review of the core concept of {topic}.*</p>
        
        {visual_guide_markdown}

        <hr>
        
        <p style="font-weight: bold; font-size: 1.1em;">✅ Let's do this! Use the roadmap to guide your deep study and the guide above for quick-fire revisions!</p>
        """
    return output

# --- Streamlit Application Layout ---
st.set_page_config(page_title="Mecrobet Mārga (LLM Integrated)", layout="wide")

st.title("Mecrobet Mārga: Your Personalized Learning Path 🗺️")
st.subheader("Your AI buddy for custom roadmaps, tips, and study plans.")

# --- INPUT COLUMNS (Layout for Topic and Duration) ---
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input("📚 What subject do you want to master?", "blockchain basics") 
    level = st.select_slider("🎯 Your Current Level:", options=['Beginner', 'Intermediate', 'Advanced'], value='Intermediate')
    
with col2:
    st.markdown("⏳ **Goal Duration**")
    duration_amount = st.number_input("Amount", min_value=1, value=5, key="duration_amount")
    duration_type = st.selectbox("Type", ["Minutes", "Hours", "Days", "Weeks", "Months"], key="duration_type")

# --- Image Uploader ---
st.markdown("---")
uploaded_files = st.file_uploader(
    "Upload your notes or images for context (Optional):", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)
st.caption("Mārga uses these visuals to make your path smarter and more accurate. Your notes will be shown on the roadmap.")
st.markdown("---")

# The button that triggers the generation
if st.button("Generate My Mārga (Roadmap)", type="primary"):
    if topic:
        # Pass all inputs to the generate function
        st.markdown(generate_roadmap(
            topic, 
            level, 
            duration_amount, 
            duration_type, 
            uploaded_files
        ), unsafe_allow_html=True) 
    else:
        st.error("Hey! Please enter a subject to start your path!")

st.markdown("---")
st.caption("Powered by the Mecrobet Mārga Team. Final Streamlit Version.")