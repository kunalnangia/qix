import os
import json
from typing import Dict, List, Optional, Any
import openai

class LlmChat:
    """
    A simple wrapper for OpenAI's chat completion API.
    """
    
    def __init__(self, api_key: str, session_id: str, system_message: str):
        """
        Initialize the chat session.
        
        Args:
            api_key: OpenAI API key
            session_id: Unique identifier for the chat session
            system_message: Initial system message to set the behavior of the assistant
        """
        self.api_key = api_key
        self.session_id = session_id
        self.messages = [{"role": "system", "content": system_message}]
        self.model = "gpt-4"  # Default model
        
        # Set the API key for openai package
        openai.api_key = self.api_key
    
    def with_model(self, provider: str, model_name: str) -> 'LlmChat':
        """
        Set the model to use for completions.
        
        Args:
            provider: The provider of the model (e.g., 'openai')
            model_name: The name of the model to use (e.g., 'gpt-4')
            
        Returns:
            Self for method chaining
        """
        # For now, we only support OpenAI models
        if provider.lower() == "openai":
            self.model = model_name
        return self
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """
        Get a completion for the given prompt.
        
        Args:
            prompt: The user's message
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The assistant's response as a string
        """
        # Add user message to the conversation history
        self.messages.append({"role": "user", "content": prompt})
        
        try:
            # Call the OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=self.messages,
                **kwargs
            )
            
            # Extract the assistant's response
            assistant_message = response.choices[0].message
            assistant_content = assistant_message.content
            
            # Add assistant's response to the conversation history
            self.messages.append({"role": "assistant", "content": assistant_content})
            
            return assistant_content
            
        except Exception as e:
            # Log the error and re-raise
            print(f"Error in LLM completion: {str(e)}")
            raise
    
    async def complete_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Get a JSON response from the model.
        
        Args:
            prompt: The user's message
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The assistant's response parsed as JSON
        """
        # Add a system message to ensure JSON response
        json_system_message = {
            "role": "system",
            "content": "You are a helpful assistant that always responds with valid JSON."
        }
        
        # Create a new messages list with the JSON instruction
        json_messages = [json_system_message] + self.messages[1:] + [{"role": "user", "content": prompt}]
        
        try:
            # Call the OpenAI API with JSON response format
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=json_messages,
                **kwargs
            )
            
            # Extract the assistant's response
            assistant_content = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                return json.loads(assistant_content)
            except json.JSONDecodeError:
                # If the response isn't valid JSON, try to extract JSON from it
                import re
                json_match = re.search(r'```(?:json)?\n(.*?)\n```', assistant_content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                raise ValueError("Failed to parse JSON response from model")
                
        except Exception as e:
            # Log the error and re-raise
            print(f"Error in LLM JSON completion: {str(e)}")
            raise
