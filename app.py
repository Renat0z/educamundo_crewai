#importar biblioteca

import os
import streamlit as st
import pandas as pd

## BARRA LATERAL

with st.sidebar:
    ##
    ### LISTA DE EQUIPES DE AGENTES
    with st.form('adicionar_agente'):
        equipe = st.radio("Escolha o agente",
                          options=("Trancrição do youtube",
                                   "Pesquisador",
                                   "Escritor",
                                   "Miguel",
                                  ))
        st.form_submit_button('Escolher')

    ### SELECIONAR TIPO DE ENTRADA DE DADOS

    option = st.selectbox("De onde vêm as informações do projeto?",
                          ("Enviar arquivo", "Preencher prompt"))

    ### SESSÃO PARA ARMAZENAR OS INPUTS

    # arquivo dos agentes
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = []

    # CARREGAR LISTAS E DICIONÁRIOS

    nome_projeto = ""  #nome do arquivo
    prompt = {}  #entrada do crewai
    lista_prompts = {}

    ####################################
    ####################################

    #### FORMULÁRIO

    # FORMULÁRIO DO PROJETO

    if option == "Preencher prompt":
        prompt = ""
        msg_usuario = ""

        with st.form('criar_projeto'):
            entrada = st.text_area("Escreva aqui o prompt")

            if st.form_submit_button('Criar projeto'):
                #zerar prompt
                st.session_state.selected_files = []

                #criar dicionário
                prompt += entrada

            #adicionar na sessão de prompts
            st.session_state.selected_files.append(prompt)

            #for chave, valor in prompt.items():
            #      msg_usuario += f"{chave.capitalize()}: {valor}\n"

    ####################################
    ####################################

    #   UPLOAD DO PROJETO EM XLSX /CSV

    if option == "Enviar arquivo":

        #faz upload do xlsx/csv
        uploaded_file = st.file_uploader("Escolha o arquivo",
                                         type=['xlsx', 'csv'])
        if uploaded_file is not None:
            #verificar extensão e carregar dataframe
            if uploaded_file.name[-3:] == 'csv':
                df = pd.read_csv(uploaded_file)
                nome_arquivo = uploaded_file.name[:-4]
            else:
                df = pd.read_excel(uploaded_file)
                nome_arquivo = uploaded_file.name[:-5]

            #exibir dataframe
            st.dataframe(df)
            
            # checkbox para rodar tudo
            todos = st.checkbox("Rodar todas de uma vez")

            # condição se for todos
            if todos:
                projeto_final = df
                nome_projeto += nome_arquivo
                todas_linhas = 'sim'

            #condição para apenas uma linha
            else:
                #criar lista de projetos
                lista_projetos = df.iloc[:, 0].tolist()
                projeto_selecionado = st.selectbox("Escolha seu projeto: ",
                                                   lista_projetos)

                #seleciona linha do dataframe do projeto escolhido
                projeto_escolhido = df.loc[df.iloc[:,
                                                   0] == projeto_selecionado]

                #tornar dataframe vertical
                projeto_vertical = projeto_escolhido.transpose()
                
                #exibe dataframe vertical
                st.dataframe(projeto_vertical)

                #tornar dataframe horizontal de novo
                projeto_final = projeto_vertical.transpose()

                #nome do arquivo
                nome_projeto += projeto_selecionado

        # dicionário do prompt do usuário
        msg_usuario = ""

        #botão de criar projeto
        if st.button("Criar Projeto"):
            #zerar prompt
            st.session_state.selected_files = []

            if todos:
                lista_prompts = projeto_final.to_dict(orient='records')
                st.write(lista_prompts)
            else:
                prompt = projeto_final.to_dict(orient='records')[0]

                #adicionar na sessão de prompts
                st.session_state.selected_files.append(prompt)

                for chave, valor in prompt.items():
                    msg_usuario += f"{chave.capitalize()}: {valor}\n"

                st.write(msg_usuario)


####################################
####################################

## CARREGAR AGENTES DE OUTROS ARQUIVOS

def optar():
    if equipe == "Trancrição do youtube":
        from youtube_transcript import (
            Transcription
        )  # Certifique-se de que agente está no mesmo diretório ou no PYTHONPATH
        result = Transcription(prompt)

        return result

    if equipe == "Pesquisador":
        from pesquisador import (
            Pesquisa
        )  # Certifique-se de que agente está no mesmo diretório ou no PYTHONPATH
        result = Pesquisa(prompt)

        return result
        
    if equipe == "Escritor":
        from escritor_C import (
            escritor_de_blog
        )  # Certifique-se de que agente está no mesmo diretório ou no PYTHONPATH
        result = escritor_de_blog(prompt)

        return result
        
    if equipe == "Miguel":
        from Miguel import (
            team
        )  # Certifique-se de que agente está no mesmo diretório ou no PYTHONPATH
        result = team(prompt)

        return result


####################################
####################################

###
### CHAT

# INICIAR SESSÃO DE HISTÓRICO DE CONVERSA

if "messages" not in st.session_state:
    st.session_state.messages = []

## COLOCAR CHAT DE MENSAGENS NA TELA

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    if role == "user":
        st.markdown(f"**Usuário**: {content}")
    elif role == "assistant":
        st.markdown(f"**Equipe {equipe}**: {content}")


####################################
####################################

###
# MOSTRAR RESPOSTA ASSISTENTE NO CHAT

def criar_projeto(prompt):

    ##
    ### USUÁRIO

    # MOSTRA user message no chat message container
    st.markdown(f"**Usuário**: {prompt}")

    # ADICIONA user message no histórico (chat history)
    st.session_state.messages.append({"role": "user", "content": prompt})

    ##
    ### ASSISTANT

    # EXECUTA E MOSTRA resposta do assistant no chat message container

    response = f"**Equipe** {equipe}:\n\n " + optar()

    #mostra resposta do agente
    st.markdown(response)

    # adiciona resposta do agente no chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

### EXECUÇÃO QUANDO APERTA O BOTÃO (CRIAR PROJETO)

# ÚNICA LINHA
if prompt:
    criar_projeto(prompt)

#PROJETO COMPLETO
if lista_prompts:
    for prompt in lista_prompts:
        criar_projeto(prompt)
