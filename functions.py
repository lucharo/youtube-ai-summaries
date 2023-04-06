
import os
import re
import tempfile
import pydub
from pydub.silence import split_on_silence
import openai
import streamlit as st
import yt_dlp as youtube_dl


def split_audio(audio_file, max_file_size):
    audio = pydub.AudioSegment.from_file(audio_file)
    duration = len(audio)
    max_duration = max_file_size * (duration / os.path.getsize(audio_file))
    num_chunks = int(duration // max_duration + 1)

    audio_chunks = split_on_silence(audio, min_silence_len=int(max_duration), silence_thresh=-50, keep_silence=100)
    
    # Ensure the number of chunks is not greater than num_chunks
    print(0)
    while len(audio_chunks) > num_chunks:
        max_duration += max_duration // 10
        audio_chunks = split_on_silence(audio, min_silence_len=int(max_duration), silence_thresh=-50, keep_silence=100)

    print(2)

    return audio_chunks

def concatenate_transcripts(transcript_list):
    transcript = " ".join(transcript_list)
    return transcript.strip()

def transcribe_audio_file(audio_file):
    MAX_FILE_SIZE = 25 * 1024 * 1024
    file_size = os.path.getsize(audio_file)

    if file_size > MAX_FILE_SIZE:
        audio_chunks = split_audio(audio_file, MAX_FILE_SIZE)
        transcript_list = []
        progress_bar = st.progress(0)
        num_chunks = len(audio_chunks)
        for index, chunk in enumerate(audio_chunks):
            print(index)
            with tempfile.NamedTemporaryFile(suffix=".webm") as temp_audio:
                chunk.export(temp_audio.name, format="webm")
                with open(temp_audio.name, "rb") as temp_audio_file:
                    transcript_chunk = openai.Audio.transcribe(
                        "whisper-1", 
                        temp_audio_file
                        )
                    transcript_list.append(transcript_chunk["text"])

            progress_bar.progress((index + 1) / num_chunks)

        transcript = concatenate_transcripts(transcript_list)
    else:
        with open(audio_file, "rb") as audio:
            transcript = openai.Audio.transcribe("whisper-1", audio)
            transcript = transcript["text"]

    return transcript

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

@st.cache_data(show_spinner=False)
def get_transcript(video_id):
    # Fetch audio from YouTube URL
    ydl_opts = {
        "format": "bestaudio/best[ext=m4a]",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": f"{video_id}.%(ext)s"
    }
    with st.spinner("Downloading audio from URL..."):
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            duration = info["duration"]
            multiplier = 1 + duration // (60*5) + 1
            title = info["title"]

    # Perform transcription or subtitle extraction
    with st.spinner('Transcribing audio...'):
        with open(f"{video_id}.webm", "rb") as audio:
            transcript = transcribe_audio_file(f"{video_id}.webm")

    return transcript, multiplier, title

# def display_auth_banner():
#     if st.session_state.api_key_valid:
#         st.markdown(
#             """
#             <head>
#             <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
#             </head>
#             <div style="background-color: #4caf50; padding: 10px; border-radius: 5px;">
#             <p style="color: white; font-weight: bold; margin: 0;">
#             <i class="material-icons" style="vertical-align: middle; font-size: 18px;">check_circle</i>
#             Authenticated
#             </p>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )


def validate_api_key(api_key: str) -> bool:
    try:
        openai.api_key = api_key
        openai.Engine.list()
        return True
    except:
        return False