import streamlit as st
import time
import base64
import random
import re

# --- Function to convert uploaded file to base64 for display ---
def get_base64_image(file_buffer):
    """Converts uploaded file buffer to base64 string for display in Markdown."""
    bytes_data = file_buffer.read()
    # Reset buffer position after reading to allow Streamlit to re-read later
    file_buffer.seek(0)
    base64_encoded = base64.b64encode(bytes_data).decode()
    return f"data:{file_buffer.type};base64,{base64_encoded}"

# --- NEW: Typo Correction and Conversational Handling ---
def clean_and_check_topic(topic):
    """Checks for common typos (like 'baisce') and suggests corrections in a friendly way."""
    original_topic = topic
    corrected_topic = topic

    # Basic substitution check (e.g., "baisce" -> "basics")
    if re.search(r'baisce|basice|basc', topic.lower()):
        # Replace the misspelled part with 'basics' in the original case (approx)
        corrected_topic = re.sub(r'baisce|basice|basc', 'basics', topic.lower())
        
    # Check if a correction was made and inform the user conversationally
    if original_topic.lower() != corrected_topic.lower():
        st.info(f"Hey! Mārga noticed you might mean **'{corrected_topic.title()}'**. We'll craft the path using that version, cool?")
    
    return corrected_topic.title()

