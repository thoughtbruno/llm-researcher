#!/usr/bin/env python
import streamlit as st
import asyncio
from datetime import datetime
from typing import Dict, List
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path para importar os módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_researcher.crew import LlmResearcher

# Configuração da página
st.set_page_config(
    page_title="LLM Researcher Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar a aparência
st.markdown("""
<style>
    /* Background geral da aplicação */
    .stApp {
        background-color: #f5f5f5;
    }
    
    /* Background da área principal */
    .main .block-container {
        background-color: #f5f5f5;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #FFFFFF;
        border-left: 4px solid #FFFFFF;
        color: #1a1a1a;
    }
    .assistant-message {
        background-color: #FFFFFF;
        border-left: 4px solid #FFFFFF;
        color: #1a1a1a;
    }
    .timestamp {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
        margin-top: 0.5rem;
    }
    .sidebar-info {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        color: #FFFFFF;
    }
    
    /* Melhorar contraste geral */
    .stMarkdown, .stText {
        color: #FFFFFF;
    }
    
    /* Ajustar cores do sidebar */
    .css-1d391kg {
        background-color: #f0f0f0;
    }
    
    /* Background da sidebar */
    .css-1lcbmhc, .css-1cypcdb {
        background-color: #f0f0f0;
    }
    
    /* Sidebar container */
    section[data-testid="stSidebar"] {
        background-color: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar o estado da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

if "crew_instance" not in st.session_state:
    st.session_state.crew_instance = None

if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

if "last_report_time" not in st.session_state:
    st.session_state.last_report_time = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Chat"

def initialize_crew():
    """Inicializa a instância do CrewAI"""
    if st.session_state.crew_instance is None:
        try:
            st.session_state.crew_instance = LlmResearcher()
            return True
        except Exception as e:
            st.error(f"Erro ao inicializar o CrewAI: {e}")
            return False
    return True

def run_crew_analysis(topic: str) -> str:
    """Executa a análise do CrewAI com o tópico fornecido"""
    try:
        inputs = {'topic': topic}
        
        # Executar o crew
        result = st.session_state.crew_instance.crew().kickoff(inputs=inputs)
        
        # Marcar que um novo relatório foi gerado
        st.session_state.report_generated = True
        st.session_state.last_report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return "Seu relatório foi gerado com sucesso! 📊\n\nVocê pode visualizá-lo na aba 'Relatório HTML' na barra lateral."
            
    except Exception as e:
        return f"Erro ao executar a análise: {str(e)}"

def load_html_report() -> str:
    """Carrega o conteúdo do relatório HTML"""
    report_path = Path(__file__).parent / "report.html"
    try:
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        st.error(f"Erro ao carregar o relatório: {e}")
        return None

def display_message(message: Dict, is_user: bool = False):
    """Exibe uma mensagem no chat"""
    css_class = "user-message" if is_user else "assistant-message"
    icon = "👤" if is_user else "🤖"
    
    with st.container():
        st.markdown(f"""
        <div class="chat-message {css_class}">
            <strong>{icon} {"Você" if is_user else "LLM Researcher"}:</strong><br>
            {message['content']}
            <div class="timestamp">{message['timestamp']}</div>
        </div>
        """, unsafe_allow_html=True)

def show_chat_page():
    """Exibe a página do chat"""
    # Área principal do chat
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Exibir histórico de mensagens
        if st.session_state.messages:
            st.markdown("### 💬 Conversa")
            for message in st.session_state.messages:
                display_message(message, message.get("role") == "user")
        else:
            st.markdown("""
            ### 👋 Bem-vindo ao LLM Researcher Chat!
            
            Digite sua pergunta ou tópico de pesquisa abaixo para começar. 
            O sistema irá analisar os dados disponíveis e gerar insights úteis.
            
            **Exemplos de perguntas:**
            - "Analise a produtividade dos trabalhadores"
            - "Quais são os principais fatores que afetam a produtividade?"
            - "Gere um relatório sobre eficiência operacional"
            """)
    
    with col2:
        # Status do sistema
        st.markdown("### 🔧 Status do Sistema")
        
        # Verificar se o CrewAI está inicializado
        if initialize_crew():
            st.success("✅ CrewAI Inicializado")
        else:
            st.error("❌ Erro na Inicialização")
        
        # Estatísticas
        st.metric("Mensagens", len(st.session_state.messages))
        
        if st.session_state.messages:
            last_message_time = st.session_state.messages[-1].get("timestamp", "")
            st.metric("Última Interação", last_message_time.split()[1] if " " in last_message_time else last_message_time)
    
    # Input do usuário
    st.markdown("---")
    
    # Formulário para enviar mensagem
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Digite sua pergunta ou tópico de pesquisa:",
                placeholder="Ex: Analise a produtividade dos trabalhadores...",
                key="user_input"
            )
        
        with col2:
            submit_button = st.form_submit_button("🚀 Enviar", use_container_width=True)
    
    # Processar input do usuário
    if submit_button and user_input:
        # Adicionar mensagem do usuário
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        }
        st.session_state.messages.append(user_message)
        
        # Mostrar indicador de carregamento
        with st.spinner("🤔 Analisando sua pergunta..."):
            # Executar análise
            if initialize_crew():
                response = run_crew_analysis(user_input)
                
                # Adicionar resposta do assistente
                assistant_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.messages.append(assistant_message)
            else:
                error_message = {
                    "role": "assistant",
                    "content": "Desculpe, houve um erro ao processar sua solicitação. Verifique se o sistema está configurado corretamente.",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.messages.append(error_message)
        
        # Recarregar a página para mostrar as novas mensagens
        st.rerun()

def show_report_page():
    """Exibe a página do relatório HTML"""
    st.markdown("### 📊 Relatório HTML")
    
    # Verificar se existe um relatório
    html_content = load_html_report()
    
    if html_content:
        st.markdown("---")
        
        # Opções de visualização
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Atualizar Relatório", use_container_width=True):
                st.rerun()
        
        with col2:
            # Botão para download
            st.download_button(
                label="📥 Download HTML",
                data=html_content,
                file_name=f"relatorio_llm_researcher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        with col3:
            if st.session_state.last_report_time:
                st.info(f"📅 Último relatório gerado em: {st.session_state.last_report_time}")
        
        st.markdown("---")
        
        # Exibir o HTML
        st.components.v1.html(html_content, height=800, scrolling=True)
        
    else:
        st.warning("📝 Nenhum relatório encontrado.")
        st.markdown("""
        Para gerar um relatório:
        1. Vá para a aba **Chat**
        2. Digite uma pergunta ou tópico de pesquisa
        3. Aguarde o processamento
        4. Retorne aqui para visualizar o relatório gerado
        """)

# Interface principal
def main():
    # Cabeçalho
    st.markdown('<h1 class="main-header">🤖 LLM Researcher</h1>', unsafe_allow_html=True)
    
    # Sidebar com navegação e informações
    with st.sidebar:
        # Navegação entre páginas
        st.markdown("### 🧭 Navegação")
        
        # Botões de navegação
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💬 Chat", use_container_width=True, type="primary" if st.session_state.current_page == "Chat" else "secondary"):
                st.session_state.current_page = "Chat"
                st.rerun()
        
        with col2:
            # Destacar se há um novo relatório
            button_type = "primary" if st.session_state.current_page == "Relatório" else "secondary"
            if st.session_state.report_generated and st.session_state.current_page != "Relatório":
                button_label = "📊 Relatório ✨"
            else:
                button_label = "📊 Relatório"
                
            if st.button(button_label, use_container_width=True, type=button_type):
                st.session_state.current_page = "Relatório"
                st.rerun()
        
        st.markdown("---")
        
        # Status do relatório
        if st.session_state.report_generated:
            st.success("✅ Relatório disponível")
            if st.session_state.last_report_time:
                st.caption(f"Gerado em: {st.session_state.last_report_time}")
        else:
            st.info("📝 Nenhum relatório gerado ainda")
        
        st.markdown("---")
        
        # Botão para limpar histórico (apenas na página do chat)
        if st.session_state.current_page == "Chat":
            if st.button("🗑️ Limpar Histórico do Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    # Exibir a página atual
    if st.session_state.current_page == "Chat":
        show_chat_page()
    elif st.session_state.current_page == "Relatório":
        show_report_page()

if __name__ == "__main__":
    main()
