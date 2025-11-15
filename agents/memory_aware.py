from autogen_agentchat.agents import AssistantAgent

class MemoryAwareAgent(AssistantAgent):
    def __init__(self, memory, store_messages=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = memory
        self.store_messages = store_messages  # Control whether to store messages

    async def run(self, task, session_id="default", cancellation_token=None):
        # Only load history if we're storing messages (skip for intent agent)
        if self.store_messages:
            # Load conversation history from Redis
            history = await self.memory.get_history(session_id)
            
            # Build context from history
            context_messages = []
            for msg in history:
                sender = msg.get("sender", "user")
                content = msg.get("message", "")
                context_messages.append(f"{sender}: {content}")
            
            # Prepend history context to the task
            if context_messages:
                history_context = "\n".join(context_messages)
                task_with_context = f"Session ID: {session_id}\n\nPrevious conversation:\n{history_context}\n\nCurrent request: {task}"
            else:
                task_with_context = f"Session ID: {session_id}\n\nCurrent request: {task}"
        else:
            # No history for agents with store_messages=False (like intent agent)
            task_with_context = task
        
        # Let the model generate its response with history context
        response = await super().run(task=task_with_context, cancellation_token=cancellation_token)
        
        # Only log agent response if store_messages is True
        if self.store_messages and response.messages:
            last_message = response.messages[-1]
            if hasattr(last_message, 'content'):
                content = last_message.content
                # Handle both string content and structured output
                if hasattr(content, 'model_dump'):
                    content_str = str(content.model_dump())
                elif hasattr(content, '__dict__'):
                    content_str = str(content.__dict__)
                else:
                    content_str = str(content) if content else ""
                await self.memory.add_message(session_id, self.name, content_str)
        
        return response

    async def run_stream(self, task, session_id="default"):
        # Only load history if we're storing messages
        if self.store_messages:
            # Load conversation history from Redis
            history = await self.memory.get_history(session_id)
            
            # Build context from history
            context_messages = []
            for msg in history:
                sender = msg.get("sender", "user")
                content = msg.get("message", "")
                context_messages.append(f"{sender}: {content}")
            
            # Prepend history context to the task
            if context_messages:
                history_context = "\n".join(context_messages)
                task_with_context = f"Previous conversation:\n{history_context}\n\nCurrent request: {task}"
            else:
                task_with_context = task
        else:
            task_with_context = task
        
        # Let the model generate its response with history
        async for response in super().run_stream(task=task_with_context):
            if self.store_messages and response.content:
                await self.memory.add_message(session_id, self.name, response.content)
            yield response