import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from prompt_toolkit.completion import FuzzyCompleter, Completion
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit import PromptSession
import requests

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set up OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

class ModelCompleter:
    def __init__(self, models):
        self.models = models

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for model in self.models:
            if word.lower() in model.lower():
                yield Completion(model, start_position=-len(word))

class AIInterface:
    def __init__(self):
        self.model_reference = self.load_model_reference()
        self.models, self.model_count = self.list_models()

    def load_model_reference(self):
        with open('Model_Reference/enhanced_model_reference.json', 'r') as f:
            return json.load(f)

    def answer_model_questions(self):
        while True:
            question = input("Enter your question about AI models (or 'back' to return to main menu): ")
            if question.lower() == 'back':
                return
            prompt = f"""You are a helpful assistant with knowledge about various AI models. 
            Based on the following model reference data, please answer this question: {question}
            
            Model Reference Data: {json.dumps(self.model_reference, indent=2)}"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant with knowledge about various AI models."},
                    {"role": "user", "content": prompt}
                ]
            )
            print(f"\nAnswer: {response.choices[0].message.content}")

    def test_model(self):
        while True:
            model_id = self.select_model()
            if model_id.lower() == 'back':
                return
            print(f"\nYou selected: {model_id}")
            confirm = input("Is this correct? (y/n/back): ").lower()
            if confirm == 'back':
                continue
            if confirm != 'y':
                continue
            prompt = input("Enter the prompt for the model (or 'back' to return to model selection): ")
            if prompt.lower() == 'back':
                continue

            # OpenRouter API call
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": os.getenv('YOUR_SITE_URL', 'http://localhost:5000'),  # Optional
                "X-Title": os.getenv('YOUR_SITE_NAME', 'AI Interface'),  # Optional
                "Content-Type": "application/json"
            }
            data = {
                "model": model_id,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                result = response.json()
                print("\nModel Response:")
                print(result['choices'][0]['message']['content'])
            except requests.exceptions.RequestException as e:
                print(f"\nError occurred: {e}")
            
            action = input("\nPress Enter to test another prompt, or type 'back' to select a different model: ")
            if action.lower() == 'back':
                continue

    def list_models(self):
        text_models = [model['id'] for model in self.model_reference['text_models']]
        media_models = [model['id'] for model in self.model_reference['media_models']]
        all_models = text_models + media_models
        model_count = len(all_models)
        print(f"\nTotal number of models extracted: {model_count}")
        print(f"Text models: {len(text_models)}")
        print(f"Media models: {len(media_models)}")
        return all_models, model_count  # Return both the list and the count

    def select_model(self):
        completer = FuzzyCompleter(ModelCompleter(self.models + ['back']))
        while True:
            session = PromptSession(
                'Select a model (type to search, use arrow keys to navigate, or type "back" to return): ',
                completer=completer,
                complete_style=CompleteStyle.MULTI_COLUMN
            )
            selected = session.prompt()
            if selected.lower() == 'back':
                return 'back'
            if selected in self.models:
                return selected
            else:
                print("Invalid selection. Please choose a model from the list or type 'back'.")

    def display_models(self):
        print(f"\nTotal number of models: {self.model_count}")
        print("\nAvailable models:")
        for model in self.models:
            print(f"- {model}")
        print("\nType 'back' to return to the main menu.")
        while True:
            action = input("Press Enter to continue viewing the list, or type 'back': ").lower()
            if action == 'back':
                return
            elif action == '':
                continue
            else:
                print("Invalid input. Please press Enter to continue or type 'back'.")

# Example usage
if __name__ == "__main__":
    ai = AIInterface()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Ask a question about AI models")
        print("2. Test a specific model")
        print("3. List available models")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            ai.answer_model_questions()
        
        elif choice == '2':
            ai.test_model()
        
        elif choice == '3':
            ai.display_models()
            continue
        
        elif choice == '4':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
