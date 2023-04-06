import streamlit as st

st.markdown("# History 📜")

history = st.session_state.history
if len(history) > 0:
    history_options = [f"{entry['title']}" for entry in history]
    selected_history_entry = st.selectbox("Select a video:", history_options, index=len(history_options) - 1)
    entry_index = history_options.index(selected_history_entry)
    entry = history[entry_index]

    st.markdown(f'### {entry["title"]}')
    st.markdown(f"**URL:** {entry['url']}")
    with st.expander(f"Expand to see transcript"):
        st.write(entry["transcript"])
    st.markdown(f"**Summary:**")
    st.write(entry["summary"])
else:
    st.write("No history available.")

st.sidebar.title("Navigation")
st.sidebar.markdown(
    """
    **⚙️ App**: This is the main page where you can enter a YouTube URL, and the app will transcribe and summarize the video.

    **📜 History**: This page displays a list of your previous transcriptions and summaries. You can revisit them without having to rerun the entire process.
    """
)
st.sidebar.title("About")
st.sidebar.markdown(
    """
    This app has two main functionalities:

    1. **Transcription**: It transcribes the audio from a given YouTube video using OpenAI's Whisper.
    2. **Summarization**: It summarizes the transcribed text using OpenAI's GPT-3.5-turbo model.

    To use the app, simply provide a valid YouTube URL and select your preferred summary language. You can also view the history of your previous requests.
    """
)