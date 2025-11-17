import streamlit as st
import time
import base64
import random
import re
import json
import requests
import os
from io import BytesIO

# --- Global Configuration ---
# API Key handling: Reads from Streamlit Secrets (GEMINI_API_KEY) or environment.
API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Using the standard gemini-2.5-flash-preview-09-2025 model for text and vision
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# --- Advanced Graphics CSS Injection ---
CUSTOM_CSS_INTERACTIVE = """
<style>
    /* Global Styles & Fonts */
    body { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4 { color: #4f46e5; }
    
    /* Core Roadmap Card Styles */
    .roadmap-step {
        background: #ffffff;
        border-radius: 12px;
        margin-bottom: 25px;
        overflow: hidden;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Unlocked/Active Step Styling */
    .unlocked-step {
        border: 1px solid #e0e7ff; /* Lighter indigo border */
        border-left: 6px solid #4f46e5; /* Primary color indicator */
    }
    .unlocked-step:hover {
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.15);
        transform: translateY(-2px);
    }
    
    /* Locked Step Styling */
    .locked-step {
        background: #fcfcfc;
        border: 1px dashed #d1d5db;
        border-left: 6px solid #9ca3af; /* Gray lock indicator */
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .step-header {
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #f9f9ff; /* Very light purple tint */
        border-bottom: 1px solid #eef;
    }

    .step-content {
        padding: 20px;
    }

    /* Icons */
    .lock-icon {
        color: #9ca3af;
        font-size: 28px;
        margin-right: 15px;
    }
    .unlock-icon {
        color: #10b981;
        font-size: 28px;
        margin-right: 15px;
    }
</style>
"""

# --- Utility Functions ---

def get_base64_image(file_buffer):
    """Converts uploaded file buffer to base64 string for display and API use."""
    bytes_data = file_buffer.read()
    file_buffer.seek(0)
    base64_encoded = base64.b64encode(bytes_data).decode()
    return base64_encoded, file_buffer.type

def call_gemini_api_with_retry(payload, max_retries=3):
    """Handles API call with exponential backoff for robustness."""
    if not API_KEY:
         # Simplified error for deployment context
         return "Error: API Key is missing. Please ensure GEMINI_API_KEY is set in Streamlit Secrets."
         
    for attempt in range(max_retries):
        try:
            headers = {'Content-Type': 'application/json'}
            # Note: We append the API_KEY here
            response = requests.post(f"{GEMINI_API_URL}?key={API_KEY}", headers=headers, data=json.dumps(payload))
            response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
            
            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            if candidate and candidate.get('content', {}).get('parts', [{}])[0].get('text'):
                return candidate['content']['parts'][0]['text']
            else:
                return "Error: LLM returned an empty or unexpected response structure."

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                time.sleep(sleep_time)
            else:
                return f"Error: Failed to connect to LLM after {max_retries} attempts. (Details: {e}). Did you set the API Key secret?"
        except Exception as e:
            return f"Error: An unexpected error occurred during API processing: {e}"
    return "Error: Unknown failure during API interaction."

def parse_markdown_roadmap(markdown_text):
    """Parses the LLM's Markdown output into a list of structured steps."""
    
    # Regex to split the text by '## Day X' or '## Week X' headings
    steps = re.split(r'(## (Day|Week) \d+.*)', markdown_text, flags=re.IGNORECASE)
    
    parsed_steps = []
    
    # steps will look like: ['', '## Day 1 Title', 'Content 1', '## Day 2 Title', 'Content 2', ...]
    
    # Skip the first element and iterate over pairs (title, content)
    for i in range(1, len(steps), 2):
        if i + 1 < len(steps):
            title = steps[i].strip()
            content = steps[i+1].strip()
            
            clean_title = title.replace('## ', '', 1).strip()
            
            parsed_steps.append({
                "title": clean_title,
                "content_markdown": content.strip()
            })
            
    return parsed_steps

