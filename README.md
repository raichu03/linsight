# linsight

Get insights into different topics with *`linsight`*. Ask questions and get the answers you need with the LLM-powered tool locally on your machine.

## Features
- **Local Execution**: Runs entirely on your machine, ensuring privacy and security.
- **LLM-Powered**: Utilizes large language models to provide accurate and relevant answers
- **Easy to Use**: Pre-built web interface for quick access to insights.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/raichu03/linsight.git
```
2. Navigate to the project directory:
```bash
cd linsight
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```
4. Install the ollama in your system 
   - Follow the instructions at [Ollama Installation](https://ollama.com) to install Ollama on your system.
5. Pull the required LLM model:
```bash
ollama pull llama3.2
```
   - Ensure you have the `llama3.2` model available locally.

6. Go to the `app` directory:
```bash
cd app
```
7. Set up the environment variables:
- Create a `.env` file in the `app` directory and add your Google Search API and Google Custom Search API keys:
   ```
   SEARCH_KEY=your_google_search_api_key
   SEARCH_ID=your_google_custom_search_api_id
   ```  

8. Start the application:
```bash
python main.py
```
9. Open your web browser and navigate to `http://127.0.0.1:8000/` to access the application. Or click on the link provided in the terminal after running the application.

## Usage
- Enter your question in the input field and click the send or press the enter button.
- The application will process your question and return the answer using the LLM model.
- It might use Google Search to find relevant information if needed.

## License
This project is licensed under the GNU GENERAL PUBLIC LICENSE v3.0. See the [LICENSE](LICENSE) file for details.

Note: *This project is still being developed....*