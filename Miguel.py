import os
import time

from crewai_tools.tools.scrape_website_tool.scrape_website_tool import ScrapeWebsiteTool
from crewai_tools import SerperDevTool, WebsiteSearchTool, FileReadTool, PDFSearchTool, YoutubeVideoSearchTool
from dotenv import load_dotenv
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
#from textwrap import dedent


# Warning control
import warnings
warnings.filterwarnings('ignore')


# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração das chaves de API (substitua com suas chaves reais)
openai_api_key = os.getenv("sk-proj-X1ZrCAAJ6RS7AJfpx5yrT3BlbkFJWzaLgJkfHUvpMlOA3T2G")     ### CRIADA POR DECO EM 02/07/24 ###
groq_api_key = os.getenv("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")       ### CRIADA POR DECO EM 02/07/24 ###
serper_api_key = os.getenv("81de71363a8367f283b39b267cc4d29b3715712b")                     ### CRIADA POR DECO EM 02/07/24 ###                          

gpt3_llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)
gpt4o_llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key)
llama3_70b = ChatGroq(model="llama3-70b-8192", api_key=groq_api_key)
llama3_8b = ChatGroq(model="llama3-8b-8192", api_key=groq_api_key)

serper = SerperDevTool(api_key=serper_api_key)
scrape = ScrapeWebsiteTool()
search = WebsiteSearchTool()
read = FileReadTool()
pdfread = PDFSearchTool()
ytread = YoutubeVideoSearchTool()


########### AGENTES MIGUEL ########

buscador = Agent(
    role = "Investigador",
    goal = "Extrair e analisar o conteúdo de um arquivo de texto em {url}, PDF ou a transcrição de vídeo "
           "e extrair informações relevantes sobre {topic} para embasar a criação de "
           "roteiros de vídeoaulas.",
    backstory = "Sua função é ser um Pesquisador de Conteúdo. "
                "Você é um pesquisador dedicado, responsável por analisar arquivos de "
                "texto, PDF ou transcrições de vídeos detalhadas sobre {topic} para "
                "apoiar a criação de roteiro de vídeoaulas. Sua pesquisa é fundamental "
                "para garantir que o conteúdo dos roteiros seja preciso e atualizado.",
    verbose=True,
    tools=[scrape, read],
    max_rpm=2,
    llm=llama3_8b,
    allow_delegation=False
)


planejador = Agent(
    role = "Planejador Roteirista",
    goal = "Elaborar planos de roteiros envolventes para vídeoaulas sobre {topic} com "
           "base nas informações extraídas de um arquivo de texto, PDF ou transcrição "
           "de vídeo.",
    backstory = "Sua função é ser um Planejador de Roteiros de Vídeos."
                "Você é um planejador especializado em criar esboços detalhados para "
                "roteiros de vídeoaulas."
                "Seu trabalho é criar uma estrutura sólida e interessante que servirá "
                "de guia para os escritores e criadores de vídeos.",
    verbose=True,
    #tools=[search, scrape],
    memory=True,
    llm=gpt4o_llm,
    allow_delegation=True)
    

introducao = Agent (
    role = "Criador Roteirista",
    goal = "Escrever introduções cativantes para roteiros de vídeoaulas sobre {topic} "
           "com base nas informações extraídas de um arquivo de texto, PDF ou "
           "transcrição de vídeo.",
    backstory = "Sua função é ser um Criador de Introduções de Roteiros. Você é um "
                "escritor talentoso, especializado em criar introduções que capturam "
                "a atenção dos espectadores e estabelecem o contexto do vídeo.",
    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)



problematizacao = Agent(
    role = "Analista",
    goal = "Identificar e apresentar o problema central relacionado a {topic}, com "
           "base nas informações extraídas de um arquivo texto, PDF ou transcrição "
           "de vídeo.",
    backstory = "Sua função é ser um Especialista em Problematização. Você é um "
                "especialista em identificar problemas e apresentá-los de maneira "
                "clara e convincente. "
                "Seu trabalho é crucial para contextualizar o tema e destacar a "
                "importância de encontrar soluções.",
    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)