def generate_styled_html_download(topic, level, duration_amount, duration_type, roadmap_markdown, insight_text):
    """Generates a complete, standalone HTML file with embedded CSS for download."""
    
    # Simple conversion of basic markdown to HTML for presentation
    html_content = roadmap_markdown.replace('## ', '<h2>').replace('### ', '<h3>')
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
    
    # Replace markdown list items
    html_content = html_content.replace('\n- ', '\n<li>')
    # Simple list wrapper
    if '<li>' in html_content:
        html_content = '<ul>' + html_content.replace('<li>', '</li><li>') + '</ul>'
        html_content = html_content.replace('<ul></li>', '<ul>') # fix leading empty li
        html_content = html_content.replace('</ul>\n', '</ul>').replace('</ul>\n\n', '</ul>')

    
    # Custom CSS to mimic the app's look
    custom_css = """
        body { font-family: sans-serif; line-height: 1.6; margin: 20px; color: #333; }
        h1 { color: #4f46e5; border-bottom: 5px solid #4f46e5; padding-bottom: 10px; }
        h2 { color: #4f46e5; border-bottom: 3px solid #4f46e5; padding-bottom: 8px; margin-top: 25px; }
        h3 { color: #10b981; margin-top: 20px; }
        .roadmap-card { 
            background: linear-gradient(145deg, #f9f9f9, #ffffff);
            border: 1px solid #e0e0e0; 
            border-radius: 16px; 
            padding: 30px; 
            box-shadow: 0 10px 20px rgba(0,0,0,0.1); 
            margin-top: 15px; 
        }
        .insight-box { 
            background-color: #f0f0ff; 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 5px solid #6c5ce7; 
            margin-bottom: 20px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .roadmap-card h2 {
            color: #e94e77; 
            border-bottom: 2px dashed #e94e7750;
            padding-bottom: 5px;
        }
        ul { padding-left: 20px; }
        li { margin-bottom: 10px; }
    """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mārga Roadmap: {topic}</title>
        <style>{custom_css}</style>
    </head>
    <body>
        <h1>🗺️ Personalized Mārga (Roadmap)</h1>
        <p style="font-size: 1.1em; font-weight: 500;">
            <b>Topic:</b> {topic} | <b>Level:</b> {level} | <b>Goal Duration:</b> <span style="color: #FF4B4B;">{duration_amount} {duration_type}</span>
        </p>
        <hr>
        
        <div class="insight-box">
            <h4 style="margin-top: 0; color: #6c5ce7;">💡 Mārga's Insight for You</h4>
            <p>{insight_text}</p>
        </div>
        
        <h3>📝 The Full Study Plan (Confidence: 95%+ Accuracy)</h3>
        <div class="roadmap-card">
            {html_content}
        </div>
        
        <br><br>
        <p><small>Generated by Mecrobet Mārga on {time.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
    </body>
    </html>
    """
    return html_template

# --- Core LLM Generation Functions (Roadmap) ---

def call_gemini_api_for_roadmap(topic, level, duration_amount, duration_type, file_parts):
    """Generates the main structured roadmap content for the full duration."""
    
    # 1. New System Persona: More human, friendly, and focused on structure
    system_prompt = (
        "Act as Mārga, a highly engaging and personalized AI tutor. You talk like a friendly human mentor—use contractions, encouraging language, and an informal but knowledgeable tone. "
        "Your primary job is to generate a comprehensive, structured study roadmap in MARKDOWN for the full time period requested. "
        "The plan MUST be broken down into 'Day X' or 'Week X' steps, covering the entire duration: "
        f"{duration_amount} {duration_type}. "
        "The output must focus on practical application and MUST be structured using Markdown headings (## Day X or ## Week X). "
        "The content accuracy must be 95%+ using search grounding."
    )
    
    # 2. Define the User Query
    user_query = (
        f"Generate a personalized {level} study roadmap for the topic: '{topic}'. "
        f"The plan must span the entire period of {duration_amount} {duration_type}. "
        "Structure the output clearly by day or week. If images are provided, tailor the roadmap to focus on the key concepts visible in the notes."
    )
    
    # 3. Construct the Full Payload
    payload = {
        "contents": [{ "parts": file_parts + [{ "text": user_query }] }],
        "systemInstruction": { "parts": [{ "text": system_prompt }] },
        "tools": [{ "google_search": {} }]
    }
    
    return call_gemini_api_with_retry(payload)

def handle_completion(index):
    """Callback function to handle marking a step as complete."""
    # Check if the step before it is complete (or if it's the first step)
    if index == 0 or st.session_state.progress[index - 1]:
        st.session_state.progress[index] = True
        # REMOVED st.experimental_rerun()
    else:
        # Should not happen via button click but as a safeguard
        st.error("Please complete the previous step first!")

def display_interactive_roadmap(topic, level, duration_amount, duration_type, uploaded_files):
    
    # Inject advanced interactive CSS
    st.markdown(CUSTOM_CSS_INTERACTIVE, unsafe_allow_html=True)
    
    # Ensure progress state is initialized or reset if the roadmap structure changes
    if 'progress' not in st.session_state or len(st.session_state.progress) != len(st.session_state.structured_roadmap):
        st.session_state.progress = [False] * len(st.session_state.structured_roadmap)

    
    # Display steps
    for i, step in enumerate(st.session_state.structured_roadmap):
        
        # Logic for Locking/Unlocking
        is_completed = st.session_state.progress[i]
        is_unlocked = i == 0 or st.session_state.progress[i-1]
        
        
        if not is_unlocked and not is_completed:
            # LOCKED STATE
            st.markdown(f"""
                <div class="roadmap-step locked-step">
                    <div class="step-header">
                        <div style="display: flex; align-items: center;">
                            <span class="lock-icon">🔒</span>
                            <h3 style="margin: 0; color: #9ca3af; font-weight: 600;">{step['title']} (Locked)</h3>
                        </div>
                        <span class="text-sm text-gray-500">Complete the previous step to unlock.</span>
                    </div>
                    <div class="step-content">
                        <p class="text-gray-400">Content hidden until previous stage is mastered. Keep going!</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            # UNLOCKED OR COMPLETED STATE
            card_class = "unlocked-step"
            
            # Using st.expander allows us to show/hide content without complex reruns
            with st.expander(f"**{step['title']}** " + ("✅" if is_completed else "💡"), expanded=not is_completed):

                st.markdown(step['content_markdown'])
                
                # Status/Button
                if is_completed:
                    st.success("Completed!")
                else:
                    st.button(
                        f"Mark Complete & Unlock Next", 
                        key=f"complete_btn_{i}", 
                        on_click=handle_completion, 
                        args=(i,),
                        type="primary",
                        use_container_width=False # Use false to prevent width issues in the expander
                    )

                
    # --- Download Button (outside the loop) ---
    roadmap_filename = f"Marga_Roadmap_{topic.replace(' ', '_')}_{duration_amount}{duration_type}.html"
    download_content = generate_styled_html_download(
        topic, 
        level, 
        duration_amount, 
        duration_type, 
        st.session_state.current_roadmap_text,
        st.session_state.current_insight
    )
    
    st.download_button(
        label="⬇️ Download Full Roadmap (Styled HTML - Print to PDF)",
        data=download_content.encode('utf-8'),
        file_name=roadmap_filename,
        mime="text/html",
        key="download_roadmap_main" 
    )
    st.caption("Tip: Open the downloaded HTML file in your browser, then use 'Print' > 'Save as PDF' for a professional document.")


def generate_roadmap_content(topic, level, duration_amount, duration_type, uploaded_files):
    
    st.session_state.topic = topic # Save topic for assignment feature
    st.session_state.has_generated = False # Set flag before generation
    
    # Prepare files for the LLM call
    file_parts = []
    visual_context_html = ""
    
    if uploaded_files:
        visual_context_html += "### 🖼️ Your Contextual Notes\n"
        visual_context_html += '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">'
        
        for i, file_buffer in enumerate(uploaded_files):
            try:
                base64_data, mime_type = get_base64_image(file_buffer)
                file_parts.append({
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": base64_data
                    }
                })

                visual_context_html += f"""
                    <div style="width: 150px; text-align: center; border: 1px solid #ddd; padding: 5px; border-radius: 8px;">
                        <img src="data:{mime_type};base64,{base64_data}" style="width: 100%; height: auto; border-radius: 4px; object-fit: cover;">
                        <small>Note {i+1}</small>
                    </div>
                """
            except Exception as e:
                st.warning(f"Could not process uploaded file {file_buffer.name}. Error: {e}")
                
        visual_context_html += "</div>"
    
    
    with st.spinner(f"Mārga is crafting your detailed {duration_amount} {duration_type} roadmap... this might take 10-20 seconds!"):
        roadmap_markdown = call_gemini_api_for_roadmap(
            topic, 
            level, 
            duration_amount, 
            duration_type, 
            file_parts
        )
        
        # Check for API error
        if roadmap_markdown.startswith("Error:"):
            st.error(roadmap_markdown)
            return

        # Store the raw markdown for download
        st.session_state.current_roadmap_text = roadmap_markdown
        st.session_state.structured_roadmap = parse_markdown_roadmap(roadmap_markdown) # <-- NEW LINE: Parse and store structure

    # Conversational Insight
    insights = [
        "You've got this! Remember: True mastery comes from consistent effort, not last-minute cramming.",
        "Your brain needs breaks! Try the Pomodoro technique—25 minutes focus, 5 minutes rest.",
        "To really own a concept, try teaching it to someone else (or even just your reflection!).",
        "Don't worry about perfection, just focus on making a little progress every day.",
    ]
    insight_text = random.choice(insights)
    st.session_state.current_insight = insight_text # Store insight for HTML download
    st.session_state.has_generated = True # Set flag after successful generation
    
    # Now that generation is complete, the rest of the function just sets up the visual components
    st.markdown(f"""
        <h2>🗺️ Your Personalized Mārga (Roadmap)</h2>
        
        <p style="font-size: 1.1em; font-weight: 500;">
            <b>Topic:</b> {topic} | <b>Level:</b> {level} | <b>Goal Duration:</b> <span style="color: #FF4B4B;">{duration_amount} {duration_type}</span>
        </p>
        
        <hr>
        
        {visual_context_html}
        
        <div class="insight-box" style="background-color: #f0f0ff; padding: 15px; border-radius: 10px; border-left: 5px solid #6c5ce7; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h4 style="margin-top: 0; color: #6c5ce7;">💡 Mārga's Insight for You</h4>
            <p>{insight_text}</p>
        </div>
        
        <h3>📝 The Full Study Plan (Interactive View)</h3>
        """, unsafe_allow_html=True)


    st.markdown(f"""
        <hr>
        <p style="font-weight: bold; font-size: 1.1em;">
            🎉 Awesome! Now head over to the **'Assignment Hub'** tab to generate your first checkpoint assignment!
        </p>
    """, unsafe_allow_html=True)


