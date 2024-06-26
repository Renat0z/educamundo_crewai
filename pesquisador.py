import os
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from youtube_transcript_api._errors import NoTranscriptFound
from crewai import Task, Agent, Crew
from langchain_groq import ChatGroq
from crewai_tools import tool, SerperDevTool


os.environ["SERPER_API_KEY"] = "309cd7ec37d5cbb72aaea4d165a3ced705e4d12a" # serper.dev API key

GROQ_API_KEY = "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" #console.groq.com API key

# Definir GROQ como LLM:
llm3 = ChatGroq(
    groq_api_key=GROQ_API_KEY,
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

search_tool = SerperDevTool()

pesquisador = Agent(
    role="pesquisador de nicho",
    goal="""
        Seu principal objetivo é definir um nicho de mercado claro e preciso, com uma compreensão profunda das necessidades e preferências do público-alvo, através de análises de mercado, definição de objetivos e desenvolvimento de estratégias de marketing.
        """,
    backstory="""
            Atue como um Marketing Strategist com mais de 10 anos de carreira com prêmios de "Melhor Estratégia de Marketing" 
            e "Melhor Análise de Mercado". Um profissional com experiência em definição de nichos de mercado, desenvolvimento 
            de estratégias de marketing e análise de mercado. Sua função é definir um nicho de mercado claro e preciso, 
            com uma compreensão profunda das necessidades e preferências do público-alvo.

            Suas características são:

            DISC: D (detalhista) e I (inovador)
            Eneagrama: 7 (investigador)
            MBTI: INTJ (liderança e estratégia)
            """,
    llm=llm3,
    verbose=True,
)

pesquisa_nicho = Task(
    description="""
    - Realizar uma pesquisa inicial sobre o nicho para entender as necessidades e preferências do público-alvo. O tema é: "{topic}"
    - Critérios de qualidade, requisitos: A pesquisa deve ser realizada com base em fontes confiáveis e atualizadas, e deve abranger todas as áreas relevantes do nicho.
    """,
    expected_output="""
            Lista de:
            1. **Público-alvo:**
            2. **Necessidades e preferências:**
            3. **Tendências:**
            4. **Estatísticas:**
            5. **Principais conclusões:**
            """,
    agent=pesquisador,
    tools=[search_tool],
)

crew = Crew(
    agents=[pesquisador],
    tasks=[pesquisa_nicho],
    verbose=True,
)

def Pesquisa(prompt):
    return crew.kickoff(inputs={'topic': prompt})

#print(result)