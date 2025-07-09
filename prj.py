import streamlit as sd
import requests

# Initialize chat history in session
if "chat_history" not in sd.session_state:
    sd.session_state.chat_history = []

# Sidebar history view
sd.sidebar.title("🕛 Chat History")
with sd.sidebar.expander("Past Narratives"):
    for idx, chat in enumerate(reversed(sd.session_state.chat_history)):
        sd.markdown(f"**{idx+1}. Genres:** {', '.join(chat['genre'])}")
        sd.markdown(f"**Prompt:** {chat['prompt']}")

# Constants
API_URL = "http://127.0.0.1:7860/chat"
MODEL_NAME = "llama3-70b-8192"

# Title and Inputs
sd.title("Inkpot ✒️")
genre = sd.multiselect("Genres:", ['Thriller', 'Romance', 'Fantasy', 'Self Help', 'Sci-Fi', 'Horror'])
prompt = sd.text_area("Story Arc / Chapter Concept:", placeholder="Enter your story 🖊️", height=100)
story_length = "moderate"

# Button Action
if sd.button("Narrate"):
    if prompt.strip():
        if not genre:
            sd.warning("Please select at least one genre.")
        else:
            try:
                payload = {
                    "model_name": MODEL_NAME,
                    "system_prompt": (
                        "You are a storytelling assistant. Based on the user's input, generate a complete short story "
                        "with a structured narrative: engaging opening, character development, plot twists, climax, and resolution. "
                        f"Ensure the writing reflects genre elements and matches the selected story length: {story_length}."
                    ),
                    "messages": [
                        f"Story idea: {prompt}. Genres: {', '.join(genre)}. Write a full story based on this arc."
                    ]
                }

                response = requests.post(API_URL, json=payload)

                if response.status_code == 200:
                    response_data = response.json()
                    if "error" in response_data:
                        sd.error(f"Model Error: {response_data['error']}")
                    else:
                        ai_response = [
                            message["content"]
                            for message in response_data.get("messages", [])
                        ]
                        if ai_response:
                            story = ai_response[-1]
                            sd.subheader("📖 Your Story")
                            sd.markdown(story)

                            # Save to session history
                            sd.session_state.chat_history.append({
                                "genre": genre,
                                "prompt": prompt,
                                "response": story
                            })
                        else:
                            sd.warning("No AI response found in the model output.")
                else:
                    sd.error(f"Request failed with status code {response.status_code}.")
            except Exception as e:
                sd.error(f"An error occurred: {e}")
    else:
        sd.warning("Please enter a story arc or chapter concept.")