# --- Core LLM Generation Functions (Assignment Hub) ---

def call_gemini_api_for_assignment(topic):
    """Generates an assignment based on the current topic."""
    
    system_prompt = (
        "You are Mārga, the friendly AI tutor. Your task is to generate a comprehensive, multi-part, and challenging assignment "
        "that tests the user's understanding of the provided topic. "
        "The assignment MUST include a mix of question types: 1-2 definition/theory questions and 1 practical/scenario-based problem. "
        "Do NOT include the answer key. Keep the tone friendly and encouraging."
        "Structure the output in clean Markdown under a single '## Assignment: [Topic]' heading."
    )
    
    user_query = f"Generate a checkpoint assignment for the topic: {topic}."
    
    payload = {
        "contents": [{ "parts": [{ "text": user_query }] }],
        "systemInstruction": { "parts": [{ "text": system_prompt }] },
        "tools": [{ "google_search": {} }]
    }
    
    return call_gemini_api_with_retry(payload)

def call_gemini_api_for_grading(topic, submitted_notes_parts):
    """Grades the user's uploaded assignment solution."""
    
    system_prompt = (
        "You are Mārga, the expert AI grader. Your tone is supportive, encouraging, and highly analytical. "
        "Your task is to analyze the user's uploaded image/notes, which contain their solution to an assignment on the topic. "
        "Provide a structured, three-part response in MARKDOWN:"
        "1. **Overall Feedback:** A human-like assessment of their effort and understanding."
        "2. **Key Points Correct (Answer Key):** List the main concepts they got right or should have included."
        "3. **Areas for Improvement (Mistake Pointer):** Detail 1-2 specific, actionable mistakes or gaps in their knowledge demonstrated in the image."
        "Do not use numerical grades, focus on qualitative feedback."
    )
    
    user_query = f"The user has submitted their handwritten solution (in the attached image/notes) for an assignment on '{topic}'. Please analyze the image and provide comprehensive feedback based on the three-part structure defined in your system instruction."
    
    # Combine image parts (the submission) and the text query
    payload = {
        "contents": [{ "parts": submitted_notes_parts + [{ "text": user_query }] }],
        "systemInstruction": { "parts": [{ "text": system_prompt }] },
        "tools": [{ "google_search": {} }]
    }
    
    return call_gemini_api_with_retry(payload)

