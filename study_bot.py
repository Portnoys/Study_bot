import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
import random
import os
import pygame

# Initialize Pygame for sounds
pygame.mixer.init()

# Load questions from CSV
def load_questions(filename="study_questions.csv"):
    return pd.read_csv(filename).to_dict(orient="records")  # Convert to list of dictionaries

all_questions = load_questions()
questions = all_questions.copy()  # Working list
total_questions = len(questions)
points_per_question = 100 / total_questions  # Points per correct answer
score = 0
current_question = {}
options = {}
hint_used = False
retry_used = False
rainbow_colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
rainbow_index = 0

# Function to play sound
def play_sound(sound_file):
    if os.path.exists(sound_file):
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

# Function to start the quiz
def start_quiz():
    intro_frame.pack_forget()  # Hide intro page
    quiz_frame.pack()  # Show quiz UI
    ask_question()

# Function to show intro screen
def show_intro():
    intro_text.set(f"📖 Welcome to the Study Bot!\n\nThis quiz contains {total_questions} questions.\n"
                   f"Each correct answer is worth {int(points_per_question)} points.\n"
                   f"If you answer correctly after a hint, you get {int(points_per_question / 2)} points.\n"
                   "If both attempts are incorrect, the correct answer is shown and you get 0 points.\n\n"
                   "Click 'Start' to begin.")
    intro_frame.pack()
    quiz_frame.pack_forget()

# Function to ask a new question
def ask_question():
    global current_question, options, hint_used, retry_used
    hint_used = False
    retry_used = False

    if not questions:  # If all questions are answered, show final score
        show_final_score()
        return

    current_question = questions.pop(random.randint(0, len(questions) - 1))

    # Update question text
    question_label.config(text=f"📖 {current_question['Question']}")

    # Set button texts (No A., B., C., D.)
    options = {
        "A": current_question["Option_A"],
        "B": current_question["Option_B"],
        "C": current_question["Option_C"],
        "D": current_question["Option_D"]
    }
    for btn, key in zip([button_A, button_B, button_C, button_D], options.keys()):
        btn.config(text=f"{options[key]}", bg="#f0f0f0", command=lambda k=key: check_answer(k))

    # Hide next question button
    next_btn.pack_forget()

    # Clear previous responses
    hint_label.config(text="")
    feedback_label.config(text="")

    # Load and display image (if available)
    image_path = current_question["Image"]
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize((300, 200))
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img
    else:
        image_label.config(image="", text="(No Image)")

# Function to check answer
def check_answer(selected_option):
    global score, hint_used, retry_used

    if selected_option == current_question["Correct_Answer"]:
        points_earned = points_per_question if not hint_used else points_per_question / 2
        score += points_earned
        feedback_label.config(text=f"✅ Correct! +{int(points_earned)} points", fg="green")
        play_sound("correct.mp3")
        score_label.config(text=f"Final Score: {int(score)}")
        root.after(1000, ask_question)
    else:
        if not hint_used:
            hint_label.config(text=f"💡 Hint: {current_question['Hint']}")
            feedback_label.config(text="❌ Incorrect. Try again!", fg="red")
            play_sound("wrong.mp3")
            hint_used = True
        elif not retry_used:
            feedback_label.config(text="❌ Still incorrect! The correct answer is highlighted.", fg="red")
            highlight_correct_answer()
            play_sound("wrong.mp3")
            next_btn.pack(pady=10)
            retry_used = True

# Function to highlight the correct answer
def highlight_correct_answer():
    correct = current_question["Correct_Answer"]
    for btn, key in zip([button_A, button_B, button_C, button_D], options.keys()):
        if key == correct:
            btn.config(bg="lightgreen")
        else:
            btn.config(bg="#f0f0f0")

