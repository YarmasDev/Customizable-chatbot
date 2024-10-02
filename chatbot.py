from groq import Groq
import streamlit as st

# Accede a la API key desde los secretos
api_key = st.secrets["API_KEY"]["key"]
client = Groq(api_key=api_key)


system_prompt = {
    "role": "system",
    "content": "You give precise answers, you adapt to the user."
}
bot_info = [system_prompt]

def get_ai_responses(messages):
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        max_tokens=1024,
        temperature=0,
        stream=True
    )
    response = "".join(chunk.choices[0].delta.content or "" for chunk in completion)
    return response

def manage_bot_info():
    # Handle the bot description and initialization
    bot_info_input = st.text_input("Describe your assistant", key="bot_info", placeholder="Write the description of the bot here")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # If bot_info_input is empty, use the system_prompt
    if not bot_info_input and not st.session_state.get("initialized", False):
        st.session_state["messages"].append(system_prompt)
        st.session_state["initialized"] = True
        st.session_state["last_bot_info"] = bot_info_input
    elif bot_info_input != st.session_state.get("last_bot_info", ""):
        # If bot info changes, update the system message
        if bot_info_input:
            st.session_state["messages"][0] = {"role": "system", "content": bot_info_input}
        else:
            st.session_state["messages"][0] = system_prompt
        st.session_state["last_bot_info"] = bot_info_input

def chat():
    st.title("Chat with your virtual assistant")
    st.write("Customize your chatbot so that it gives you the most appropriate answers for you")

    # Handle the bot info management
    manage_bot_info()

    # Function to handle user input
    def submit():
        user_input = st.session_state.user_input
        
        if user_input:  # Check if the user input is not empty
            st.session_state["messages"].append({"role": "user", "content": user_input})

            with st.spinner("Getting answer..."):
                ai_response = get_ai_responses(st.session_state["messages"])
                st.session_state["messages"].append({"role": "assistant", "content": ai_response})

            st.session_state.user_input = ""

    # Display chat history
    for message in st.session_state["messages"]:
        # Skip the system message (bot description) when displaying chat history
        if message["role"] != "system":
            role = "You" if message["role"] == "user" else "Bot"
            st.write(f"**{role}:** {message['content']}")
    
    # Input box for user messages
    st.text_input("Write your message", key="user_input", on_change=submit)

if __name__ == "__main__":
    chat()