# --- Streamlit Page Functions ---

def roadmap_generator_page():
    """Defines the layout and logic for the Roadmap Generation Tab."""
    
    st.subheader("Craft Your Learning Path with Mārga 🧭")

    col1, col2 = st.columns([2, 1])

    with col1:
        topic = st.text_input("📚 1. What subject or concept are you mastering?", 
                              st.session_state.get('topic', 'Data Science Basics'),
                              key="roadmap_topic_input") # UNIQUE KEY
        level = st.select_slider("🎯 3. Your Current Level:", 
                                 options=['Beginner', 'Intermediate', 'Advanced'], 
                                 value='Intermediate',
                                 key="roadmap_level_slider") # UNIQUE KEY
        
    with col2:
        st.markdown("⏳ **2. Goal Duration**")
        duration_amount = st.number_input("Amount", min_value=1, value=5, key="duration_amount_input") # UNIQUE KEY
        duration_type = st.selectbox("Type", ["Days", "Weeks", "Months"], key="duration_type_select") # UNIQUE KEY
        
        if duration_amount == 1 and duration_type in ["Days", "Weeks", "Months"]:
             st.warning("For a multi-day plan, consider 3+ Days or 1+ Week.")

    st.markdown("---")
    uploaded_files = st.file_uploader(
        "Upload your current notes or images for contextual learning (Optional):", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        key="roadmap_uploader" # UNIQUE KEY
    )
    st.caption("Mārga uses these visuals to tailor the plan specifically to your existing knowledge.")
    st.markdown("---")

    if st.button("Generate My Mārga (Roadmap)", type="primary", use_container_width=True, key="generate_roadmap_button"): # UNIQUE KEY
        if topic:
            # We call the generation function here, which sets st.session_state.has_generated = True
            generate_roadmap_content(topic, level, duration_amount, duration_type, uploaded_files)
        else:
            st.error("Hold up! Please enter a subject to start your path!")

    # Display interactive roadmap if it has been generated successfully
    if st.session_state.get('has_generated') and 'structured_roadmap' in st.session_state and st.session_state.structured_roadmap:
        display_interactive_roadmap(topic, level, duration_amount, duration_type, uploaded_files)


