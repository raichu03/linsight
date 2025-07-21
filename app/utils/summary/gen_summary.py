import logging

import ollama

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/summary.log'
)

class DocSummarizer:
    """
    A class for generating extractive summaries of documents using an Ollama-compatible LLM.
    Exnsures strict adherence to extracting verbatim sentences form the input document.
    """
    
    def __init__(self, model_name: str = 'llama3.2', temperature: float = 0.1):
        """
        Initializes the DocumentSummarizer with a specified LLM model and temperature.

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
        logging.info(f"DocumentSummarizer initialized with model: {self.model_name}, temperature: {self.temperature}")
        
    def _construct_prompt(self, document_text: str) -> str:
        """
        Constructs the user prompt for the extractive summarization task.
        
        Args:
            document_text(str): The full text of the document to be summarized.
            
        Returns:
            str: The formatted prompt string.
        """
        
        if not isinstance(document_text, str) or not document_text.strip():
            raise ValueError("Document text must be a non-empty string.")

        prompt = f"""
            You are an **expert extractive summarizer** with a critical mission: to identify and present the most significant and informative sentences **directly from the provided text**.

            **ABSOLUTELY CRITICAL RULE: DO NOT REPHRASE, PARAPHRASE, OR INTRODUCE ANY NEW INFORMATION. EVERY SINGLE WORD IN YOUR SUMMARY MUST BE AN EXACT, UNALTERED QUOTE FROM THE ORIGINAL DOCUMENT.**

            Your selection process should prioritize sentences that:
            * Clearly articulate **core concepts and central themes**.
            * Contain **key arguments and supporting evidence**.
            * Provide **critical details, facts, figures, or definitions**.
            * Represent **important conclusions or outcomes**.

            The goal is a summary that is as **concise as possible** while **retaining all essential, valuable information** needed for a comprehensive understanding of the original document. Focus intensely on **factual accuracy and the completeness of extracted facts**.

            Document:
            {document_text}

            Extractive Summary:
        """
        return prompt.strip()

    def summarize(self, document_text: str) -> str:
        """
        Generate an extractive summary of the given document text.
        
        Args:
            document_test(str): The text of the document to be summarized.
        
        Returns:
            str: The exetractive summary consisting of verbatim sentences from the document.
            
        Raises:
            ValueError: If the input document_text is invalid.
            RuntimeError: If there's an issue comminicating with the Ollama service
                            or if the model fails to return a valid response.
        """
        if not isinstance(document_text, str) or not document_text.strip():
            logging.error("Attempted to summarize with empty or invalid document_text.")
            raise ValueError("Document text cannot be empty or null.")

        user_prompt = self._construct_prompt(document_text)
        
        messages = [
            {'role': 'system',
             'content': """
                You are a highly skilled extractive summarizer. Your goal is to identify
                and present the most critical sentences from a given text, ensuring no essential
                information for subsequent summarization stages is lost. Your output must consist
                solely of verbatim sentences from the original document, carefully selected
                for maximum information density and coverage. STRICT ADHERENCE TO ORIGINAL WORDING IS PARAMOUNT.
                Do not add your own language in the response, strictly respond with the summary only.
                """},
            {'role': 'user', 'content': user_prompt}
        ]
        
        try:
            logging.info(f"Attempting to generate summary using model: {self.model_name}")
            response = ollama.chat(
                model='llama3.2',
                messages=messages,
                options={'temperature': self.temperature}
            )

            if not response or 'message' not in response or 'content' not in response['message']:
                logging.error(f"Ollama API returned an unexpected response structure: {response}")
                raise RuntimeError("Failed to get a valid summary response from Ollama API.")

            summary_content = response['message']['content'].strip()
            if not summary_content:
                logging.warning("Ollama API returned an empty summary for the given document.")
                return ""
            
            logging.info("Summary generated successfully.")
            return summary_content

        except ollama.ResponseError as e:
            logging.exception(f"Ollama API error during summarization: {e}")
            raise RuntimeError(f"Ollama API communication error: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred during summarization: {e}")
            raise RuntimeError(f"An unexpected error occurred: {e}")