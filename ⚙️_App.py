import time
import streamlit as st
import openai

from functions import *

def display_bmc_button():
    st.write(
        """
        <style>
            .bmc-container {
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 1rem;
                }
            .github-logo {
                width: 40px;
                height: 40px;
                margin-left: 1rem;
            }
        </style>
        <div class="bmc-container">
            <a href="https://www.buymeacoffee.com/lucharo" target="_blank" title="Donate to support the project">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"  alt="Buy Me A Coffee" width="200">
            </a>
            <a href="https://github.com/lucharo/youtube-ai-summaries" target="_blank" title="Check out the GitHub repository">
                <svg class="github-logo" viewBox="0 0 16 16" version="1.1" width="30" height="30" aria-hidden="true">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>            
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

def login():
    if 'openai_key' not in st.session_state or 'api_key_valid' not in st.session_state:
        st.session_state.api_key_valid = False

    if not st.session_state.api_key_valid:
        st.header("Login")
        openai_key = st.text_input(
            "Enter the OpenAI API Key - get yours at [OpenAI docs](https://platform.openai.com/account/api-keys)",
            type="password"
        )

        if st.button("Validate API Key"):
            if validate_api_key(openai_key):
                st.session_state.openai_key = openai_key
                st.session_state.api_key_valid = True
                st.success("API key is valid. Loading app...")
                time.sleep(1)
                st.experimental_rerun()
            else:
                st.error("Invalid API key. Please try again.")
    else:
        openai.api_key = st.session_state.openai_key
        app()

def app():
    # display_auth_banner()
    st.title("YouTube Audio Transcription and Summarization")

    st.subheader("This tool summarises youtube videos of whatever length into 300 words"
                 " for every 5 minutes of video. \n"
                 "> On average it takes a human 1 minute to read 300 words.")

    example_videos = {
        "English example": "https://www.youtube.com/watch?v=Dmpnrtey3YU",
        "French example": "https://www.youtube.com/watch?v=KD3n7f3HnbE",
        "Spanish long example": "https://www.youtube.com/watch?v=BjzxheRM7jk"
    }
    
    cols = st.columns([1,1,5])
    for i, (name, url) in enumerate(example_videos.items()):
        if cols[i].button(name):
            st.session_state.example_url = url

    if "example_url" in st.session_state:
        youtube_url = st.text_input("Enter the YouTube URL", st.session_state.example_url)
    else:
        youtube_url = st.text_input("Enter the YouTube video URL")

    summary_language = st.radio(
        "Select summary language", 
        ("English", "Video's original language"),
        horizontal= True
        )

    video_id = extract_video_id(youtube_url)
    if video_id:
        embed_youtube_video(video_id)
    else:
        st.error("Invalid YouTube URL.")

    if st.button("Submit"):
        if not video_id:
            st.error("Invalid YouTube URL.")
        else:
            transcript, multiplier, title = get_transcript(video_id)

            token_count = count_tokens(transcript)
            st.write(f"Token count: {token_count}")

            with st.expander("Expand to see transcript"):
                st.text_area('Transcript', transcript)

            if token_count > 4000:
                st.error('The transcript has more than 4000 tokens and cannot be summarized.')
                summary = "The transcript has more than 4000 tokens and cannot be summarized.'"
            else:
                # Summarize transcription using OpenAI GPT API
                with st.spinner("Summarising transcript..."):
                    translation_instruction = 'in their original language' if summary_language == "Video's original language" else "in english"
                    summary = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are a helpful assistant that"
                                        " summarises youtube video transcripts into "
                                        f"{300 * (1 + multiplier)} words or less {translation_instruction} "
                                        )
                                },
                                {"role": "user", "content": transcript}
                            ]
                    )
                    summary = summary.choices[0]["message"]["content"]

                    # Display summary
                    st.write("Summary:", summary)

            # store output in session_state 
            st.session_state.history.append(
                {
                    "url": youtube_url,
                    "title": title,
                    "transcript": transcript,
                    "summary": summary,
                }
            )

if __name__ == "__main__":
    st.set_page_config(
        page_title="YouTube Audio Transcription and Summarization",
        layout="wide"
        )
    
    if 'history' not in st.session_state:
        st.session_state.history = []

    with st.sidebar:
        display_bmc_button()

    with open('pages/sidebar.md', 'r') as sidebar_md:
        st.sidebar.markdown(sidebar_md.read())

    st.sidebar.warning("⚠️ If the transcript is longer than 4097 tokens (roughly a 10-20 minute video) the summarization won't work as this is GPT-3.5-turbo's maximum context size 😢")

    login()

