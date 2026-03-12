import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import xmltodict

# Configuracao da pagina
st.set_page_config(page_title="Estoque na Nuvem", layout="wide")
st.title("📦 Sistema de Estoque - Conectado ao Google Sheets")

# Criar conexao com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Funcao para ler os dados da planilha
def buscar_estoque():
    return conn.read(ttl=0) # ttl=0 garante que ele busque o dado mais atual

st.header("1. Importar Nota Fiscal (XML)")
arquivo_xml = st.file_uploader("Arraste o arquivo XML da nota", type="xml")

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

        novos_itens = []
        for item in produtos_nfe:
            prod = item['prod']
            novos_itens.append({
                "Codigo": str(prod['cProd']),
                "Produto": prod['xProd'],
                "Quantidade": float(prod['qCom']),
                "Preco_Unitario": float(prod['vUnCom'])
            })
            st.write(f"✅ {prod['xProd']} - Qtd: {prod['qCom']}")

        if st.button("Salvar na Planilha Google"):
            estoque_atual = buscar_estoque()
            novo_df = pd.DataFrame(novos_itens)
            
            # Une o que ja tem com o novo e soma as quantidades
            estoque_final = pd.concat([estoque_atual, novo_df]).groupby(['Codigo', 'Produto'], as_index=False).sum()
            
            # Atualiza a planilha
            conn.update(data=estoque_final)
            st.success("Dados salvos com sucesso no Google Sheets!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro: {e}")

st.markdown("---")
st.header("2. Estoque Atual (Direto da Planilha)")
dados = buscar_estoque()
st.dataframe(dados, use_container_width=True)