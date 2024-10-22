# AI Model Interface

This project provides an interface for interacting with various AI models through OpenRouter, including a model reference system and a scraper to enhance model information.

## Features

- AI interface for interacting with models via OpenRouter
- Model reference system with detailed information on various AI models
- Scraper to extract model information from OpenRouter and the internet (uses OpenAI)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-model-interface.git
   cd ai-model-interface
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add your API keys:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   Note: The OpenAI API key is only used for the model scraper.

## Usage

1. Run the AI interface (uses OpenRouter):
   ```
   python ai_interface.py
   ```

2. To enhance the model reference data (uses OpenAI):
   ```
   python Scraper/enhance_model_reference.py
   ```

## Project Structure

- `ai_interface.py`: Main interface for interacting with AI models via OpenRouter
- `Scraper/enhance_model_reference.py`: Script to enhance model reference data using OpenAI
- `Model_Reference/`: Directory containing model reference data
  - `model_reference.json`: Original model reference data
  - `enhanced_model_reference.json`: Enhanced model reference data
  - `Backups/`: Backup directory for model reference data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).
