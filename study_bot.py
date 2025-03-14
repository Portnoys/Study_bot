import streamlit as st
import pandas as pd
import random

# Load questions from CSV
@st.cache_data
def load_questions():
    try:
        df = pd.read_csv("study_questions.csv")
        
        # Ensure column names are correctly formatted (strip spaces)
        df.columns = df.columns.str.strip()

        # Check if Correct_Answer column exists
        if "Correct_Answer" not in df.columns:
            st.error("⚠️ Error: 'Correct_Answer' column is missing from CSV.")
            return []
        
        # Ensure Correct_Answer values are correctly formatted
        valid_options = ["Option_A", "Option_B", "Option_C", "Option_D"]
        df["Correct_Answer"] = df["Correct_Answer"].astype(str).str.strip()
        
        # Check for invalid Correct_Answer values
        invalid_answers = df[~df["Correct_Answer"].isin(valid_options)]
        if not invalid_answers.empty:
            st.error(f"⚠️ Error: Found invalid values in 'Correct_Answer' column. Ensure all values are 'Option_A', 'Option_B', etc.")
            return []
        
        return df.to_dict(orient="records")
    
    except Exception as e:
        st.error(f"⚠️ Error loading questions: {str(e)}")
        return []

questions = load_questions()

# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "hint_used" not in st.session_state:
    st.session_state.hint_used = False
if "quiz_done" not in st.session_state:
    st.session_state.quiz_done = False

# Display quiz
st.title("🧠 Study Bot Quiz")

if st.session_state.question_index < len(questions) and not st.session_state.quiz_done:
    q = questions[st.session_state.question_index]

    # Show question and image (if available)
    st.subheader(q["Question"])
    if "Image" in q and isinstance(q["Image"], str) and q["Image"].strip():
        st.image(q["Image"], width=300)

    # Show multiple-choice options
    options = [q["Option_A"], q["Option_B"], q["Option_C"], q["Option_D"]]
    answer = st.radio("Choose an answer:", options, index=None)

    # Validate Correct_Answer column
    if "Correct_Answer" in q:
        correct_option = str(q["Correct_Answer"]).strip()  # Ensure it's a string and remove spaces

        # Fix: Ensure correct_option is valid and exists in q
        valid_options = ["Option_A", "Option_B", "Option_C", "Option_D"]
        if correct_option in valid_options and correct_option in q:
            correct_answer = str(q[correct_option]).strip()  # Get actual answer text and clean spaces
        else:
            st.error(f"⚠️ Error: '{correct_option}' is not valid. Check CSV formatting.")
            correct_answer = None
    else:
        st.error("⚠️ Error: 'Correct_Answer' column not found in CSV.")
        correct_answer = None

    # Check answer when submit button is clicked
    if st.button("Submit"):
        if answer and correct_answer:
            if answer == correct_answer:
                points = 100 / len(questions) if not st.session_state.hint_used else (100 / len(questions)) / 2
                st.session_state.score += int(points)
                st.success(f"✅ Correct! +{int(points)} points")
                st.session_state.question_index += 1
                st.session_state.hint_used = False  # Reset hint usage for next question
            else:
                if not st.session_state.hint_used:
                    st.warning(f"💡 Hint: {q['Hint']}")
                    st.session_state.hint_used = True
                else:
                    st.error(f"❌ Incorrect again! The correct answer was: {correct_answer}")
                    st.session_state.question_index += 1
                    st.session_state.hint_used = False  # Reset hint usage for next question
            st.experimental_rerun()
        else:
            st.warning("⚠️ Please select an answer before submitting.")

# Show final score
if st.session_state.question_index >= len(questions):
    st.session_state.quiz_done = True
    final_score = int(st.session_state.score)
    st.title("🎯 Quiz Completed!")
    st.header(f"Final Score: {final_score}")

    # Celebration for 100 points
    if final_score == 100:
        st.balloons()
        st.markdown("<h2 style='color:green;'>🎉 Perfect Score! You nailed it! 🎉</h2>", unsafe_allow_html=True)

    # Restart button
    if st.button("Restart Quiz"):
        st.session_state.score = 0
        st.session_state.question_index = 0
        st.session_state.hint_used = False
        st.session_state.quiz_done = False
        st.experimental_rerun()