def assignment_hub_page():
    """Defines the layout and logic for the Assignment and Grading Tab."""
    
    current_topic = st.session_state.get('topic', 'No Topic Set (e.g., Data Science Basics)')
    
    st.markdown(f"""
        <h2 style="color: #4f46e5;">📝 Assignment Hub: Checkpoint for {current_topic}</h2>
        <p>Mārga suggests a check-in assignment roughly every 5 days of study to lock in what you've learned. </p>
    """, unsafe_allow_html=True)
    
    # --- Generate Assignment Section ---
    st.markdown("### 1. Generate Your Assignment")
    
    if st.button(f"Generate Checkpoint Assignment for '{current_topic}'", type="secondary", key="generate_assignment_button_hub"): # UNIQUE KEY
        with st.spinner("Mārga is designing your custom challenge..."):
            assignment_text = call_gemini_api_for_assignment(current_topic)
            st.session_state.last_assignment = assignment_text # Store for display
            
    if 'last_assignment' in st.session_state:
        st.markdown(st.session_state.last_assignment)
    
    st.markdown("---")
    
    # --- Submit and Grade Section ---
    st.markdown("### 2. Submit Your Solution & Get Feedback")
    
    submission_file = st.file_uploader(
        "Upload your handwritten or typed assignment solution (as a PNG/JPG image):", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=False,
        key="submission_file_uploader" # UNIQUE KEY
    )
    
    # Use a flag to track if the grade button was pressed AND a file exists
    grade_button_clicked = st.button("Get My Grade & Feedback", type="primary", key="grade_feedback_button_main")
    
    if grade_button_clicked and submission_file: 
        
        submitted_notes_parts = []
        try:
            base64_data, mime_type = get_base64_image(submission_file)
            submitted_notes_parts.append({
                "inlineData": {
                    "mimeType": mime_type,
                    "data": base64_data
                }
            })
        except Exception as e:
            st.error(f"Could not process submission file. Error: {e}")
            return
            
        with st.spinner("Mārga is analyzing your submission and pointing out those key learning areas..."):
            feedback_markdown = call_gemini_api_for_grading(current_topic, submitted_notes_parts)
            st.session_state.last_feedback = feedback_markdown

        # Display Feedback
        st.markdown("### 🌟 Mārga's Personalized Feedback 🌟")
        st.markdown(feedback_markdown)
        st.success("Great work! Use the 'Areas for Improvement' to refine your study plan.")
        
        # --- Download Button for Feedback (After successful grading) ---
        feedback_filename = f"Marga_Feedback_{current_topic.replace(' ', '_')}_GRADE.md"
        download_content = f"# Mecrobet Mārga Assignment Feedback: {current_topic}\n\n---\n\n{feedback_markdown}"
        st.download_button(
            label="⬇️ Download Feedback (Markdown File)",
            data=download_content.encode('utf-8'),
            file_name=feedback_filename,
            mime="text/markdown",
            key="download_feedback_post_grade" # UNIQUE KEY
        )
        
    elif grade_button_clicked and not submission_file:
         st.warning("Please upload your solution file first before requesting feedback!")
        
    elif 'last_feedback' in st.session_state:
        # This section is for displaying previously generated feedback
        st.markdown("### 🌟 Mārga's Personalized Feedback 🌟")
        st.markdown(st.session_state.last_feedback)
         # --- Download Button for Feedback (Re-display) ---
        feedback_filename = f"Marga_Feedback_{current_topic.replace(' ', '_')}_RELOAD.md"
        download_content = f"# Mecrobet Mārga Assignment Feedback: {current_topic}\n\n---\n\n{st.session_state.last_feedback}"
        st.download_button(
            label="⬇️ Download Feedback (Markdown File)",
            data=download_content.encode('utf-8'),
            file_name=feedback_filename,
            mime="text/markdown",
            key="download_feedback_reloaded" # UNIQUE KEY
        )
        

# --- Main App Execution ---

# Initialize necessary session state variables
if 'topic' not in st.session_state:
    st.session_state['topic'] = 'Data Science Basics'

if 'current_insight' not in st.session_state:
    st.session_state['current_insight'] = 'No insight yet.'
    
if 'current_roadmap_text' not in st.session_state:
    st.session_state['current_roadmap_text'] = ''
    
# Flag to control if the roadmap display should be active
if 'has_generated' not in st.session_state:
    st.session_state['has_generated'] = False

# The interactive state variable 'structured_roadmap' will be initialized in generate_roadmap_content

st.set_page_config(page_title="Mecrobet Mārga: Personalized Learning", layout="wide")

st.title("Mecrobet Mārga: Your Personalized Learning Path 🗺️")
st.subheader("Your friendly AI mentor for structured study, human-like feedback, and 95%+ content accuracy.")

# Create the tab navigation
tab_roadmap, tab_assignments = st.tabs(["🗺️ Roadmap Generator", "📝 Assignment Hub"])

with tab_roadmap:
    roadmap_generator_page()

with tab_assignments:
    assignment_hub_page()

st.markdown("---")
st.caption("Powered by the Mecrobet Mārga Team. Final Streamlit Version.")