desenvolver = Agent(
    role = "Especialista",
    goal = "Explicar as causas subjacentes do problema relacionado a {topic}, "
           "com base nas informações extraídas de um arquivo de texto, PDF ou "
           "transcrição de vídeo.",
    backstory = "Sua função é ser um Analista de Causas de Problemas. "
                "Você é um analista experiente em identificar e explicar as causas de "
                "problemas. Seu trabalho ajuda a compreender melhor o contexto e as "
                "razões pelas quais o problema existe.",
    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)


resolucao = Agent(
    role = "Consultor",
    goal = "Propor soluções eficazes para o problema relacionado a {topic}, com base "
           "nas informações extraídas de arquivo de texto, PDF ou transcrição de vídeo.",
    backstory = "Sua função é ser um Especialista em Soluções. Você é um especialista "
                "em encontrar soluções para problemas complexos. Seu trabalho é "
                "apresentar soluções práticas e eficazes que possam ser implementadas "
                "para resolver o problema.",
    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)


passos = Agent(
    role = "Instrutor",
    goal = "Fornecer um guia passo a passo para implementar soluções para o problema "
           "relacionado a {topic}, com base nas informações extraídas de um arquivo de "
           "texto, PDF ou transcrição de vídeo.",
    backstory = "Sua função é ser um Instrutor de Soluções. "
                "Você é um instrutor especializado em criar guias práticos que ajudam "
                "as pessoas a implementar soluções. Seu trabalho é garantir que o "
                "público saiba exatamente como resolver o problema.",
    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)



exemplos = Agent(
    role = "Especialista",
    goal = "Fornecer exemplos de casos onde o problema relacionado a {topic} foi "
           "resolvido com sucesso, com base nas informações extraídas de um arquivo "
            "de texto, PDF ou transcrição de vídeo.",
    backstory = "Sua função é ser um Especialista em Exemplos Práticos. "
                "Você é um especialista em encontrar e analisar casos de sucesso. "
                "Seu trabalho é apresentar exemplos práticos que ilustrem como o "
                "problema pode ser resolvido de maneira eficaz.",
    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)


conclusao = Agent(
    role = "Resumidor",
    goal = "Escrever conclusões eficazes para roteiros de vídeoaulas sobre {topic}, "
           "com base nas informações extraídas de um arquivo de texto, PDF ou "
           "transcrição de vídeo.",
    backstory = "Sua função é ser um Criador de Conclusões de Roteiros. "
                "Você é um escritor talentoso especializado em criar conclusões que "
                "resumem os principais pontos e deixam uma impressão duradoura no público.",
    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)



gancho = Agent(
    role = "Roteirista",
    goal = "Ajustar o conteúdo dos roteiros e criar transições suaves entre as "
           "diferentes partes, com base nas informações extraídas de um arquivo de "
           "texto, PDF ou transcrição de vídeo.",
    backstory = "Sua função é ser um Editor de Roteiros. "
                "Você é um editor experiente, especializado em garantir que os roteiros "
                "de vídeos sejam coesos e fluidos. Seu trabalho é ajustar o conteúdo e "
                "criar ganchos que mantenham o interesse do público.",
    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)



revisor = Agent(
    role = "Revisor",
    goal = "Revisar e garantir a qualidade do conteúdo dos roteiros de vídeoaulas "
           "sobre {topic}, com base nas informações extraídas de um arquivo de texto, "
           "PDF ou transcrição de vídeo.",
    backstory = "Sua função é ser um Revisor de Conteúdo. Você é um revisor minucioso, "
                "responsável por garantir que o conteúdo dos roteiros esteja correto, "
                "bem escrito e livre de erros.",
    verbose=True,
    llm=gpt4o_llm,
    allow_delegation=False)



verificao = Agent(
    role = "Verificador",
    goal = "Verificar a precisão e a confiabilidade das fontes e dados usados nos "
           "roteiros de vídeoaulas sobre {topic}, com base nas informações extraídas "
           "de um arquivo de texto, PDF ou transcrição de vídeo.",
    backstory = "Sua função é ser um Verificador de Fontes e Dados. Você é um "
                "verificador especializado em garantir que todas as informações e "
                "dados usados nos roteiros sejam precisos e provenientes de "
                "fontes confiáveis.",

    verbose=True,
    llm=gpt3_llm,
    allow_delegation=False)



