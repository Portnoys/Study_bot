import streamlit as st
import pandas as pd
import random

# Load questions from CSV
@st.cache_data
def load_questions():
    return pd.read_csv("study_questions.csv").to_dict(orient="records")

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

        # Ensure the correct answer key is actually in the row
        if correct_option in q and correct_option in ["Option_A", "Option_B", "Option_C", "Option_D"]:
            correct_answer = q[correct_option]  # Get the actual answer text
        else:
            st.error(f"⚠️ Error: '{correct_option}' is not a valid answer option in the question data.")
            correct_answer = None
    else:
        st.error("⚠️ Error: 'Correct_Answer' column not found in CSV. Ensure correct spelling.")
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
