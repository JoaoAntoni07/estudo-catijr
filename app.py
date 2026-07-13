import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanças")

st.markdown("""
# Boas vindas
## Nosso app financeiro!
""")

file_upload = st.file_uploader(label="Faça upload dos dados", type=["csv"])

if file_upload:
    
    # leitura dos dados
    df = pd.read_csv(file_upload)
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y").dt.date  

    # exibição dos dados no app
    exp1 = st.expander('Dados Brutos')
    columns_fmt = {"Valor": st.column_config.NumberColumn("Valor", format="$%d")}
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)
    
    # visão instituição
    exp2 =st.expander('Instituição')
    df_instituicao = df.pivot_table(index="Data", columns="Instituição", values="Valor")

    tab_data, tab_history, tab_share = st.tabs(['Dados', 'Histórico', 'Distribuição'])
    
    with tab_data:
        st.dataframe(df_instituicao)

    with tab_history:
        st.line_chart(df_instituicao)

    with tab_share:

        date = st.date_input("Data para distribuição",
                      min_value=df_instituicao.index.min(),
                      max_value=df_instituicao.index.max()
                      )

        if date not in df_instituicao.index:
            st.warning('Entre com uma data válida.')

        else:
            st.bar_chart(df_instituicao.loc[date])