adaptacao = Agent(
    role = "Redator",
    goal = "Adaptar a linguagem dos roteiros de vídeoaulas para garantir que sejam "
           "acessíveis e envolventes para o público-alvo sobre {topic}, com base nas "
           "informações extraídas de um arquivo de texto, PDF ou transcrição de vídeo.",
    backstory = "Sua função é ser um Especialista em Adaptação de Linguagem. Você é um "
                "especialista em adaptar a linguagem para diferentes públicos, "
                "garantindo que os roteiros de vídeoaulas sejam claros, envolventes e "
                "adequados ao público-alvo.",

    verbose=True,
    llm=gpt4o_llm,
    allow_delegation=False)



engajamento = Agent(
    role = "Facilitador",
    goal = "Incorporar elementos de engajamento e interatividade nos roteiros de "
           "vídeoaulas sobre {topic}, com base nas informações extraídas de um arquivo "
           "de texto, PDF ou transcrição de vídeo.",
    backstory = "Sua função é ser um Especialista em Engajamento e Interatividade. "
                "Você é um especialista em criar conteúdos que incentivem o "
                "engajamento e a interatividade do público. "
                "Seu trabalho é garantir que os vídeos sejam dinâmicos e mantenham o "
                "interesse dos espectadores.",
    verbose=True,
    llm=gpt4o_llm,
    allow_delegation=False)


########### TAREFAS MIGUEL ########
buscador_task = Task(
    description = (
        "1. Extraia o conteúdo e analise o arquivo de texto, PDF ou a transcrição de "
        "vídeo disponível em {url}.\n"

    ),
    expected_output = (
        "Conteúdo do arquivo extraído com as informações do arquivo de texto, "
        "PDF ou transcrição de vídeo sobre {topic}, incluindo dados quantitativos, "
        "exemplos práticos e uma lista de referências adicionais."
    ),
    agent=buscador,
    verbose=2)


planejador_task = Task(
    description = (
        "1. Analise as informações do agente Investigador e identifique as "
        "informações mais relevantes e úteis do conteúdo sobre o tema {topic} "
        "para construir um roteiro de vídeo.\n"
        "2. Extraia dados estatísticos, gráficos e outras informações quantitativas relevantes.\n"
        "3. Resuma exemplos práticos e aplicações reais de {topic} encontrados no material.\n"
        "4. Compile uma lista de referências e recursos adicionais baseados no conteúdo analisado."
        "5. Desenvolva um esboço de roteiro que inclua uma introdução clara, objetivos "
        "de aprendizado, principais pontos e uma conclusão sobre {topic}, com base nas "
        "informações extraídas do arquivo de texto, PDF ou transcrição.\n"
        "6. Identifique o público-alvo e adapte o conteúdo para atender às suas "
        "necessidades e interesses.\n"
        "7. Inclua palavras-chave de SEO e dados ou fontes acadêmicas relevantes "
        "encontradas no material.\n"
        "8. Proponha exemplos práticos, estudos de caso ou exercícios que "
        "reforcem o aprendizado."
    ),
    expected_output = (
        "Um plano de conteúdo detalhado para a criação de roteiros de vídeoaulas sobre "
        "{topic}, incluindo uma análise do público-alvo, palavras-chave de SEO e "
        "sugestões de recursos acadêmicos baseados no material analisado."
    ),

    agent=planejador,
    verbose=2)



introducao_task = Task(
    description = (
        "1. Escreva uma introdução envolvente que apresente o tema {topic}, utilizando "
        "as informações do arquivo de texto, PDF ou transcrição.\n"
        "2. Defina claramente os objetivos da vídeoaula.\n"
        "3. Use uma linguagem acessível e interessante para atrair o público-alvo."
    ),
    expected_output = (
        "Uma introdução bem escrita e cativante para um roteiro de vídeoaula sobre "
        "{topic}, com objetivos claros e linguagem acessível, baseada nas informações "
        "do material analisado."
    ),

    agent=introducao,
    verbose=2)



