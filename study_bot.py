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
        required_columns = ["Question", "Option_A", "Option_B", "Option_C", "Option_D", "Correct_Answer", "Hint"]
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
                    <audio autoplay>
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
if "hint_used" not in st.session_state:
    st.session_state.hint_used = False
if "quiz_done" not in st.session_state:
    st.session_state.quiz_done = False
if "last_selected_answer" not in st.session_state:
    st.session_state.last_selected_answer = None

# Display quiz
st.title("🧠 Study Bot Quiz")

if st.session_state.question_index < len(questions) and not st.session_state.quiz_done:
    q = questions[st.session_state.question_index]

    # Show question
    st.subheader(q["Question"])

    # Show image if available
    if "Image" in q:
        image_path = str(q["Image"]).strip()
        
        if image_path.startswith("http") or image_path.startswith("https"):  
            st.image(image_path, width=300)  # Load online images
        elif os.path.exists(image_path):  
            try:
                st.image(image_path, width=300)  # Load local images
            except Exception as e:
                st.warning(f"⚠️ Could not load image: {image_path}. Error: {e}")
        else:
            st.warning(f"⚠️ Image not found: {image_path}. Please check file location.")

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

    # Show hint if the user previously got it wrong
    if st.session_state.hint_used and st.session_state.last_selected_answer == answer:
        st.warning(f"💡 Hint: {q['Hint']}")

    # Check answer when submit button is clicked
    if st.button("Submit"):
        if answer and correct_answer:
            st.session_state.last_selected_answer = answer  # Save last selected answer

            if answer == correct_answer:
                points = 100 / len(questions) if not st.session_state.hint_used else (100 / len(questions)) / 2
                st.session_state.score += int(points)
                st.success(f"✅ Correct! +{int(points)} points")

                # Play correct sound
                if "Sound_Correct" in q:
                    play_sound(q["Sound_Correct"])

                st.session_state.question_index += 1
                st.session_state.hint_used = False  # Reset hint usage for next question
            else:
                if not st.session_state.hint_used:
                    st.session_state.hint_used = True

                    # Play incorrect sound
                    if "Sound_Incorrect" in q:
                        play_sound(q["Sound_Incorrect"])

                else:
                    st.error(f"❌ Incorrect again! The correct answer was: {correct_answer}")
                    st.session_state.question_index += 1
                    st.session_state.hint_used = False  # Reset hint usage for next question

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
        st.session_state.hint_used = False
        st.session_state.quiz_done = False
        st.rerun()
