import json
import os
import time
import logging
import openai
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MODEL_REFERENCE_DIR = "Model_Reference"
ORIGINAL_FILE = os.path.join(MODEL_REFERENCE_DIR, "model_reference.json")
ENHANCED_FILE = os.path.join(MODEL_REFERENCE_DIR, "enhanced_model_reference.json")

# Initialize OpenAI client
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

client = openai.OpenAI(api_key=openai_api_key)

def load_original_data():
    with open(ORIGINAL_FILE, 'r') as f:
        return json.load(f)

def perform_search(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=10))
    return [{"title": r['title'], "body": r['body']} for r in results]

def ai_search_and_extract_speed(model_name):
    messages = [
        {"role": "system", "content": "You are an AI assistant that provides concise information about AI model performance in terms of tokens per second. Always respond with a single, brief sentence."},
        {"role": "user", "content": f"Find and report the performance of the AI model '{model_name}' in tokens per second. Provide the information in a single, concise sentence. If no specific tokens per second data is found, briefly state that."}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            function_call="auto",
            functions=[
                {
                    "name": "search",
                    "description": "Search DuckDuckGo for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        )

        message = response.choices[0].message

        if message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            
            if function_name == "search":
                search_results = perform_search(function_args['query'])
                messages.append({
                    "role": "function",
                    "name": "search",
                    "content": json.dumps(search_results)
                })
            else:
                return f"Unexpected function call: {function_name}"
        else:
            return message.content.strip()

        if len(messages) > 10:  # Limit the conversation to prevent infinite loops
            return "No specific tokens per second information found."

def ai_get_model_description(model_name):
    messages = [
        {"role": "system", "content": "You are an AI assistant that provides concise information about AI models. Respond with brief bullet points."},
        {"role": "user", "content": f"""Provide a concise description of the AI model '{model_name}' with the following information:
        - What the model is good at
        - What the model is not good at
        - Other relevant information for assessing the model's capabilities
        - Whether it's a variant of an existing model (if applicable)
        Use brief bullet points and keep the total response under 100 words."""}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            function_call="auto",
            functions=[
                {
                    "name": "search",
                    "description": "Search DuckDuckGo for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        )

        message = response.choices[0].message

        if message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            
            if function_name == "search":
                search_results = perform_search(function_args['query'])
                messages.append({
                    "role": "function",
                    "name": "search",
                    "content": json.dumps(search_results)
                })
            else:
                return f"Unexpected function call: {function_name}"
        else:
            return message.content.strip()

        if len(messages) > 10:  # Limit the conversation to prevent infinite loops
            return "Unable to gather sufficient information about the model."

def enhance_model_data(model):
    model_name = model['name']
    try:
        speed_info = ai_search_and_extract_speed(model_name)
        model['speed'] = speed_info
        
        description_info = ai_get_model_description(model_name)
        model['description'] = description_info
    except Exception as e:
        logging.error(f"Error processing {model_name}: {str(e)}")
        model['speed'] = "Error occurred while fetching speed information"
        model['description'] = "Error occurred while fetching model description"
    return model

def enhance_all_models(data):
    enhanced_data = {
        'text_models': [],
        'media_models': data['media_models']  # Keep media models unchanged
    }
    
    category = 'text_models'
    total_models = len(data[category])
    for i, model in enumerate(data[category]):
        logging.info(f"Enhancing data for {model['name']} ({i+1}/{total_models})")
        enhanced_model = enhance_model_data(model)
        enhanced_data[category].append(enhanced_model)
        time.sleep(2)  # Add a delay to avoid rate limiting
    
    return enhanced_data

def save_enhanced_data(data):
    with open(ENHANCED_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    original_data = load_original_data()
    enhanced_data = enhance_all_models(original_data)
    save_enhanced_data(enhanced_data)
    logging.info(f"Enhanced model reference saved to {ENHANCED_FILE}")

if __name__ == "__main__":
    main()
