import streamlit as st
import pandas as pd
import xmltodict
import os

# Nome do arquivo de banco de dados
DB_FILE = "meu_estoque.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            return pd.read_csv(DB_FILE, encoding='latin1')
    return pd.DataFrame(columns=["Codigo", "Produto", "Quantidade", "Preco_Unitario"])

def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)

st.set_page_config(page_title="Estoque NF", layout="wide")
st.title("Sistema de Estoque - Importacao de Nota Fiscal")

st.header("1. Importar Nota Fiscal (XML)")
arquivo_xml = st.file_uploader("Arraste o arquivo XML aqui", type="xml")

if arquivo_xml:
    try:
        conteudo_xml = arquivo_xml.read()
        dados_xml = xmltodict.parse(conteudo_xml)
        
        # Tenta encontrar os dados da nota
        nfe_root = dados_xml.get('nfeProc', {}).get('NFe', {}).get('infNFe', {})
        if not nfe_root:
             nfe_root = dados_xml.get('NFe', {}).get('infNFe', {})
             
        produtos_nfe = nfe_root.get('det', [])
        
        if not isinstance(produtos_nfe, list):
            produtos_nfe = [produtos_nfe]

        st.subheader("Produtos encontrados:")
        novos_itens = []
        
        for item in produtos_nfe:
            prod = item['prod']
            nome = prod['xProd']
            qtd = float(prod['qCom'])
            preco = float(prod['vUnCom'])
            codigo = prod['cProd']
            
            st.write(f"Item: {nome} | Qtd: {qtd} | R$: {preco}")
            novos_itens.append({"Codigo": str(codigo), "Produto": nome, "Quantidade": qtd, "Preco_Unitario": preco})

        if st.button("Salvar no Estoque"):
            estoque_atual = carregar_dados()
            estoque_atual['Codigo'] = estoque_atual['Codigo'].astype(str)
            
            novo_df = pd.DataFrame(novos_itens)
            # Soma as quantidades se o produto ja existir
            estoque_final = pd.concat([estoque_atual, novo_df]).groupby(['Codigo', 'Produto'], as_index=False).sum()
            salvar_dados(estoque_final)
            st.success("Estoque atualizado!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro ao ler nota: {e}")

st.markdown("---")
st.header("2. Estoque Atual")
estoque_exibir = carregar_dados()
st.dataframe(estoque_exibir, use_container_width=True)