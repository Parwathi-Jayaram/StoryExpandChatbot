import os

import requests
import streamlit as st


API_URL = os.getenv("STORY_API_URL", "http://127.0.0.1:7860/chat")
MODEL_NAME = "llama-3.3-70b-versatile"
GENRES = ["Thriller", "Romance", "Fantasy", "Self Help", "Sci-Fi", "Horror"]


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


st.sidebar.title("Chat History")
with st.sidebar.expander("Past Narratives", expanded=False):
    if st.session_state.chat_history:
        for idx, chat in enumerate(reversed(st.session_state.chat_history), start=1):
            st.markdown(f"**{idx}. Genres:** {', '.join(chat['genre'])}")
            st.markdown(f"**Prompt:** {chat['prompt']}")
    else:
        st.caption("Your generated stories will appear here.")


st.title("Inkpot")
genre = st.multiselect("Genres:", GENRES)
prompt = st.text_area(
    "Story Arc / Chapter Concept:",
    placeholder="Enter your story idea",
    height=120,
)
story_length = "moderate"


if st.button("Narrate", type="primary"):
    if not prompt.strip():
        st.warning("Please enter a story arc or chapter concept.")
    elif not genre:
        st.warning("Please select at least one genre.")
    else:
        payload = {
            "model_name": MODEL_NAME,
            "system_prompt": (
                "You are a storytelling assistant. Based on the user's input, generate a complete short story "
                "with a structured narrative: engaging opening, character development, plot twists, climax, and "
                f"resolution. Ensure the writing reflects genre elements and matches the selected story length: {story_length}."
            ),
            "messages": [
                f"Story idea: {prompt}. Genres: {', '.join(genre)}. Write a full story based on this arc."
            ],
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not reach the backend API at "
                f"`{API_URL}`. Start `prj.py` separately before generating a story."
            )
        except requests.exceptions.Timeout:
            st.error("The backend took too long to respond. Please try again.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")
        else:
            if "error" in response_data:
                st.error(f"Model Error: {response_data['error']}")
            else:
                ai_response = [
                    message["content"]
                    for message in response_data.get("messages", [])
                    if message.get("role") == "assistant"
                ]

                if ai_response:
                    story = ai_response[-1]
                    st.subheader("Your Story")
                    st.markdown(story)
                    st.session_state.chat_history.append(
                        {
                            "genre": genre,
                            "prompt": prompt,
                            "response": story,
                        }
                    )
                else:
                    st.warning("No AI response found in the model output.")
