import os
import uuid
from typing import List, Dict, Any, Optional

class UserMessage:
    def __init__(self, content: str):
        self.content = content
        self.role = "user"

class LlmChat:
    def __init__(self, api_key: Optional[str] = None, session_id: Optional[str] = None, system_message: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "test-key")
        self.session_id = session_id or str(uuid.uuid4())
        self.system_message = system_message or "You are a helpful assistant."
        self.messages = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def with_model(self, provider: str, model: str):
        # Placeholder for model/provider selection
        self.provider = provider
        self.model = model
        return self

    async def chat(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        # Dummy implementation: echo last user message
        user_msg = next((m for m in reversed(messages) if m["role"] == "user"), {"content": ""})
        return {
            "role": "assistant",
            "content": f"[MOCK RESPONSE] Echo: {user_msg['content']}"
        }

    async def __call__(self, messages: List[Dict[str, str]]):
        return await self.chat(messages)
