import streamlit as st
import pandas as pd
import datetime

# Calcula estatísticas gerais do patrimônio ao longo do tempo
def calc_general_stats(df):
    # Soma os valores por data
    df_data = df.groupby(by="Data")[["Valor"]].sum()

    # Valor do mês anterior
    df_data["lag_1"] = df_data["Valor"].shift(1)

    # Diferença absoluta entre os meses
    df_data["Diferença Mensal Abs."] = df_data["Valor"] - df_data["lag_1"]

    # Médias móveis da diferença mensal
    df_data["Média 6M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(6).mean()
    df_data["Média 12M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(12).mean()
    df_data["Média 24M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(24).mean()

    # Variação percentual em relação ao mês anterior
    df_data["Diferença Mensal Rel."] = df_data["Valor"] / df_data["lag_1"] - 1

    # Evolução total do patrimônio em janelas de tempo
    df_data["Evolução 6M Total"] = df_data["Valor"].rolling(6).apply(lambda x: x[-1] - x[0])
    df_data["Evolução 12M Total"] = df_data["Valor"].rolling(12).apply(lambda x: x[-1] - x[0])
    df_data["Evolução 24M Total"] = df_data["Valor"].rolling(24).apply(lambda x: x[-1] - x[0])

    # Evolução percentual do patrimônio
    df_data["Evolução 6M Relativa"] = df_data["Valor"].rolling(6).apply(lambda x: x[-1] / x[0])
    df_data["Evolução 12M Relativa"] = df_data["Valor"].rolling(12).apply(lambda x: x[-1] / x[0])
    df_data["Evolução 24M Relativa"] = df_data["Valor"].rolling(24).apply(lambda x: x[-1] / x[0])

    return df_data

# Configuração da página
st.set_page_config(page_title="Finanças")

# Título do aplicativo
st.markdown("""
# Boas vindas
## Nosso app financeiro!
""")

# Upload do arquivo CSV
file_upload = st.file_uploader(label="Faça upload dos dados", type=["csv"])

# Executa apenas se um arquivo for enviado
if file_upload:

    # Lê o arquivo
    df = pd.read_csv(file_upload)

    # Converte a coluna Data para o formato de data
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y").dt.date

    # Exibe os dados originais
    exp1 = st.expander('Dados Brutos')
    columns_fmt = {"Valor": st.column_config.NumberColumn("Valor", format="$%d")}
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)

    # Seção de análise por instituição
    with st.expander('Instituição'):

        # Cria tabela dinâmica
        df_instituicao = df.pivot_table(index="Data", columns="Instituição", values="Valor")

        # Cria abas
        tab_data, tab_history, tab_share = st.tabs(['Dados', 'Histórico', 'Distribuição'])

        # Tabela
        with tab_data:
            st.dataframe(df_instituicao)

        # Gráfico de evolução
        with tab_history:
            st.line_chart(df_instituicao)

        # Distribuição por data
        with tab_share:

            date = st.date_input(
                "Data para distribuição",
                min_value=df_instituicao.index.min(),
                max_value=df_instituicao.index.max()
            )

            # Verifica se existe informação para a data escolhida
            if date not in df_instituicao.index:
                st.warning('Entre com uma data válida.')
            else:
                st.bar_chart(df_instituicao.loc[date])

    # Estatísticas gerais
    with st.expander("Estatísticas Gerais"):

        # Calcula estatísticas
        df_stats = calc_general_stats(df)

        # Formatação das colunas
        columns_config = {
            "Valor": st.column_config.NumberColumn("Valor", format='R$ %.2f'),
            "Diferença Mensal Abs.": st.column_config.NumberColumn("Diferença Mensal Abs.", format='R$ %.2f'),
            "Média 6M Diferença Mensal Abs.": st.column_config.NumberColumn("Média 6M Diferença Mensal Abs.", format='R$ %.2f'),
            "Média 12M Diferença Mensal Abs.": st.column_config.NumberColumn("Média 12M Diferença Mensal Abs.", format='R$ %.2f'),
            "Média 24M Diferença Mensal Abs.": st.column_config.NumberColumn("Média 24M Diferença Mensal Abs.", format='R$ %.2f'),
            "Evolução 6M Total": st.column_config.NumberColumn("Evolução 6M Total", format='R$ %.2f'),
            "Evolução 12M Total": st.column_config.NumberColumn("Evolução 12M Total", format='R$ %.2f'),
            "Evolução 24M Total": st.column_config.NumberColumn("Evolução 24M Total", format='R$ %.2f'),
            "Diferença Mensal Rel.": st.column_config.NumberColumn("Diferença Mensal Rel.", format='percent'),
            "Evolução 6M Relativa": st.column_config.NumberColumn("Evolução 6M Relativa", format='percent'),
            "Evolução 12M Relativa": st.column_config.NumberColumn("Evolução 12M Relativa", format='percent'),
            "Evolução 24M Relativa": st.column_config.NumberColumn("Evolução 24M Relativa", format='percent'),
        }

        # Mostra a tabela
        st.dataframe(df_stats, column_config=columns_config)

        # Colunas usadas no gráfico
        abs_cols = [
            "Diferença Mensal Abs.",
            "Média 6M Diferença Mensal Abs.",
            "Média 12M Diferença Mensal Abs.",
            "Média 24M Diferença Mensal Abs.",
        ]

        # Gráfico das diferenças
        st.line_chart(df_stats[abs_cols])

    # Área para cálculo de metas
    with st.expander('Metas'):

        # Divide a tela em duas colunas
        col1, col2 = st.columns(2)

        # Escolhe a data inicial da meta
        data_inicio_meta = col1.date_input(
            'Início de meta:',
            max_value=df_stats.index.max()
        )

        # Procura a última data disponível
        data_filtrada = df_stats.index[df_stats.index <= data_inicio_meta][-1]

        # Entradas de salário
        salario_bruto = col2.number_input('Salário Bruto:', min_value=0., format="%.2f")
        salario_liquido = col2.number_input('Salário Líquido:', min_value=0., format="%.2f")

        # Custos fixos mensais
        custos_fixos = col1.number_input('Custos fixos', min_value=0., format="%.2f")

        # Patrimônio inicial
        valor_inicio = df_stats.loc[data_filtrada, 'Valor']
        col1.markdown(f'**Valor no início da meta**: R${valor_inicio:.2f}')

        # Colunas para mostrar resultados
        col1_pot, col2_pot = st.columns(2)

        # Valor disponível para investir por mês
        mensal = salario_liquido - custos_fixos
        col1_pot.markdown(f'**Potencial arrecadação mensal**: R${mensal:.2f}')

        # Valor disponível em um ano
        anual = mensal * 12
        col2_pot.markdown(f'**Potencial arrecadação anual**: R${anual:.2f}')

        # Meta financeira
        col1_meta, col2_meta = st.columns(2)

        with col1_meta:
            meta_estipulada = st.number_input(
                'Meta estipulada',
                min_value=0.,
                format="%.2f"
            )

        with col2_meta:
            # Estimativa de patrimônio final
            patrimonio_final = meta_estipulada + valor_inicio
            st.markdown(f'Patrimônio estimado pós meta: R${patrimonio_final}')

        meses = pd.DataFrame({
            "Data referência":[data_inicio_meta + pd.DateOffset(months=1) for i in range(1, 13)],
            "Meta mensal": [valor_inicio + round(meta_estipulada/12, 2) * i for i in range(1, 13)]
            })
        meses["Data referência"] = meses["Data referência"].dt.strftime("%Y-%m    ")

        df_patrimonio = df_stats.reset_index()[["Data", "Valor"]]
        df_patrimonio["Data AnoMes"] = pd.to_datetime(df_patrimonio["Data"]).dt.strftime("%Y-%m")
        meses.merge(df_patrimonio, left_on="Data referência", right_on="Data AnoMes", how='left')

        st.dataframe(meses)
        st.text(meses)

# não tem arquivos