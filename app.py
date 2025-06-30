import streamlit as st
from dotenv import load_dotenv
import os
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from google.generativeai import types

avatars = {
    "assistant": r"c:\Users\sawhn\Downloads\WhatsApp Image 2025-06-30 at 12.19.13 AM.jpeg",
    "user": r"c:\Users\sawhn\Downloads\pngtree-man-avatar-isolated-png-image_13022170.png"
}

def clear_chat_history():
    st.session_state.messages = [{
        "role": "assistant",
        "content": "How may I assist you today?",
        "image": None
    }]

def generateresponse(input_text):
    try:
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        system_prompt = """
        # INSTRUCTIONS
        You are a user-friendly chatbot,give answers according to the question given by the user,
        if an image is given in the input then tell accordingly about the image.

        # OUTPUT
        Here is the Information you have asked for
        """

        contents = [system_prompt, input_text]
        if "image" in st.session_state:
            contents.append(st.session_state.image)
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(
        contents=contents,
        stream=True
        )


        return response

    except Exception as ex:
        st.error(f"Gemini API Error: {ex}")
        return "error"

def main():
    st.set_page_config(page_title='TaskGenie', initial_sidebar_state='auto')
    st.markdown("<h2 style='text-align:center;color:#3184a0;'>TaskGenie</h2>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* Chat message text size */
    .stChatMessageContent {
        font-size: 1.3rem !important;
        line-height: 1.6 !important;
    }
    /* Assistant name or header font (optional) */
    h2 {
        font-size: 2.2rem !important;
    }
    </style>
""", unsafe_allow_html=True)


    with st.sidebar:
        st.image(r"c:\Users\sawhn\Downloads\istockphoto-1445426863-612x612.jpg")
        st.button("Clear chat history", on_click=clear_chat_history)

        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image_bytes = Image.open(uploaded_file)
            st.session_state.image = {
                "mime_type": uploaded_file.type,
                "data": uploaded_file.getvalue()
            }
            st.image(image_bytes, caption="Uploaded Image", use_container_width=True)

    if "messages" not in st.session_state:
        clear_chat_history()

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=avatars[message["role"]]):
            st.write(message["content"])
            if message["role"] == "assistant" and message["image"]:
                st.image(message["image"])

    prompt = st.chat_input("Enter your instruction...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "image": None})
        with st.chat_message("user", avatar=avatars["user"]):
            st.write(prompt)

        with st.chat_message("assistant", avatar=avatars["assistant"]):
            with st.spinner("Thinking..."):
                response = generateresponse(prompt)

                if response == "error":
                    return  # Stop further execution on error

                placeholder = st.empty()
                full_response = ""
                avatar_image = None

                try:
                    for part in response:
                        if hasattr(part, "candidates"):
                            for inner_part in part.candidates[0].content.parts:
                                if hasattr(inner_part, "text") and inner_part.text:
                                    full_response += inner_part.text
                                    placeholder.markdown(full_response, unsafe_allow_html=True)
                                elif hasattr(inner_part, "inline_data") and inner_part.inline_data:
                                    avatar_image = Image.open(BytesIO(inner_part.inline_data.data))
                                    st.image(avatar_image)
                except Exception as ex:
                    st.error(f"Error while parsing response: {ex}")
                    return

                # Store assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "image": avatar_image
                })

# ✅ Call main
if __name__ == "__main__":
    main()
