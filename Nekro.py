import speech_recognition as sr
import pyttsx3
import requests
import google.generativeai as genai
from googletrans import Translator
import random
import threading

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Initialize the translator
translator = Translator()

# Configure voices
voices = engine.getProperty('voices')
female_voice = voices[1].id  # First female voice

# Set default voice to female
engine.setProperty('voice', female_voice)

# API keys
NEWS_API_KEY = '6a5756e24dc6452ca3972b960c85184d'
GEMINI_API_KEY = 'AIzaSyBnE-I5WcML3E6BkNJi1YsrJGQUMtRpssk'

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Interaction history
interaction_history = []

# Humor level (0 to 100)
humor_level = 50

# Lock for managing speech interruption
speech_lock = threading.Lock()
interrupt_flag = threading.Event()

def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
        except sr.RequestError:
            print("Sorry, my speech service is down.")
        return None

def translate_text(text, target_language='en'):
    translation = translator.translate(text, dest=target_language)
    return translation.text, translation.src

def handle_greeting():
    greetings = [
        "Hi there! How can I help you today?",
        "Hello! What's up?",
        "Hey! How's it going?",
        "Greetings! How can I assist you?",
        "Hi! What can I do for you today?"
    ]
    return random.choice(greetings)

def handle_casual_chat():
    responses = [
        "I'm cool, well, you got some work or what?",
        "Just hanging out in the cloud, how about you?",
        "All systems operational! How can I help?",
        "Living the digital dream. What's up with you?",
        "Just running some algorithms. Need anything?"
    ]
    return random.choice(responses)

def fetch_gemini_data(query):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([query])
    return response.text

def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        top_articles = articles[:5]  # Get the top 5 articles
        news_summary = ""
        for article in top_articles:
            title = article['title']
            description = article['description']
            news_summary += f"Title: {title}\nDescription: {description}\n\n"
        return news_summary.strip()
    else:
        return "Sorry, I couldn't fetch the news at this moment."

def summarize_text(text):
    # Implement a simple summarization (for example, first 3 sentences)
    sentences = text.split('. ')
    summary = '. '.join(sentences[:3]) + ('...' if len(sentences) > 3 else '')
    return summary

def fetch_real_answer(query):
    if "news" in query.lower():
        return fetch_news(query)
    return fetch_gemini_data(query)

def speak(text):
    with speech_lock:
        interrupt_flag.clear()
        filtered_text = text.replace("*", "")  # Remove asterisks from the text
        engine.say(filtered_text)
        engine.runAndWait()

def interruptible_speak(text):
    thread = threading.Thread(target=speak, args=(text,))
    thread.start()
    return thread

def log_decision(decision, text):
    print(f"Decision: {decision}, Text: {text}")
    interaction_history.append((decision, text))

def generate_response_with_humor(response, humor_level):
    humorous_responses = [
        "Did you know that I'm not just a chatbot, I'm also a comedian?",
        "I could tell you a joke, but you'd probably just LOL!",
        "You know, I've got a million of these responses!"
    ]
    if humor_level > 50:
        response += " " + random.choice(humorous_responses)
    return response

def L1_X_L2(query):
    # Decision Making for L1
    return "Before"

def process_input(text):
    translated_text, detected_language = translate_text(text)
    decision = L1_X_L2(translated_text)
    
    if decision == "Before":
        if "hello" in translated_text.lower():
            response = handle_greeting()
        elif "how are you" in translated_text.lower():
            response = handle_casual_chat()
        elif "set humor level to" in translated_text.lower():
            try:
                global humor_level
                humor_level = int(translated_text.split()[-1])
                response = f"Humor level set to {humor_level}"
            except ValueError:
                response = "I couldn't understand the humor level you want to set."
        else:
            response = fetch_real_answer(translated_text)
            response = summarize_text(response)
    
    response = generate_response_with_humor(response, humor_level)
    print(response)
    speak_thread = interruptible_speak(response)
    
    # # Allow interruption
    # while speak_thread.is_alive():
    #     new_input = input("Press Enter to interrupt: ").strip()
    #     if new_input:
    #         interrupt_flag.set()
    #         engine.stop()
    #         process_input(new_input)
    #         break

# Main loop
while True:
    user_input = input("Nekro: ").strip()
    
    if user_input:
        interrupt_flag.set()
        process_input(user_input)
    else:
        text = recognize_speech()
        if text:
            interrupt_flag.set()
            process_input(text)
