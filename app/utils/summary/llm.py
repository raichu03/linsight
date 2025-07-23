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
**Do not mention or refer to the 'document,' 'text,' 'source,' or any similar term that indicates the information came from a provided source.**
"Please generate a comprehensive and meticulously structured summary from the provided text. Your summary should not only capture the essence of the content but also provide insightful details, demonstrating a deep understanding. **Do not refer to the original source text (e.g., avoid phrases like 'according to the document,' 'from the text provided,' 'the document states,' or 'this document covers'). Present the information as if it is a standalone piece.** Adhere strictly to the following hierarchical structure and guidelines:
---
### **1. Document Title**
* Craft a precise and highly informative title that encapsulates the core subject matter and primary focus. Consider using keywords from the text.

### **2. Introduction & Contextualization**
* **Topic & Significance:** Briefly introduce the main topic, explaining its overall significance or relevance within its broader field.
* **Purpose & Scope:** Clearly state the primary purpose of the original content and define the scope of the information it covers.
* **Key Questions/Objectives:** Identify and articulate any central questions, problems, or objectives that the original content aims to address or explore.
* **Main Arguments/Themes:** Provide a high-level overview of the most prominent arguments, themes, or concepts that will be elaborated upon in the subsequent sections.

### **3. Detailed Analysis & Elaboration**
* **Sectional Breakdown:** Divide the main body of the summary into logical, distinct sections, using descriptive subheadings that reflect the thematic organization of the original content.
* **In-depth Explanation of Key Points:** For each section, meticulously explain the core ideas, concepts, and findings. Go beyond mere listing; provide sufficient detail to convey a thorough understanding.
* **Supporting Evidence & Examples:** Integrate specific, concise examples, data points, or direct references from the original text to substantiate explanations. (e.g., "Critical factor 'X' is highlighted, with [specific example/data] illustrating its impact.")
* **Relationships & Nuances:** Explicitly identify and explain relationships between ideas, such as cause-and-effect, comparisons, contrasts, or problem-solution frameworks presented. Unpack any nuances or complexities in the arguments.
* **Methodology/Approach (If Applicable):** If the original content describes a research study, analysis, or specific methodology, briefly explain its key components and their relevance to the findings.

### **4. Concluding Insights & Implications**
* **Synthesis of Core Takeaways:** Concisely synthesize the most critical insights, conclusions, or major findings presented. What are the ultimate messages conveyed?
* **Unresolved Issues/Future Directions:** Discuss any questions that remain unanswered, limitations of the content's scope, or implications for future research, discussion, or action as suggested or implied.
* **Overall Significance/Impact:** Briefly reiterate the overall significance or potential impact of the content.

---

### **Additional Guidelines for Excellence:**
* **Tone & Style:** Maintain a highly professional, objective, and academic tone. Ensure the language is precise, clear, and avoids ambiguity.
* **Clarity & Accessibility:** While providing depth, ensure complex ideas are presented in an accessible manner without sacrificing accuracy. Simplify technical jargon where appropriate, always retaining the original meaning.
* **Conciseness with Detail:** Strive for a balance between conciseness and comprehensive detail. Every sentence should contribute meaningfully to the summary.
* **Adherence to Original Intent:** Your summary must accurately reflect the original content's arguments, emphasis, and perspective without introducing external interpretations or biases.
* **Crucially, do not mention or refer to the 'document,' 'text,' 'source,' or any similar term that indicates the information came from a provided source. Write as if the summary itself is the primary source of the information.**"
---

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
        full_response_content = ""
        
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
                        full_response_content += partial_content
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