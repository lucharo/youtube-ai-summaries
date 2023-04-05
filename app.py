import streamlit as st
import openai
import yt_dlp as youtube_dl
import re

def embed_youtube_video(video_id: str, width: int = 640, height: int = 360):
    """Embed a YouTube video in a Streamlit app."""
    youtube_embed_url = f"https://www.youtube.com/embed/{video_id}"
    iframe_html = f'<iframe src="{youtube_embed_url}" width="{width}" height="{height}" frameborder="0" allowfullscreen></iframe>'
    st.markdown(iframe_html, unsafe_allow_html=True)

def extract_video_id(youtube_url: str) -> str:
    """Extract the video ID from the YouTube URL."""
    regex = r"(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/(?:watch\?v=)?(.{11})"
    match = re.match(regex, youtube_url)
    if match:
        return match.group(1)
    return None

@st.cache
def get_transcript(video_id, extract_subs):
    # Fetch audio from YouTube URL
    ydl_opts = {
        "format": "bestaudio/best[ext=m4a]",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": f"{video_id}.%(ext)s"
    }
    if extract_subs:
        ydl_opts.update({"writesubtitles": True, "writeautomaticsub": True, "subtitlesformat": "vtt"})
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        duration = info["duration"]
        multiplier = 1 + duration // (60*5) + 1

    # Perform transcription or subtitle extraction
    if extract_subs:
        SUBTITLES_LANG = 'en-US'
        subtitle_file = f"{video_id}.{SUBTITLES_LANG}.vtt"
        with open(subtitle_file, 'r') as f:
            transcript = f.read()
            transcript = '\n'.join(transcript.split('\n')[3:])
            transcript = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\n', '', transcript)
            transcript = re.sub(r'\n\n', '\n', transcript)
            transcript = re.sub(r'\n', ' ', transcript)
            transcript = transcript.strip()
    else:
        with open(f"{video_id}.webm", "rb") as audio:
            transcript = openai.Audio.transcribe("whisper-1", audio)
            transcript = transcript["text"]

    return transcript, multiplier

def main():
    st.title("YouTube Audio Transcription and Summarization")

    st.subheader("This tool summarises youtube videos of whatever length into 300 words"
                 " for every 5 minutes of video. \n"
                 "> On average it takes a human 1 minute to read 300 words.")

    youtube_url = st.text_input(
        "Enter the YouTube URL",
        "https://www.youtube.com/watch?v=Dmpnrtey3YU"
    )

    extract_subs = st.checkbox("Extract subtitles from YouTube (if available)")

    video_id = extract_video_id(youtube_url)
    if video_id:
        embed_youtube_video(video_id)
    else:
        st.error("Invalid YouTube URL.")

    openai_key = st.text_input(
        "Enter the OpenAI API Key - get yours at [OpenAI docs](https://platform.openai.com/account/api-keys)",
        type="password"
    )
    openai.api_key = openai_key

    if st.button("Submit"):
        if not video_id:
            st.error("Invalid YouTube URL.")
        else:
            with st.spinner("Downloading audio from URL..."):
                transcript, multiplier = get_transcript(video_id, extract_subs)

            with st.expander("Expand to see transcript"):
                st.text_area('Transcript', transcript)

            # Summarize transcription using OpenAI GPT API
            with st.spinner("Summarising transcript..."):
                summary = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a helpful assistant that"
                                    " summarises youtube video transcripts into "
                                    f"{300 * multiplier} words or less."
                                    )
                            },
                            {"role": "user", "content": transcript}
                        ]
                )

            # Display summary
            st.write("Summary:", summary.choices[0]["message"]["content"])

if __name__ == "__main__":
    main()