# --- Placeholder Function for the Roadmap Generation (Includes all features) ---
def generate_roadmap(topic, level, duration_amount, duration_type, uploaded_files):
    
    # 1. NEW: Typo Check and Correction
    topic = clean_and_check_topic(topic)
    
    # Simulate AI processing time with friendly language
    st.markdown(f"**Mārga is on it!** Give me a sec to craft your hyper-personalized **{level}** roadmap for **'{topic}'** over the next **{duration_amount} {duration_type}**.")
    time.sleep(2) 

    # --- Feature 1: Visual Note Focus (Simulated Extraction) ---
    focus_terms = []
    topic_lower = topic.lower()
    if "chemistry" in topic_lower or "organic" in topic_lower:
        focus_terms = ["Functional Groups", "Ring Compounds", "Grignard Reagents"]
    elif "math" in topic_lower or "algebra" in topic_lower or "linear" in topic_lower:
        focus_terms = ["Determinants (2x2)", "Eigenvalues", "Least Squares"]
    elif "blockchain" in topic_lower or "basics" in topic_lower: # Added 'basics' after correction
        focus_terms = ["Hashing/Mining", "Decentralization", "Wallet Security"]
    elif "python" in topic_lower or "html" in topic_lower or "javascript" in topic_lower or "coding" in topic_lower:
        focus_terms = ["Core Syntax", "Data Structures", "Project Deployment"]
    elif "linux" in topic_lower or "command" in topic_lower:
        focus_terms = ["File Permissions (chmod)", "Network Config", "Grep Syntax"]
    else:
        focus_terms = [f"Core Concepts in {topic}", "Key Definitions", "Advanced Practice"]
        
    focus_box = ""
    if uploaded_files:
        focus_box = f"""
            <div style="background-color: #f0f0ff; padding: 15px; border-radius: 10px; border-left: 5px solid #6c5ce7; margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #6c5ce7;">🧠 Quick-Win Focus Box</h4>
                <p>Mārga peeked at your notes and suggests nailing these concepts first:</p>
                <ul>
                    <li>**{focus_terms[0]}** (The absolute foundation!)</li>
                    <li>**{focus_terms[1]}** (The essential skill to practice.)</li>
                    <li>**{focus_terms[2]}** (The challenging topic to save for later.)</li>
                </ul>
            </div>
        """

    # --- Feature 2: Mecrobet Insight (Updated for Conversational Tone) ---
    insights = [
        "Hey buddy, remember: True mastery is in understanding *why* things work, not just memorizing the steps.",
        "Your brain learns best when you're slightly challenged. If it feels too easy, level up the difficulty!",
        "Take a 5-minute break every hour. Your focus will thank you.",
        "To really own a concept, try teaching it to a rubber duck (or a friend!).",
        "**User Activity Tip (Simulated):** Your last session showed strong recall in {focus_terms[0]}! Let's focus on application this time."
    ]
    insight_text = random.choice(insights)

    # --- Feature 3: Display Visual Context ---
    visual_context_html = ""
    if uploaded_files:
        visual_context_html += "### 🖼️ Your Notes: Context is King\n"
        visual_context_html += '<div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">'
        
        for i, file in enumerate(uploaded_files):
            try:
                base64_img = get_base64_image(file)
                visual_context_html += f"""
                    <div style="width: 150px; text-align: center; border: 1px solid #ddd; padding: 5px; border-radius: 8px;">
                        <img src="{base64_img}" style="width: 100%; height: auto; border-radius: 4px; object-fit: cover;">
                        <small>Note {i+1}</small>
                    </div>
                """
            except Exception:
                visual_context_html += f"<p>Could not load image {i+1}.</p>"
        visual_context_html += "</div>"
        
    
    # --- Structured Roadmap Output (Updated for Conversational Tone) ---
    
    # Simple calculation for split duration
    half_duration = duration_amount // 2
    
    # Determine if Coding Activity is needed
    coding_activity = ""
    if "python" in topic_lower or "html" in topic_lower or "javascript" in topic_lower or "coding" in topic_lower:
        coding_activity = """
        * **Code Quiz Time!** Head over to your code sandbox (or just open a text editor) and write a short script to solve a simple problem, like printing "Hello, World!" in Python or creating a basic web button in HTML.
        """
    else:
        coding_activity = """
        * **Hands-on Lab:** Focus on practical assignments, simulations, or building a concept map to apply your knowledge (no code needed here!).
        """
        
    output = f"""
        <style>
            .stMarkdown h3 {{ color: #2e8b57; border-bottom: 2px solid #2e8b57; padding-bottom: 5px; }}
            .stMarkdown h4 {{ color: #3a537d; }}
        </style>
        
        ## 🗺️ Your Personalized Mārga (Roadmap)
        
        <p style="font-size: 1.1em; font-weight: 500;">
            **Topic:** {topic} | **Level:** {level} | **Goal:** <span style="color: #FF4B4B;">{duration_amount} {duration_type}</span>
        </p>
        
        ---
        
        {visual_context_html}
        
        {focus_box}
        
        ### 🚀 Your First Goal: The Basics (Approx. {half_duration} {duration_type})
        
        * **Hey buddy, let's start here!** This phase is all about building a rock-solid foundation.
        * **Day 1 Task:** Grab a blank page and map out **{focus_terms[0]}**. Don't look anything up yet! Then compare it to your notes.
        * **Core Study:** Spend the next **{half_duration} {duration_type}** focused on crushing **{focus_terms[1]}**. This is the most essential skill at your level.
        * **Weekly Quiz (Simulated):** Take a simulated 'Week 1 Quiz' on {focus_terms[0]}. **Mārga Note:** Other users who struggled here found success by drawing diagrams!
        
        ### 🛠️ Next Up: Build & Apply (Approx. {duration_amount - half_duration} {duration_type})
        
        * **Project Time!** You need to build something or solve complex problems. Complete 5 real-world simulations or assignments related to {topic}.
        {coding_activity}
        * **🎯 Community Vibe:** Find two other people studying {topic} on a forum. Post your progress or help someone stuck on a basic problem. This is how you really master it.
        
        ### 🌟 Final Checkpoint: Master Mode
        
        * **The Big Test:** Spend your last study session reviewing the hardest topic, **{focus_terms[2]}**, and explain it verbally without using your notes. If you can teach it, you know it!
        
        <div style="background-color: #e6ffe6; padding: 15px; border-radius: 10px; border: 1px solid #2e8b57; margin-top: 20px;">
            <h4 style="margin-top: 0; color: #2e8b57;'>💡 Mecrobet Insight</h4>
            <p>{insight_text}</p>
        </div>
        
        ---
        
        **✅ Let's do this!** Your first mission is the **Day 1 Task**. Go get 'em!
        """
    return output

# --- Streamlit Application Layout ---
st.set_page_config(page_title="Mecrobet Mārga (Conversational)", layout="wide")

st.title("Mecrobet Mārga: Your Personalized Learning Path 🗺️")
st.subheader("Your AI buddy for custom roadmaps, tips, and study plans.")

# --- INPUT COLUMNS (Layout for Topic and Duration) ---
col1, col2 = st.columns([2, 1])

with col1:
    # Set default to show typo correction immediately
    topic = st.text_input("📚 What subject do you want to master?", "blockchain baisce") 
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
st.caption("Mārga uses these visuals to make your path smarter. We will show them right on your roadmap!")
st.markdown("---")

# The button that triggers the generation
if st.button("Generate My Mārga (Roadmap)", type="primary"):
    if topic:
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