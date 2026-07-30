"""
memory.py - Conversational Memory Module

Provides helper classes and utility functions for managing multi-turn chat history
and context serialization for the PPT Semantic RAG Chatbot.
"""

from langchain_community.chat_message_histories import ChatMessageHistory

class MemoryManager:
    def __init__(self):
        self.chat_history = ChatMessageHistory()

    def get_formatted_history(self) -> str:
        history = ""
        for message in self.chat_history.messages:
            if message.type == "human":
                history += f"User: {message.content}\n"
            elif message.type == "ai":
                history += f"Assistant: {message.content}\n"
        return history

    def add_user_message(self, message: str):
        self.chat_history.add_user_message(message)

    def add_ai_message(self, message: str):
        self.chat_history.add_ai_message(message)

    def clear(self):
        self.chat_history.clear()
