import os
import traceback
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


MODEL_NAMES = ["llama-3.3-70b-versatile"]
GROQ_API_KEY = ""

app = FastAPI(title="LangGraph AI Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]


def get_llm(model_name: str) -> ChatGroq:
    groq_api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError(
            "Missing GROQ_API_KEY. Add it to your .env file or set it in your terminal before starting the backend."
        )
    return ChatGroq(groq_api_key=groq_api_key, model_name=model_name)


@app.get("/")
def healthcheck():
    return {"status": "ok"}


@app.post("/chat")
def chat_endpoint(request: RequestState):
    try:
        if request.model_name not in MODEL_NAMES:
            return {"error": "Invalid model name. Please select a valid model."}

        llm = get_llm(request.model_name)
        agent = create_react_agent(llm, tools=[])

        message_history = [{"role": "system", "content": request.system_prompt}]
        message_history += [{"role": "user", "content": msg} for msg in request.messages]

        result = agent.invoke({"messages": message_history})
        assistant_messages = [
            {"role": "assistant", "content": msg.content}
            for msg in result["messages"]
            if isinstance(msg, AIMessage)
        ]
        return {"messages": assistant_messages}

    except Exception as exc:
        traceback.print_exc()
        return {"error": str(exc)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=7860)
