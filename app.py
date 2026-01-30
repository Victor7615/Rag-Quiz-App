import streamlit as st
import os
from backend.rag import process_resource, generate_quiz
from backend.database import save_score

st.set_page_config(page_title="RAG Quiz Gen", layout="wide")

# API Key Handling
if "OPENAI_API_KEY" in os.environ:
    api_key = os.environ["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

st.title("🧠 Grounded Quiz Generator")

with st.sidebar:
    st.header("1. Configuration")
    # --- NEW FEATURE: Question Count Slider ---
    num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)
    
    st.header("2. Upload Source")
    mode = st.radio("Source Type", ["PDF", "YouTube"])
    
    if mode == "PDF":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file and api_key:
            # Save to disk because LangChain loaders need a file path
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("Process PDF"):
                with st.spinner("Analyzing Document..."):
                    st.session_state.vectorstore = process_resource(file_path="temp.pdf", api_key=api_key)
                    st.session_state.resource_name = uploaded_file.name
                    st.success("PDF Ready!")

    elif mode == "YouTube":
        yt_url = st.text_input("Paste YouTube URL")
        if yt_url and api_key and st.button("Process Video"):
            with st.spinner("Fetching Transcript..."):
                st.session_state.vectorstore = process_resource(youtube_url=yt_url, api_key=api_key)
                st.session_state.resource_name = yt_url
                st.success("Video Ready!")

# --- Main Quiz Area ---
if 'vectorstore' in st.session_state:
    st.divider()
    st.subheader(f"Quiz: {st.session_state.get('resource_name', 'Unknown')}")
    
    # Generate Button
    if st.button("Generate New Quiz"):
        with st.spinner(f"Generating {num_questions} questions..."):
            # Pass the slider value to the backend
            quiz_data = generate_quiz(
                st.session_state.vectorstore, 
                num_questions=num_questions, 
                api_key=api_key
            )
            st.session_state.quiz_data = quiz_data
            # Reset previous answers
            for key in list(st.session_state.keys()):
                if key.startswith("q_answer_"):
                    del st.session_state[key]

    # Display Quiz
    if 'quiz_data' in st.session_state:
        with st.form("quiz_form"):
            score = 0
            # Iterate through questions
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**{i+1}. {q['question']}**")
                
                # Unique key for every question widget
                st.radio(
                    "Select an answer:", 
                    q['options'], 
                    key=f"q_answer_{i}",
                    index=None # No default selection
                )
                st.divider()
                
            submitted = st.form_submit_button("Submit Answers")
            
            if submitted:
                score = 0
                
                for i, q in enumerate(st.session_state.quiz_data):
                    user_choice = st.session_state.get(f"q_answer_{i}")
                    
                    if user_choice:
                        # 1. Determine which "Index" the user selected (0, 1, 2, 3)
                        # We look up the selected text in the original options list
                        try:
                            selected_index = q['options'].index(user_choice)
                            
                            # 2. Convert Index to Letter (0->A, 1->B, 2->C...)
                            # chr(65) is 'A', chr(66) is 'B', etc.
                            selected_letter = chr(65 + selected_index)
                        except ValueError:
                            selected_letter = None

                        # 3. Compare BOTH possibilities (Robust check)
                        # Case A: LLM said answer is "A" (Compare letters)
                        # Case B: LLM said answer is "The Mitochondria" (Compare text)
                        correct_raw = q['correct_answer'].strip()
                        
                        is_letter_match = (selected_letter == correct_raw)
                        is_text_match = (user_choice.strip() == correct_raw)

                        if is_letter_match or is_text_match:
                            score += 1
                
                total = len(st.session_state.quiz_data)
                st.balloons()
                st.write(f"### 🏆 Score: {score} / {total}")
                
                # Save to Database
                try:
                    # Using hardcoded User ID 1 for now
                    save_score(1, st.session_state.resource_name, score, total)
                    st.success("Score saved to database!")
                except Exception as e:
                    st.error(f"⚠️ Database Error: {e}")

                # Show Answers & Explanations
                st.subheader("📝 Review")
                for i, q in enumerate(st.session_state.quiz_data):
                    user_choice = st.session_state.get(f"q_answer_{i}")
                    color = "green" if user_choice == q['correct_answer'] else "red"
                    
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    st.markdown(f":{color}[Your Answer: {user_choice}]")
                    
                    if user_choice != q['correct_answer']:
                        st.info(f"✅ Correct Answer: {q['correct_answer']}")
                        
                    with st.expander("Why? (Explanation)"):
                        st.write(q['explanation'])
else:
    st.info("👈 Upload a file to start.")