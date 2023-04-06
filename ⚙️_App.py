import time
import streamlit as st
import openai

from functions import *

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

    st.sidebar.warning("⚠️ If the transcript is longer than 4097 tokens (roughly a 10-20 minute video) the summarization won't work as this is GPT-3.5-turbo's maximum context size 😢")

    with open('pages/sidebar.md', 'r') as sidebar_md:
        st.sidebar.markdown(sidebar_md.read())



    login()

