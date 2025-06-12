from pydantic import BaseModel, Field
from typing import Optional

class SummaryFormat(BaseModel):
    """
    Defines the structured format for an LLM-generated summary.

    This class helps ensure the LLM's output adheres to a predictable structure,
    making it easier to parse and use in downstream applications.

    Expected Format:
    {
        "title": "A concise and relevant title for the summary.",
        "definition": "Optional definition of the main topic.",
        "introduction": "An introductory paragraph setting the context.",
        "body": "The main content of the summary, covering key details.",
        "conclusion": "A concluding statement or summary of key takeaways."
    }
    """

    title: str = Field(
        description="A concise, descriptive, and relevant title for the summary. "
                    "This should capture the main essence of the summarized content."
    )

    definition: Optional[str] = Field(
        default=None,
        description="An optional, brief definition or explanation of the core topic "
                    "if applicable and useful for context. If no definition is needed, "
                    "output null or an empty string."
    )

    introduction: str = Field(
        description="An introductory paragraph that sets the stage for the summary. "
                    "It should provide necessary context and briefly outline what will be covered."
    )

    body: str = Field(
        description="The main content of the summary. This section should cover "
                    "all essential details, arguments, or information relevant to the topic. "
                    "Organize it logically and concisely."
    )

    conclusion: str = Field(
        description="A concluding paragraph that summarizes the key takeaways, "
                    "reiterates the main points, or offers a final thought. "
                    "It should provide a sense of closure to the summary."
    )