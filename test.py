import google.generativeai as genai
import PIL.Image
import os

# Set the API key directly in the script
api_key = "AIzaSyBnE-I5WcML3E6BkNJi1YsrJGQUMtRpssk"

genai.configure(api_key=api_key)

def generate_content_with_gemini(query, img_path=None):
    # Load image if path is provided
    img = None
    if img_path:
        img = PIL.Image.open(img_path)
    
    # Create the model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    # Generate content
    if img:
        response = model.generate_content([query, img])
    else:
        response = model.generate_content([query])
    
    return response.text

def main():
    while True:
        query = input("Enter your query: ").strip()
        if query:
            img_path = input("Enter the image path (or press Enter to skip): ").strip()
            if not img_path:
                img_path = None
            try:
                response_text = generate_content_with_gemini(query, img_path)
                print(response_text)
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