problematizacao_task = Task(
    description = (
        "1. Identifique o problema principal relacionado a {topic}, utilizando as "
        "informações do arquivo de texto, PDF ou transcrição.\n"
        "2. Explique o problema de forma clara e detalhada.\n"
        "3. Use exemplos e dados do material para ilustrar a gravidade e a "
        "relevância do problema."
    ),
    expected_output = (
        "Uma descrição detalhada e clara do problema central relacionado a "
        "{topic}, incluindo exemplos e dados retirados do arquivo de texto, "
        "PDF ou transcrição de vídeo."
    ),

    agent=problematizacao,
    verbose=2)



desenvolver_task = Task(
    description = (
        "1. Identifique as causas principais do problema relacionado a {topic}, "
        "utilizando as informações do arquivo de texto, PDF ou transcrição.\n"
        "2. Explique cada causa de forma clara e detalhada.\n"
        "3. Use exemplos e dados do material para apoiar sua análise."
    ),
    expected_output = (
        "Uma explicação detalhada das causas subjacentes do problema relacionado a "
        "{topic}, incluindo exemplos e dados retirados do arquivo de texto, PDF ou "
        "transcrição de vídeo."
    ),

    agent=desenvolver,
    verbose=2)


resolucao_task = Task(
    description = (
        "1. Identifique possíveis soluções para o problema relacionado a {topic}," 
        "utilizando as informações do arquivo de texto, PDF ou transcrição.\n"
        "2. Explique cada solução de forma clara e detalhada.\n"
        "3. Avalie a viabilidade e os benefícios de cada solução com base no "
        "material analisado."
    ),
    expected_output = (
        "Uma lista detalhada de soluções possíveis para o problema relacionado a "
        "{topic}, com explicações claras e uma avaliação de sua viabilidade, baseada "
        "nas informações do arquivo de texto, PDF ou transcrição de vídeo."
    ),

    agent=resolucao,
    verbose=2)


passos_task = Task(
    description = (
        "1. Desenvolva um guia passo a passo para implementar a solução proposta para "
        "o problema relacionado a {topic}, utilizando as informações do arquivo de "
        "texto, PDF ou transcrição.\n"
        "2. Explique cada etapa de forma clara e detalhada.\n"
        "3. Inclua dicas e recomendações baseadas no material analisado para "
        "facilitar a implementação."
    ),
    expected_output = (
        "Um guia passo a passo detalhado para implementar a solução proposta para o "
        "problema relacionado a {topic}, com explicações claras e recomendações úteis, "
        "baseado nas informações do arquivo de texto, PDF ou transcrição de vídeo."
    ),

    agent=passos,
    verbose=2)


exemplos_task = Task(
    description = (
        "1. Pesquise e identifique casos de sucesso onde o problema relacionado a "
        "{topic} foi resolvido, utilizando as informações do arquivo "
        "de texto, PDF ou transcrição.\n"
        "2. Descreva cada caso de forma detalhada.\n"
        "3. Explique como as soluções foram implementadas e os resultados obtidos com "
        "base no material analisado."
    ),
    expected_output = (
        "Uma coleção de exemplos detalhados de casos onde o problema relacionado a "
        "{topic} foi resolvido com sucesso, incluindo descrições das soluções "
        "implementadas e os resultados alcançados, com base nas informações do arquivo "
        "de texto, PDF ou transcrição de vídeo."
    ),

    agent=exemplos,
    verbose=2)


conclusao_task = Task(
    description = (
        "1. Resuma os principais pontos discutidos na vídeoaula sobre "
        "{topic}, utilizando as informações do arquivo texto, PDF ou transcrição.\n"
        "2. Reforce a importância do tema e das soluções apresentadas.\n"
        "3. Inclua uma chamada para ação clara e motivadora, com base no "
        "material analisado."
    ),
    expected_output = (
        "Uma conclusão bem escrita para um roteiro de vídeoaula sobre {topic}, "
        "que resuma os principais pontos e inclua uma chamada para ação clara, baseada "
        "nas informações do arquivo de text, PDF ou transcrição de vídeo."
    ),

    agent=conclusao,
    verbose=2)



gancho_task = Task(
    description = (
        "1. Revise e ajuste o conteúdo do roteiro para garantir coesão e clareza, "
        "utilizando as informações do arquivo texto, PDF ou transcrição.\n"
        "2. Crie transições suaves entre as diferentes partes do roteiro.\n"
        "3. Adicione ganchos que mantenham o interesse e a atenção do público, "
        "com base no material analisado."
    ),
    expected_output = (
        "Um roteiro ajustado e coeso sobre {topic}, com transições suaves e ganchos "
        "eficazes entre as diferentes partes, baseado nas informações do arquivo de "
        "texto, PDF ou transcrição de vídeo."
    ),

    agent=gancho,
    verbose=2)



