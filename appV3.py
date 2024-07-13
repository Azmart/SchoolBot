import openai
import streamlit as st
import time
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

#Add custom CSS for hiding icons
hide_github_icon="""
#GithubIcon {
    visibility: hidden
}
"""

st.markdown(hide_github_icon, unsafe_allow_html=True)


# Set page configuration
st.set_page_config(page_title="मेरो ए.आई शिक्षक", page_icon=":speech_balloon:")

# Load secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]



# Authentication setup
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Check authentication status
name, authentication_status, username = authenticator.login('main')

if authentication_status:
    st.sidebar.title(f"Welcome {name}")

    assistant_id = "asst_9CJ6Gbg8SSCtca5i6vn2lW6l"
    client = openai

    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    if st.sidebar.button("Exit Chat"):
        st.session_state.messages = []  # Clear the chat history
        st.session_state.start_chat = False  # Reset the chat state
        st.session_state.thread_id = None
        
    

    st.title("मेरो ए.आई शिक्षक")
    st.write("Namaskar🙏")

    if st.button("Start Chat"):
        st.session_state.start_chat = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    if st.session_state.start_chat:
        if "openai_model" not in st.session_state:
            st.session_state.openai_model = "gpt-3.5-turbo-0125"
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input(""):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )

            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions="You are a teacher in Nepal who 1) understands all English, Nepali, Romanised Nepali as well as mix of those languages, 2) have knowledge of the coursebook and related materials used in the school level education in Nepal. you can find that at https://moecdc.gov.np/np/text-books 3) will help the students with questions they have and teach them in a simple easy to understand tone 4) before start of conversation ask the student the grade they are in and subject to learn at the beginning to adjust your knowledge base accordingly (नमस्ते! तपाईं आज कति कक्षाको कुन विषय पढ्न चाहनुहुन्छ? 5) help the students understand the questions they have. instead of simply providing the answer u will explain the question, reasoning behind the steps and then provide answer explaining the flow 6) if the student wants to switch to a different subject and/or grade, they can switch using /switch command eg: /switch 8, maths which means grade 8 & subject maths. 7) you only support english, nepali, maths, science and सामाजिक subjects for now. 8) You will converse in pure Nepali language by default even if the user's starts the conversation in english or the questions asked are in english unless i) the user explicitly asks to talk & explain in english ii) the subject of learning is english iii) can use romanised nepali if the user asks to do so 9) if the user asks question unrelated to the the topics in secondary school eg: how does X Elite chips work? how to use photoshop? etc, please reply in pure nepali language with a polite refusal message, that questions are limited within curriculum."
            )

            while run.status != 'completed':
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # Process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
                with st.chat_message("assistant"):
                    st.markdown(message.content[0].text.value)

    else:
        st.write("Click 'Start Chat' to begin.")

elif authentication_status == False:
    st.error('Username/password is incorrect')

elif authentication_status == None:
    st.warning('Please enter your username and password')

# Allow the user to logout
authenticator.logout('Logout', 'sidebar')
