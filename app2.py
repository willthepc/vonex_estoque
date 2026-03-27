import streamlit as st
import pandas as pd
import sqlite3


bdEstoque = sqlite3.connect('estoque.db', check_same_thread=False)

cursor = bdEstoque.cursor()



cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtosTable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT UNIQUE,
        total INTEGER CHECK(total >= 0)
    )  
    ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS historicoTable (
        id INTEGER,
        movimentacao TEXT,
        produto TEXT,
        categoria TEXT,
        quantidade INTEGER,
        destino TEXT,
        protocolo INTEGER,
        observacao TEXT
    )         
    ''')


listaProdutos = ["Adaptador Display Port para HDMI", "Adaptador p/ Tomada 10A 2P+T", 
                                       "Adaptador P2/P3 para Lightning", "Adaptador P3 para USB", 
                                       "Adaptador de Som USB VENTION", "Adaptador USB Ethernet TP-LINK",
                                        "Carregador e Cabo IPAD", "Carregador Notebook LENOVO 20V", 
                                        "DELL OPTIPLEX 3050", "DELL OPTIPLEX 7020", "DELL OPTIPLEX 9020", 
                                        "Extensor USB Genérico", "Filtro de Linha 3 Tomadas", 
                                        "Filtro de Linha 5 Tomadas", "Fonte MYMAX Desktop 300W", "Headset HP P3", 
                                        "Headset JBL QUANTUM 100", "Headset JBL QUANTUM 200", "Headset TOP USE USB", 
                                        "Headset USB LOGITECH H390", "HUB USB 4 Portas EXBOM", 
                                        "Kit Teclado e Mouse Wireless DELL", "Memória RAM Notebook 8GB DDR4 2666MHz RISE MODE", 
                                        "MINI MAC APPLE", "Monitor ACER 19.5", "Monitor DELL 19.5", "Monitor FOX RACER 19.5", 
                                        "Monitor LG 19.5", "Monitor LG 24", "Monitor PHILIPS 21", "Monitor T350 SAMSUNG 27", 
                                        "Mouse LOGITECH M150 Wireless", "Mouse LOGITECH M170", "Mouse Pad Preto", "Mouse USB LOGITECH M90",
                                        "Notebook ACER ASPIRE I3 8GB RAM 256GB", "Notebook ASUS VIVOBOOK GO 16GB 512GB", 
                                        "Notebook LENOVO RYZEN 5 8GB 256GB", "Notebook SAMSUNG BOOK4 I3 8GB 256GB", 
                                        "Notebook SAMSUNG I5 8GB 256GB", "Notebook VAIO FIT 15S I7 8GB 256GB", 
                                        "Película de Privacidade 24", "Pendrive KINGSTON 64GB", "SSD KINGSTON 240GB", 
                                        "Suporte de Monitor Articulado", "Switch POE 5 Portas TP-LINK", "Teclado USB EXBOM BK-102",
                                        "Teclado USB LOGITECH K120", "Tela de Privacidade 15.6", "Tela de Privacidade 19.5",
                                        "Telefone IP HUAWEI ET655", "Webcam HD 1080P Genérica", "Webcam KROSS ELEGANCE 1080P",
                                        "Webcam KROSS ELEGANCE 720P", "Webcam LOGITECH C270", "Webcam RISEMODE 1080P"]

bdEstoque.commit()


@st.dialog("Registrar Entrada")
def modal_entrada():
    st.text("ENTRADA")
    movimentacao = "ENTRADA"
    produto = st.selectbox("Produto", listaProdutos)
    categoria = st.selectbox("Categoria", ["Adaptador/Extensor", "Desktop", "Monitor", "Notebook", "Periférico", "Outros"])
    quantidade = st.number_input("Quantidade", min_value=1)
    destino = st.text_input("Destino")
    protocolo = st.number_input("Número do Protocolo", min_value=1)
    observacao = st.text_input("Observação")
    if st.button("Confirmar Entrada"):
        try:
            cursor.execute("SELECT id FROM produtosTable WHERE produto = ?", (produto,))
            id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO historicoTable (id, movimentacao, produto, categoria, quantidade, destino, protocolo, observacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, movimentacao, produto, categoria, quantidade, destino, protocolo, observacao))
            cursor.execute("UPDATE produtosTable SET total = total + ? WHERE produto = ?", (quantidade, produto))
            bdEstoque.commit()
            st.success(f"{quantidade} unidades de {produto} adicionadas!")
            st.rerun()
        except sqlite3.OperationalError:
            st.error("Operational Error")


@st.dialog("Registrar Saída")
def modal_saida():
    st.text("SAÍDA")
    movimentacao = "SAÍDA"
    produto = st.selectbox("Produto", listaProdutos)
    categoria = st.selectbox("Categoria", ["Adaptador/Extensor", "Desktop", "Monitor", "Notebook", "Periférico", "Outros"])
    quantidade = st.number_input("Quantidade", min_value=1)
    destino = st.text_input("Destino")
    protocolo = st.number_input("Número do Protocolo", min_value=1)
    observacao = st.text_input("Observação")
    if st.button("Confirmar Saída"):
        try:
            cursor.execute("UPDATE produtosTable SET total = total - ? WHERE produto = ?", (quantidade, produto))
            cursor.execute("SELECT id FROM produtosTable WHERE produto = ?", (produto,))
            id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO historicoTable (id, movimentacao, produto, categoria, quantidade, destino, protocolo, observacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, movimentacao, produto, categoria, quantidade, destino, protocolo, observacao))
            bdEstoque.commit()
            st.success(f"{quantidade} unidades de {produto} removidas!")
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("Quantidade indísponivel.")
            
            
        

#INTERFACE PRINCIPAL
st.title("📦 Sistema de Estoque")

col1, col2, _ = st.columns([1, 1, 4])

with col1:
    if st.button("➕ Entrada"):
        modal_entrada()

with col2:
    if st.button("➖ Saída"):
        modal_saida()

st.divider()


df = pd.read_sql_query("SELECT * FROM produtosTable", bdEstoque)
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("HISTÓRICO")

df2 = pd.read_sql_query("SELECT * FROM historicoTable", bdEstoque)
st.dataframe(df2, use_container_width=True, hide_index=True)