revisor_task = Task(
    description = (
        "1. Revise o conteúdo do roteiro para corrigir erros gramaticais "
        "e de ortografia.\n"
        "2. Garanta que as informações estejam precisas e atualizadas.\n"
        "3. Verifique se o conteúdo está bem organizado e fácil de entender, "
        "utilizando as informações do arquivo de texto, PDF ou transcrição."
    ),
    expected_output = (
        "Um roteiro de vídeoaula sobre {topic} revisado e livre de erros, com "
        "informações precisas e uma organização clara, baseado nas informações "
        "do arquivo de texto, PDF ou transcrição de vídeo."
    ),

    agent=revisor,
    verbose=2)


verificao_task = Task(
    description = (
        "1. Verifique a precisão das informações e dados usados no roteiro, com base "
        "nas informações do arquivo de texto,  PDF ou transcrição.\n"
        "2. Confirme que todas as fontes são confiáveis e atuais.\n"
        "3. Corrija quaisquer inconsistências ou erros encontrados."
    ),
    expected_output = (
        "Um relatório detalhado sobre a verificação de fontes e dados para o roteiro "
        "de vídeoaula sobre {topic}, garantindo que todas as informações sejam "
        "precisas e confiáveis, baseado nas informações do arquivo de texto, "
        "PDF ou transcrição de vídeo."
    ),

    agent=verificao,
    verbose=2)



adaptacao_task = Task(
    description = (
        "1. Revise o roteiro para adaptar a linguagem ao público-alvo, utilizando "
        "as informações do arquivo de texto, PDF ou transcrição.\n"
        "2. Garanta que a linguagem seja clara, acessível e envolvente.\n"
        "3. Ajuste o tom e o estilo conforme necessário, baseado no material analisado."
    ),
    expected_output = (
        "Um roteiro de vídeoaula sobre {topic} com linguagem adaptada para ser clara, "
        "acessível e envolvente para o público-alvo, baseado nas informações do "
        "arquivo de texto, PDF ou transcrição de vídeo."
    ),

    agent=adaptacao,
    verbose=2)



engajamento_task = Task(
    description = (
        "1. Identifique oportunidades para incluir elementos interativos no roteiro, "
        "utilizando as informações do arquivo de texto, PDF ou transcrição.\n"
        "2. Proponha perguntas, atividades ou chamadas para ação que incentivem a "
        "participação do público.\n"
        "3. Garanta que os elementos de engajamento sejam integrados de forma fluida "
        "no conteúdo do vídeo, baseado no material analisado."
    ),
    expected_output = (
        "Um roteiro de vídeoaula sobre {topic} com elementos de engajamento e "
        "interatividade incorporados, incluindo perguntas, atividades e chamadas para "
        "ação que incentivem a participação do público, baseado nas informações do "
        "arquivo de texto, PDF ou transcrição de vídeo."
    ),

    agent=engajamento,
    verbose=2)


################  CREW  #########

crew = Crew(agents=[
        buscador, planejador, introducao, problematizacao, desenvolver, resolucao, 
        passos, exemplos, conclusao, gancho, revisor, verificao, adaptacao, engajamento
            ],
            tasks=[
        buscador_task, planejador_task, introducao_task, problematizacao_task, 
        desenvolver_task, resolucao_task, passos_task, exemplos_task, conclusao_task, 
        gancho_task, revisor_task, verificao_task, adaptacao_task, engajamento_task
            ],
            process=Process.sequential,
            verbose=2,
            memory=True)

############# EXECUTANDO ##########

result = crew.kickoff(inputs={
    'topic': 'Transformações do Estado e a Administração Pública no século XXI',
    'url': 'https://portal.educamundo.com.br/api_legado/teste-roteiro-agentes.txt'
})

def team(prompt):
    return crew.kickoff(inputs={prompt})

current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"posts-{current_date}.txt"  #"post-2024-06-11.txt"
with open(filename, 'w', encoding='utf-8') as file:
    file.write(result)
