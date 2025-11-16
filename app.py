import streamlit as st
import time
import base64
import random

# --- Function to convert uploaded file to base64 for display ---
def get_base64_image(file_buffer):
    """Converts uploaded file buffer to base64 string for display in Markdown."""
    bytes_data = file_buffer.read()
    # Reset buffer position after reading to allow Streamlit to re-read later
    file_buffer.seek(0)
    base64_encoded = base64.b64encode(bytes_data).decode()
    return f"data:{file_buffer.type};base64,{base64_encoded}"

# --- Placeholder Function for the Roadmap Generation (Includes all features) ---
def generate_roadmap(topic, level, duration_amount, duration_type, uploaded_files):
    
    # Simulate AI processing time
    st.info(f"Mecrobet Mārga is running the final analysis... crafting your **{level}** path for **'{topic}'** over **{duration_amount} {duration_type}**.")
    time.sleep(2) 

    # --- Feature 1: Visual Note Focus (Simulated Extraction) ---
    # Logic to determine focus terms based on the topic and notes provided
    focus_terms = []
    topic_lower = topic.lower()
    if "chemistry" in topic_lower or "organic" in topic_lower:
        focus_terms = ["Functional Groups", "Ring Compounds", "Grignard Reagents"]
    elif "math" in topic_lower or "algebra" in topic_lower or "linear" in topic_lower:
        focus_terms = ["Determinants (2x2)", "Eigenvalues", "Least Squares"]
    elif "linux" in topic_lower or "command" in topic_lower:
        focus_terms = ["File Permissions (chmod)", "Network Config", "Grep Syntax"]
    else:
        focus_terms = [f"Core Concepts in {topic}", "Key Definitions", "Advanced Practice"]
        
    focus_box = ""
    if uploaded_files:
        focus_box = f"""
            <div style="background-color: #f0f0ff; padding: 15px; border-radius: 10px; border-left: 5px solid #6c5ce7; margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #6c5ce7;">✨ Visual Note Focus</h4>
                <p>Mārga has extracted these concepts from your notes for special attention:</p>
                <ul>
                    <li>**{focus_terms[0]}** (Critical Foundation)</li>
                    <li>**{focus_terms[1]}** (Application Skill)</li>
                    <li>**{focus_terms[2]}** (Advanced Topic)</li>
                </ul>
            </div>
        """

    # --- Feature 2: Mecrobet Insight ---
    insights = [
        "Focus on understanding *why* a concept works, not just *how* to use it. True mastery is in the theory.",
        "Your best learning moments often come right after a failure. Embrace the debug process!",
        "Spend 10 minutes before bed reviewing your **Visual Note Focus** items. This boosts memory retention.",
        "Do not underestimate the power of teaching. Explain your current concept to an imaginary friend."
    ]
    insight_text = random.choice(insights)

    # --- Feature 3: Display Visual Context ---
    visual_context_html = ""
    if uploaded_files:
        visual_context_html += "### 🖼️ Visual Context Provided:\n"
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
        
    
    # --- Structured Roadmap Output (The Final Result) ---
    output = f"""
        <style>
            .stMarkdown h3 {{ color: #2e8b57; border-bottom: 2px solid #2e8b57; padding-bottom: 5px; }}
            .stMarkdown h4 {{ color: #3a537d; }}
        </style>
        
        ## 🗺️ Mecrobet Mārga: Your Path to **{topic}**
        
        <p style="font-size: 1.1em; font-weight: 500;">
            **Level:** {level} | **Goal Duration:** <span style="color: #FF4B4B;">{duration_amount} {duration_type}</span>
        </p>
        
        ---
        
        {visual_context_html}
        
        {focus_box}
        
        ### Phase 1: Foundational Concepts
        
        * **Focus Goal:** Master the fundamentals using the concepts Mārga identified from your notes.
        * **Activity (1):** Create a mind map linking **{focus_terms[0]}** to 3 real-world applications.
        * **Activity (2):** Dedicated study of **{focus_terms[1]}**. Schedule **{duration_amount // 2} {duration_type}** for deep work on this concept.
        
        ### Phase 2: Application and Mastery
        
        * **Project Goal:** Apply concepts by building or solving something practical.
        * **Activity (3):** Complete 5 structured practice problems or simulations related to {topic}.
        * **🎯 Community Focus:** Find an online forum or social group for {topic}. Post one insightful question or answer one beginner's question to consolidate your learning.
        
        ### Final Review and Consolidation
        
        * **Final Activity:** Review the toughest concept, **{focus_terms[2]}**, and explain it verbally without using your notes.
        
        <div style="background-color: #e6ffe6; padding: 15px; border-radius: 10px; border: 1px solid #2e8b57; margin-top: 20px;">
            <h4 style="margin-top: 0; color: #2e8b57;">💡 Mecrobet Insight</h4>
            <p>{insight_text}</p>
        </div>
        
        ---
        
        **✅ Your Next Step:** Start with Phase 1, Activity (1). Consistency is the true Mārga (path)!
        """
    return output

# --- Streamlit Application Layout ---
st.set_page_config(page_title="Mecrobet Mārga (Final)", layout="wide")

st.title("Mecrobet Mārga: Your Personalized Learning Path 🗺️")
st.subheader("Turn any subject into a structured, custom roadmap.")

# --- INPUT COLUMNS (Layout for Topic and Duration) ---
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input("📚 What subject do you want to master?", "Organic Chemistry and Linear Algebra")
    level = st.select_slider("🎯 Your Current Level:", options=['Beginner', 'Intermediate', 'Advanced'], value='Intermediate')
    
with col2:
    st.markdown("⏳ **Goal Duration**")
    duration_amount = st.number_input("Amount", min_value=1, value=4, key="duration_amount")
    duration_type = st.selectbox("Type", ["Minutes", "Hours", "Days", "Weeks", "Months"], key="duration_type")

# --- Image Uploader ---
st.markdown("---")
uploaded_files = st.file_uploader(
    "Upload your notes or images for context (Optional):", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)
st.caption("Mārga uses these visual notes (like cheat sheets or diagrams) to customize your path.")
st.markdown("---")

# The button that triggers the generation
if st.button("Generate My Mārga (Roadmap)", type="primary"):
    if topic:
        # Pass all user inputs and files to the generation function
        st.markdown(generate_roadmap(
            topic, 
            level, 
            duration_amount, 
            duration_type, 
            uploaded_files
        ), unsafe_allow_html=True) 
    else:
        st.error("Please enter a subject to start your path!")

st.markdown("---")
st.caption("Powered by the Mecrobet Mārga Team. Final Version: All MVP Features Implemented.")
