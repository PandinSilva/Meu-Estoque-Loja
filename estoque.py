import streamlit as st
import pandas as pd
import xmltodict
import requests

# Configurações do formulário (IDs que pegamos do seu link)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSemnrbeHWnsaJDJbhdRNEuGY3pI2vFrPvqXuystlzhUFwnoEQ/formResponse"

# Dicionário mapeando as entradas do Google Forms
ID_CODIGO = "entry.2084338753"
ID_PRODUTO = "entry.333539528"
ID_QTD = "entry.1801737990"
ID_PRECO = "entry.981122510"

st.set_page_config(page_title="Estoque Loja", layout="wide")
st.title("📦 Sistema de Entrada de Estoque")

st.header("1. Importar Nota Fiscal (XML)")
arquivo_xml = st.file_uploader("Arraste o arquivo XML da nota aqui", type="xml")

if arquivo_xml:
    try:
        conteudo_xml = arquivo_xml.read()
        dados_xml = xmltodict.parse(conteudo_xml)
        
        nfe_root = dados_xml.get('nfeProc', {}).get('NFe', {}).get('infNFe', {})
        if not nfe_root:
             nfe_root = dados_xml.get('NFe', {}).get('infNFe', {})
             
        produtos_nfe = nfe_root.get('det', [])
        if not isinstance(produtos_nfe, list):
            produtos_nfe = [produtos_nfe]

        st.subheader("Produtos detectados na nota:")
        
        for item in produtos_nfe:
            prod = item['prod']
            nome = prod['xProd']
            qtd = prod['qCom']
            preco = prod['vUnCom']
            codigo = prod['cProd']
            
            col1, col2 = st.columns([3, 1])
            col1.write(f"🔹 **{nome}** (Cód: {codigo})")
            
            # Botão individual para cada item para garantir o envio correto
            if col2.button(f"Salvar {codigo}"):
                dados_form = {
                    ID_CODIGO: codigo,
                    ID_PRODUTO: nome,
                    ID_QTD: qtd,
                    ID_PRECO: preco
                }
                # Envia os dados para o Google Forms
                resposta = requests.post(FORM_URL, data=dados_form)
                
                if resposta.status_code == 200:
                    st.success(f"Item {nome} enviado para a planilha!")
                else:
                    st.error("Erro ao enviar. Verifique a internet.")
            
    except Exception as e:
        st.error(f"Erro ao processar XML: {e}")

st.markdown("---")
st.info("Para ver o estoque completo, abra sua planilha de respostas do Google Forms.")