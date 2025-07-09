from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
import traceback

# Set API keys
groq_api_key = "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"
os.environ["TAVILY_API_KEY"] = "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"

# Supported model names
MODEL_NAMES = ["llama3-70b-8192"]

# Initialize tools
tool_tavily = TavilySearchResults(max_results=2)
tools = [tool_tavily]

# Create FastAPI instance
app = FastAPI(title='LangGraph AI Agent')

# Request body model
class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]

# API endpoint
@app.post("/chat")
def chat_endpoint(request: RequestState):
    try:
        if request.model_name not in MODEL_NAMES:
            return {"error": "Invalid model name. Please select a valid model."}

        llm = ChatGroq(groq_api_key=groq_api_key, model_name=request.model_name)
        agent = create_react_agent(llm, tools=tools)

        message_history = [{"role": "system", "content": request.system_prompt}]
        message_history += [{"role": "user", "content": msg} for msg in request.messages]

        state = {"messages": message_history}
        result = agent.invoke(state)

        # Extract assistant messages for frontend
        assistant_messages = [
            {"role": "assistant", "content": msg.content}
            for msg in result["messages"]
            if isinstance(msg, AIMessage)
        ]
        return {"messages": assistant_messages}

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

# Run locally
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=7860)