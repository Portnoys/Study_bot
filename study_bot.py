import streamlit as st
import pandas as pd
import os
import base64
import time

# Load questions from CSV
@st.cache_data
def load_questions():
    try:
        df = pd.read_csv("study_questions.csv")
        
        # Ensure column names are correctly formatted (strip spaces)
        df.columns = df.columns.str.strip()

        # Check if required columns exist
        required_columns = ["Question", "Option_A", "Option_B", "Option_C", "Option_D", "Correct_Answer", "Hint", "Image"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"⚠️ Error: Missing columns in CSV: {missing_columns}")
            return []
        
        # Ensure Correct_Answer values are correctly formatted
        valid_options = ["Option_A", "Option_B", "Option_C", "Option_D"]
        df["Correct_Answer"] = df["Correct_Answer"].astype(str).str.strip()

        # Check for invalid Correct_Answer values
        invalid_answers = df[~df["Correct_Answer"].isin(valid_options)]
        if not invalid_answers.empty:
            st.error(f"⚠️ Error: Invalid values in 'Correct_Answer' column. Must be 'Option_A', 'Option_B', etc.")
            return []

        return df.to_dict(orient="records")
    
    except Exception as e:
        st.error(f"⚠️ Error loading questions: {str(e)}")
        return []

questions = load_questions()

# Function to play sounds
def play_sound(sound_file):
    if sound_file and isinstance(sound_file, str) and sound_file.strip():
        try:
            if sound_file.startswith("http") or sound_file.startswith("https"):
                st.audio(sound_file, format="audio/mp3")  # Play online audio

            elif os.path.exists(sound_file):
                with open(sound_file, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    audio_html = f"""
                    <audio controls autoplay>
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                        Your browser does not support the audio element.
                    </audio>
                    """
                    st.markdown(audio_html, unsafe_allow_html=True)

            else:
                st.warning(f"⚠️ Sound file not found: {sound_file}")

        except Exception as e:
            st.warning(f"⚠️ Error playing sound: {e}")

# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "hint_visible" not in st.session_state:
    st.session_state.hint_visible = False
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

# Show intro page
if not st.session_state.quiz_started:
    st.title("🧠 Study Bot Quiz")
    total_questions = len(questions)
    points_per_question = 100 / total_questions

    st.markdown(f"""
        **Welcome to the Study Bot Quiz!**  
        - There are **{total_questions}** questions.  
        - Each question is worth **{int(points_per_question)} points**.  
        - If you answer **correctly after a hint**, you get **half the points**.  
        - You have **one extra attempt** after seeing the hint.  
    """)

    if st.button("Start Quiz"):
        st.session_state.quiz_started = True
        st.rerun()
else:
    # Display quiz
    if st.session_state.question_index < len(questions):
        q = questions[st.session_state.question_index]

        # Show question
        st.subheader(q["Question"])

        # Show image if available
        image_path = str(q.get("Image", "")).strip()
        if image_path:
            if image_path.startswith("http") or image_path.startswith("https"):  
                st.image(image_path, width=300)  # Load online images
            elif os.path.exists(image_path):  
                st.image(image_path, width=300)  # Load local images
            else:
                st.warning(f"⚠️ Image not found: {image_path}. Please check file location.")

        # Show multiple-choice options
        options = [q["Option_A"], q["Option_B"], q["Option_C"], q["Option_D"]]
        answer = st.radio("Choose an answer:", options, index=None)

        # Validate Correct_Answer column
        correct_option = str(q["Correct_Answer"]).strip()
        correct_answer = q.get(correct_option, "")

        # Show hint if it was revealed
        if st.session_state.hint_visible:
            st.warning(f"💡 Hint: {q['Hint']}")

        # Check answer when submit button is clicked
        if st.button("Submit"):
            if answer and correct_answer:
                if answer == correct_answer:
                    points = 100 / len(questions) if not st.session_state.hint_visible else (100 / len(questions)) / 2
                    st.session_state.score += int(points)
                    st.success(f"✅ Correct! +{int(points)} points")

                    # Play correct sound
                    play_sound(q.get("Sound_Correct", ""))

                    st.session_state.question_index += 1
                    st.session_state.hint_visible = False  # Reset hint usage for next question
                else:
                    if not st.session_state.hint_visible:
                        st.session_state.hint_visible = True
                        play_sound(q.get("Sound_Incorrect", ""))
                    else:
                        st.error(f"❌ Incorrect again! The correct answer was: {correct_answer}")
                        st.session_state.question_index += 1
                        st.session_state.hint_visible = False  # Reset hint usage for next question

                time.sleep(1)  # Small delay to let the sound play before reloading
                st.rerun()
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
        st.session_state.hint_visible = False
        st.session_state.quiz_started = False
        st.rerun()
