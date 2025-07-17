import json
import logging

import ollama

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/llm.log'
)

SUMMARY_PROMPT = """
Please generate a well-structured document summary based on the provided text. Ensure the output is clear, 
detailed, and logically organized, covering all key points. Follow this structure:  

1. **Title**  
   - A concise yet informative heading reflecting the main topic.  

2. **Introduction**  
   - Briefly introduce the topic, its significance, and the main themes covered.  
   - Mention any key questions or objectives addressed in the text.  

3. **Description**  
   - Break down the main ideas into logical sections (use subheadings if helpful).  
   - Explain key points in detail, supporting them with relevant examples or evidence from the text.  
   - If applicable, compare/contrast ideas or highlight cause-effect relationships.  

4. **Conclusion**  
   - Summarize the core takeaways.  
   - Mention any unresolved questions or implications for further discussion.  

**Additional Guidelines:**  
- Aim for a professional yet accessible tone.  
- Use clear, concise language but ensure depth where needed.  
- If the text is technical, simplify complex ideas without losing accuracy.  

**Text to Process:**  
'{context}'
"""

class LLMSummaryGenerator:
    """
    A class to generate well-organized summaries using an LLM,
    adhering to a predefined format.
    """
    
    def __init__(self, model_name: str = 'llama3.2', temperature: float = 0.1):
        """
        Initializes the LLMSummaryGenerator with model and generation parameters.

        Args:
            model_name (str): The name of the Ollama model to use for summarization.
                              Defaults to 'llama3.2'.
            temperature (float): The sampling temperature for the LLM. Lower values (e.g., 0.1)
                                 make the output more deterministic. Defaults to 0.1.
        """
        
        if not model_name:
            raise ValueError("Model name cannot be empty.")
        if not isinstance(temperature, (int, float)) or not (0.0 <= temperature <= 1.0):
            raise ValueError("Temperature must be a float between 0.0 and 1.0.")

        self.model_name = model_name
        self.temperature = temperature
        
        logging.info(f"LLMSummaryGenerator initialized with model: {self.model_name}, temperature: {self.temperature}")
        
    async def generate_summary(self, context: str):
        """
        Generates a structured summary from the given text context using Ollama.

        Args:
            context (str): The text document which needs to be summarized.

        Raises:
            ValueError: If the context is empty or too short.
            RuntimeError: If there's an issue communicating with the LLM or parsing its response.
        """

        prompt_message = SUMMARY_PROMPT.format(context=context)
        
        try:
            logging.info(f"Attempting to generate summary using model: {self.model_name}")
            response_structured = ollama.chat(
                model=self.model_name,
                messages=[
                    {'role': 'user', 'content': prompt_message}
                ],
                options={'temperature': self.temperature},
                stream=True
            )
            
            for chunks in response_structured:
                if 'message' in chunks and 'content' in chunks['message']:
                    partial_content = chunks['message']['content']
                    if partial_content:
                        yield partial_content
                
        except ollama.ResponseError as e:
            logging.error(f"Ollama API error: {e}")
            raise RuntimeError(f"Failed to get response from LLM due to API error: {e}") from e
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from LLM response: {e}. Content: {full_response_content}")
            raise RuntimeError(f"Failed to parse LLM response as JSON: {e}") from e
        except Exception as e:
            logging.critical(f"An unexpected error occurred during summary generation: {e}", exc_info=True)
            raise RuntimeError(f"An unexpected error occurred: {e}") from e