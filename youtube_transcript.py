from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from youtube_transcript_api._errors import NoTranscriptFound
from crewai import Task, Agent, Crew
from langchain_groq import ChatGroq
from crewai_tools import tool


GROQ2 = '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'

count = 0
def groq_key():
    global count
    if count == 0:
        GROQ_API_KEY = "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" #console.groq.com API key
        count = 1
    elif count == 1:
        GROQ_API_KEY = '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'
        count = 0
    return GROQ_API_KEY


# Definir GROQ como LLM:
llm3 = ChatGroq(
    groq_api_key=groq_key(),
    model_name="llama3-70b-8192",
)


def split_text_into_chunks(text, max_tokens=6000):
    """Split text into chunks with a maximum number of tokens."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


@tool("Youtube Transcriptor")
def youtube_transcript(url, language='pt'):
    """
    Extract the YouTube URL for transcription.
    input: The URL of the YouTube video.
    output: texto of YouTube transcription
    language: The language code for the transcript (default is 'pt').
    """
    video_id = url.replace('https://www.youtube.com/watch?v=', '').strip()

    try:
        # Attempt to get the transcript in the specified language
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    except NoTranscriptFound:
        # If no transcript is found in the specified language, fall back to the generated language
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except NoTranscriptFound as e:
            return f"No transcript found for video {url}. Error: {str(e)}"

    # Combine the transcript texts into a single string
    full_text = '\n'.join([x['text'] for x in transcript])

    return full_text

transcritor = Agent(
    role="youtube transcriptor",
    goal="transcript the youtube video",
    backstory="He is dedicated to providing accurate and timely transcriptions for a variety of YouTube videos.",
    llm=llm3,
    memory=True,
    verbose=True,
)

transcrever = Task(
    description="Transcrever o vídeo do {url}",
    expected_output="the transcription of the video",
    agent=transcritor,
    tools=[youtube_transcript],
)


crew = Crew(
    agents=[transcritor],
    tasks=[transcrever, resumir],
    verbose=True,
)

def Transcription(prompt):
    return crew.kickoff(inputs={'url': prompt})

#print(result)
