# YouTube AI Summaries

YouTube AI Summaries is a tool that uses OpenAI's Whisper and GPT summarization algorithms to create concise summaries of YouTube videos. This tool is built using Streamlit and it requires an OpenAI API key to run.

## Installation

```sh
pip install openai yt-dlp streamlit
```

## Usage

To use YouTube Summaries, simply enter the URL of the YouTube video you want to summarize and your OpenAI API key into the input boxes on the app, and click the "Submit" button. The tool will download the audio from the video, transcribe it using the OpenAI transcription API, and summarize the transcription into 1000 words or less using the OpenAI GPT API. The resulting summary will be displayed in the app.

To run the tool, navigate to the root directory of the project and run the following command:

```sh
streamlit run app.py
```
