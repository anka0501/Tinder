from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import vertexai
import os
from configuration import path, project_id, location

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] =  path
# initialize Vertex AI
vertexai.init(project=project_id, location=location)


def get_prompt(instruction, new_system_prompt):
    prompt_template =  new_system_prompt + instruction
    return prompt_template

instruction = "User: {user_input}"
system_prompt = """
Write a great pick-up line for a woman to use on a man, based on: {user_input}. 
Don't write about yourself, focus on the guy. Keep it to one sentence.
"""

class MessageGemini:
        
      def __init__(self, description):
        self.description = description
        self.model = None 

      def get_model(self):
        if self.model is None:
            self.model = VertexAI(
                      model_name="gemini-pro",
                      max_output_tokens=256,
                      temperature=0.9,
                      top_p=0.8,
                      top_k=2,
                      verbose=True,)
        return self.model

      def model_gemini(self):
        prompt = PromptTemplate(
                  input_variables=["user_input"], template=get_prompt(instruction, system_prompt)
                  )
        llm_chain = LLMChain(
                    llm=self.get_model(),
                    prompt=prompt,
                    verbose=True
                    )
        return llm_chain.predict(user_input=self.description)



