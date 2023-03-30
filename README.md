# YouTube Summaries

YouTube Summaries is a tool that uses OpenAI's Whisper and GPT summarization algorithms to create concise summaries of YouTube videos. This tool is built using Python 3.10 and Streamlit, and it requires an OpenAI API key and the youtube_dl and streamlit libraries to run.

## Installation

To use YouTube Summaries, you must first install Python 3.10 on your system. You can download Python from the official website: <https://www.python.org/downloads/>

Once you have Python installed, you can install the required packages using pip:

```sh
pip install openai yt-dlp streamlit
```

## Usage

To use YouTube Summaries, simply enter the URL of the YouTube video you want to summarize and your OpenAI API key into the input boxes on the app, and click the "Submit" button. The tool will download the audio from the video, transcribe it using the OpenAI transcription API, and summarize the transcription into 1000 words or less using the OpenAI GPT API. The resulting summary will be displayed in the app.

To run the tool, navigate to the root directory of the project and run the following command:

```sh
streamlit run app.py
```