# Function to show final score
def show_final_score():
    global score
    final_score = int(score)

    question_label.config(text="🎯 Quiz Completed!")
    image_label.config(image="", text="")
    feedback_label.config(text="")
    hint_label.config(text="")

    # Hide question buttons
    button_A.pack_forget()
    button_B.pack_forget()
    button_C.pack_forget()
    button_D.pack_forget()

    # Display final grade
    score_label.config(text=f"Final Score: {final_score}")

    # If 100 points, start rainbow celebration 🎉
    if final_score == 100:
        start_rainbow_effect()

    # Show restart button
    restart_btn.pack(pady=10)

# Function to cycle through rainbow colors
def start_rainbow_effect():
    global rainbow_index
    rainbow_index = 0
    change_to_next_rainbow_color()

# Function to change to the next rainbow color
def change_to_next_rainbow_color():
    global rainbow_index
    if rainbow_index < len(rainbow_colors):
        new_color = rainbow_colors[rainbow_index]
        root.configure(bg=new_color)
        quiz_frame.configure(bg=new_color)
        score_label.config(bg=new_color)
        rainbow_index += 1
        root.after(300, change_to_next_rainbow_color)  # Change color every 300ms
    else:
        root.after(1000, reset_background)  # After 3 seconds, reset background

# Function to reset background after celebration
def reset_background():
    root.configure(bg="white")
    quiz_frame.configure(bg="white")
    score_label.config(bg="white")

# Function to restart quiz
def restart_quiz():
    global questions, score
    questions = all_questions.copy()
    score = 0
    score_label.config(text=f"Final Score: {int(score)}")

    # Restore UI
    question_label.config(text="")
    button_A.pack(pady=5)
    button_B.pack(pady=5)
    button_C.pack(pady=5)
    button_D.pack(pady=5)
    restart_btn.pack_forget()

    show_intro()

# GUI Setup
root = tk.Tk()
root.title("Study Bot")
root.geometry("600x550")
root.configure(bg="white")

# **Intro Frame**
intro_frame = tk.Frame(root, bg="white")
intro_text = tk.StringVar()
intro_label = tk.Label(intro_frame, textvariable=intro_text, font=("Arial", 14), bg="white", wraplength=500)
intro_label.pack(pady=20)
start_btn = tk.Button(intro_frame, text="Start", font=("Arial", 14, "bold"), command=start_quiz, bg="#4CAF50", fg="white")
start_btn.pack(pady=10)

# **Quiz Frame**
quiz_frame = tk.Frame(root, bg="white")

question_label = tk.Label(quiz_frame, text="", font=("Arial", 16, "bold"), bg="white", wraplength=550)
question_label.pack(pady=20)

image_label = tk.Label(quiz_frame, text="", bg="white")
image_label.pack(pady=10)

button_A = tk.Button(quiz_frame, text="", font=("Arial", 14, "bold"), width=25, bg="#f0f0f0")
button_A.pack(pady=5)
button_B = tk.Button(quiz_frame, text="", font=("Arial", 14, "bold"), width=25, bg="#f0f0f0")
button_B.pack(pady=5)
button_C = tk.Button(quiz_frame, text="", font=("Arial", 14, "bold"), width=25, bg="#f0f0f0")
button_C.pack(pady=5)
button_D = tk.Button(quiz_frame, text="", font=("Arial", 14, "bold"), width=25, bg="#f0f0f0")
button_D.pack(pady=5)

next_btn = tk.Button(quiz_frame, text="Next Question", font=("Arial", 14, "bold"), command=ask_question, bg="#2196F3", fg="white")
next_btn.pack_forget()

hint_label = tk.Label(quiz_frame, text="", font=("Arial", 14, "italic"), fg="blue", bg="white")
hint_label.pack()
feedback_label = tk.Label(quiz_frame, text="", font=("Arial", 16, "bold"), bg="white")
feedback_label.pack()
score_label = tk.Label(quiz_frame, text="Final Score: 0", font=("Arial", 14), bg="white")
score_label.pack(pady=10)

restart_btn = tk.Button(quiz_frame, text="Restart Quiz", font=("Arial", 14, "bold"), command=restart_quiz, bg="#FF5733", fg="white")
restart_btn.pack_forget()

show_intro()
root.mainloop()
