import streamlit as st
import re
import os
import pdfplumber
import shutil
from io import BytesIO
import zipfile

# Título da aplicação
st.title("Renomeador de PDFs por Informação Extraída")

# Criar diretório temporário
output_dir = "arquivos_renomeados"
os.makedirs(output_dir, exist_ok=True)

# Função para extrair número e nome
def extrair_informacao(file):
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                texto = page.extract_text()
                if texto:
                    texto = re.sub(r'\n+', ' ', texto)

                    # Número (ex: N° 12345)
                    numero_match = re.search(r'N[º°]?\s*(\d+)', texto, re.IGNORECASE)
                    numero = numero_match.group(1).lstrip('0') if numero_match else None

                    # Nome após "REM.:"
                    nome = "Nome_Indisponivel"
                    nome_match = re.search(r'REM\.\:\s*([A-Za-zÀ-ÿ\s,.-]+)', texto)
                    if nome_match:
                        nome = nome_match.group(1).strip()
                        nome = re.sub(r'\s*-.*$', '', nome).strip()
                        nome = re.sub(r'\b(HABILITAÇÃO|FILIAÇÃO)\b', '', nome, flags=re.IGNORECASE).strip()

                    if numero and nome:
                        return f"{numero} {nome}"
        return "Informacao_Nao_Encontrada"
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return "Informacao_Nao_Encontrada"

# Upload dos arquivos
uploaded_files = st.file_uploader("Faça upload dos arquivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        info_extraida = extrair_informacao(uploaded_file)
        if info_extraida and info_extraida != "Informacao_Nao_Encontrada":
            novo_nome = re.sub(r'[\/:*?"<>|]', '_', info_extraida) + ".pdf"
            caminho = os.path.join(output_dir, novo_nome)

            # Salvar arquivo
            with open(caminho, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Arquivo '{uploaded_file.name}' renomeado para '{novo_nome}'")

    # Compactar os arquivos renomeados
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file)

    zip_buffer.seek(0)
    st.download_button(
        label="📦 Baixar ZIP com PDFs renomeados",
        data=zip_buffer,
        file_name="pdfs_renomeados.zip",
        mime="application/zip"
    )
