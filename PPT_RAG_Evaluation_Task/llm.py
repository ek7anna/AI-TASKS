from langchain_ollama import OllamaLLM

def get_llm(model_name="llama3.2"):
    return OllamaLLM(model=model_name)

def generate_answer(history, context, question, llm=None):
    if llm is None:
        llm = get_llm()
        
    prompt = f"""
You are an AI assistant answering questions about a PowerPoint document.
Use the conversation history to understand follow-up questions.
Answer ONLY using the provided context.
If the answer is not available in the context, reply:
"I couldn't find the answer in the provided document."
-----------------------------
Conversation History
-----------------------------
{history}
-----------------------------
Retrieved Context
-----------------------------
{context}
-----------------------------
Current Question
-----------------------------
{question}
Answer:
"""
    return llm.invoke(prompt)
