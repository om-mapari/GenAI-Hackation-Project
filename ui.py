import streamlit as st
import setenv
import backend

def responseFromKB(prompt,input_text):
    # kBResponse = "my-response"
    kBResponse = backend.driver_function(prompt,input_text)
    return kBResponse

# Title and Sidebar
st.set_page_config(page_title="Confluece GPT", page_icon="")
st.title("Team Beyond Human")
st.sidebar.title("Options")

# Sidebar for additional options
if st.sidebar.button("Clear Chat History"):
    # Clear session state memory
    st.session_state.chat_history = []
    st.rerun()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
st.write("### ConflueceGPT")

for message in st.session_state.chat_history:
    with st.chat_message(message['role']):
        st.markdown(message['text'])

# User input
input_text = st.chat_input("Chat with Confluece database Bot here")

def formatConversationHistory():
    # Format conversation history by combining the role and text
    conversation_history = ""
    for message in st.session_state.chat_history:
        role = message.get("role")
        text = message.get("text")
        conversation_history += f"{role.capitalize()}: {text}\n"

    return conversation_history

def setInitialData():
    # Read the content from the input text file
    with open("file.txt", 'r') as file:
        data = file.read()

    # Format the conversation history
    conversation_history = formatConversationHistory()

    # Construct the enhanced prompt
    prompt = f"""
You are Confluence GPT, an assistant dedicated to answering questions based strictly on the data provided below. Your role is to assist users by referencing only the information in the data, and you are not permitted to provide any external knowledge or answers beyond what is available in the provided content.

Key Guidelines:
1. Respond **only** with information found in the provided data. If the data does not contain an answer to a question, kindly inform the user that you can only provide responses based on the available Confluence documentation.
2. Do **not** attempt to provide interpretations, guesses, or additional context not explicitly included in the data.
3. Maintain the history of the conversation. If a question refers to prior interactions in the conversation, you must answer based on the information already discussed or available in the Confluence content. Keep your responses concise and directly related to the user's query.
4. Do **not** repeat the data or the conversation history unless explicitly requested to do so. Simply focus on providing relevant, data-based answers.

Please remember:
- Any questions or comments outside the scope of the data should be redirected to indicate that only answers based on the available documentation will be provided.
- Maintain a professional and neutral tone at all times.

Below is the available confluence data:

{data}

Conversation history so far:

{conversation_history}
"""

    # Return the constructed prompt for further use
    return prompt

# Process user input
if input_text:
    with st.chat_message("user"):
        st.markdown(input_text)
    st.session_state.chat_history.append({
        "role": "user",
        "text": input_text
    })
    prompt = setInitialData()
   
    chat_response = responseFromKB(prompt,input_text)  # Replace with actual response logic
    with st.chat_message("assistant"):
        st.markdown(chat_response)
    st.session_state.chat_history.append({
        "role": "assistant",
        "text": chat_response
    })