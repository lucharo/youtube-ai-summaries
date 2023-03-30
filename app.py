import streamlit as st
import openai
import yt_dlp as youtube_dl
import re

# Define Streamlit app
def app():

    st.title("YouTube Audio Transcription and Summarization")

    st.subheader("This tool summarises youtube videos of whatever length into 300 words  "
    "for every 5 minutes of video. \n"
    "> On average it takes a human 1 minute to read 300 words.")

    # Input box for YouTube URL
    youtube_url = st.text_input(
        "Enter the YouTube URL", 
        "https://www.youtube.com/watch?v=Dmpnrtey3YU"
    )

    # Checkbox for subtitle extraction
    extract_subs = st.checkbox("Extract subtitles from YouTube (if available)")

    video_id = youtube_url.replace('https://www.youtube.com/watch?v=', '')

    # Input box for OpenAI API key
    openai_key = st.text_input(
        "Enter the OpenAI API Key - get yours at [OpenAI docs](https://platform.openai.com/account/api-keys)",
        "sk-...",
        type = "password"
    )
    openai.api_key = openai_key

    # Submit button
    if st.button("Submit"):
        with st.spinner("Downloading audio from URL..."):
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
                ydl.download([youtube_url])
                info = ydl.extract_info(youtube_url, download=False)
                duration = info["duration"]
                # below is the multiplier, being 1 minute (as a min) + 
                # the number of 5 minutes contained in the video duration
                multiplier = 1 + duration // (60*5) + 1


        # Perform transcription or subtitle extraction
        if extract_subs:
            SUBTITLES_LANG = 'en-US'
            # Show buffering symbol while extracting subtitles
            with st.spinner("Extracting subtitles..."):
                subtitle_file = f"{video_id}.{SUBTITLES_LANG}.vtt"
                with open(subtitle_file, 'r') as f:
                    transcript = f.read()
                    # manual clean up

                    # Parse the captions text without timestamps
                    # Remove the first three lines
                    transcript = '\n'.join(transcript.split('\n')[3:])
                    transcript = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\n', '', transcript)
                    transcript = re.sub(r'\n\n', '\n', transcript) 
                    transcript = re.sub(r'\n', ' ', transcript)
                    transcript = transcript.strip()
        else:
            # Transcribe audio using OpenAI transcription API
            with st.spinner("Transcribing audio..."):
                with open(f"{video_id}.webm", "rb") as audio:
                    transcript = openai.Audio.transcribe("whisper-1", audio)
                    transcript = transcript["text"]

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
                                f"{300*multiplier} words or less."
                                )
                        },
                        {"role": "user", "content": transcript}
                    ]
            )

        # Display summary
        st.write("Summary:", summary.choices[0]["message"]["content"])

# Run Streamlit app
app()
