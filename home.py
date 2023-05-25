import os
import time
import math
import json
import pickle
import base64
import requests
import numpy as np
import pandas as pd
from PIL import Image
from fpdf import FPDF
import streamlit as st
import plotly.express as px
from htbuilder.units import rem
from streamlit_lottie import st_lottie
from htbuilder import div, big, h2, styles
from streamlit_option_menu import option_menu

COLOR_BLUE = "#1C83E1"
COLOR_RED = "#dd4f78"
COLOR_BLACK = '#186acc'

# Page layout
## Page expands to full width
st.set_page_config(
    page_title='SAD - GRSU - MS',
    page_icon='💻',
    layout='wide'
)

#hide_st_style = """
#            <style>
#            #MainMenu {visibility: hidden;}
#            footer {visibility: hidden;}
#            header {visibility: hidden;}
#            </style>
#           """
#st.markdown(hide_st_style, unsafe_allow_html=True)

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def display_dial(title, value, color):
    st.markdown(
        div(
            style=styles(
                text_align="center",
                color=color,
                padding=(rem(0.8), 0, rem(3), 0),
            )
        )(
            h2(style=styles(font_size=rem(0.9), font_weight=600, padding=0))(title),
            big(style=styles(font_size=rem(2.6), font_weight=800, line_height=1))(
                value
            ),
        ),
        unsafe_allow_html=True,
    )

def display_interval(title, value, color):
    st.markdown(
        div(
            style=styles(
                text_align="center",
                color=color,
                padding=(rem(0.8), 0, rem(3), 0),
            )
        )(
            h2(style=styles(font_size=rem(0.9), font_weight=600, padding=0))(title),
            big(style=styles(font_size=rem(2.1), font_weight=800, line_height=1))(
                value
            ),
        ),
        unsafe_allow_html=True,
    )

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# Menu sidebar
with st.sidebar:
    lottie_home = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_D2Bl7ZTvwe.json")
    st_lottie(
        lottie_home,
        speed=1,
        reverse=False,
        loop=False,
        quality="low", # medium ; high
        height=None,
        width=None,
        key=None,
    )
    selected = option_menu(
        menu_title=' ',
        options=["Início", "Predições", "Visualização", "Modelagem"],
        icons=["house-fill", "bar-chart-line-fill", "layers-half", "diagram-2-fill"],
        menu_icon="",
        default_index=0,
        orientation=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "", "font-size": "18px"},
            "nav-link": {
                "font-size": "18px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#29b9c2"},
        },
    )

    st.markdown("---")

# Page home
if selected == "Início":
    st.sidebar.info("Selecione uma opção acima", icon="ℹ️")
    col1, col2, col3 = st.columns(3)
    left_col, right_col = st.columns(2)

    with left_col:
        lottie_home = load_lottieurl("https://assets2.lottiefiles.com/temp/lf20_3bpCnZ.json")
        st_lottie(
            lottie_home,
            speed=0.6,
            reverse=False,
            loop=True,
            quality="low", # medium ; high
            height=None,
            width=400,
            key=None,
        )
        

    # Title and description
    right_col.markdown("# SAD GRS")
    right_col.markdown("### Uma ferramenta para o gerenciamento de resíduos sólidos")
    right_col.markdown("**Criado por João Marcos Soares Anjos**")
    right_col.markdown("**Universidade Federal de Mato Grosso do Sul**")
    
    st.markdown(
        """
        ### Sumário
        *SAD GRS* é um sistema de apoio à decisão, desenvolvido para auxiliar no gerenciamento de resíduos sólidos, 
        com o apoio do convênio técnico-científico entre MPMS, UEMS e outros órgãos como IMASUL, SEMAGRO e TCE.
        O sistema desenvolvido utiliza ferramentas de inteligência artificial para realizar a predição da geração de resíduos sólidos domiciliares,
        além de permitir a realização de projeções de geração de resíduos no tempo, e do volume de aterro.
        O modelo implementado utiliza o classificador Naive Bayes. 
        Existe também a opção de utilizar outros algoritmos classificadores, ou até mesmo desenvolver um outro modelo a partir dos dados.
        Os detalhes do sistema serão apresentados futuramente na dissertação.
        """
    )
    st.markdown("---")
    st.markdown(
        """
        ### Guia do usuário
        Localizado à esquerda da tela, existe um menu que possibilita a navegação entre 
        cada página do sistema *SAD GRS*:
        - **Início:** Apresentação do sistema!
        - **Predições:** Permite realizar inferências sobre a geração de resíduos sólidos por cada tipo de material.
        - **Visualização:** Possibilita a visualização mais detalhada sobre projeções da geração de resíduos, volume de aterro e proporção dos recicláveis.
        - **Modelagem:** Explora o desenvolvimento de um modelo a partir de dados de gravimetrias à nível domiciliar.
        """
    )
    st.markdown("---")

    left_info_col, middle_info_col, right_info_col = st.columns([2,1,1])

    # Contact
    left_info_col.markdown(
        f"""
        ### Autores
        Em caso de dúvidas ou sugestões, entre em contato.
        ##### João Marcos
        - Email:  <joaomarcoscomp@gmail.com>
        - Lattes: http://lattes.cnpq.br/8278312709865459
        - GitHub: https://github.com/joaomarcoscomp
        """,
        unsafe_allow_html=True,
    )

    with right_info_col:
        st.write(" ")
        image = Image.open('./images/projeto_rs.png')
        st.image(image, caption='Convênio técnico científico MPMS UEMS', width=200, use_column_width='never')
        
# Page predictions
if selected == "Predições":
    mat_color = COLOR_BLUE
    tot_color = COLOR_RED
    int_color = COLOR_BLACK

    c1, c2, c3 = st.columns([1,2,1]) 

    with c2:
        st.write(
            """
        # Estimativa da geração de resíduos
        Informe os respectivos dados para realizar a predição:
        """
        )

        files_dir = []
        dir_path = './models/'
        # Iterate directory
        for path in os.listdir(dir_path):
            # check if current path is a file
            if os.path.isfile(os.path.join(dir_path, path)):
                files_dir.append(path)
        print(files_dir)

        default_municipio = 'Campo Grande'

        f = open('./data/cidades_ms.json', encoding="utf8") 
        data = json.load(f)
        municipios = data['cidades']
        municipio = st.selectbox("Selecione o município", municipios,index=19)
        f.close()

        selected_model = st.selectbox("Selecione o modelo", list(files_dir), 0)
        model_path = './models/' + selected_model
        loaded_model = pickle.load(open(model_path, 'rb'))

        st.write(
            """
        ### Enviar relação dos domicílios
        Selecione o arquivo contendo a relação com os valores de IPTU para cada domicílio do município:
        """
        )
        
        uploaded_file = st.file_uploader("Enviar arquivo .XLSX", type=".xlsx")

        use_default_iptu = st.checkbox(
            "Usar relação padrão (Campo Grande)", False, help="Use a planilha com a relação dos domicílios de Campo Grande"
        )

    df = []
    if use_default_iptu:
        with c2:
            st.markdown("---")

            #load data from disk
            file_loc = './data/IPTU_MEDIO_RESIDENCIAL_CG.xlsx'

            with st.spinner('Carregando dados...'):
                df = pd.read_excel(file_loc)
            st.success('Pronto!')
            
        uploaded_file = file_loc

    if uploaded_file:
        with c2:

            if not use_default_iptu:
                st.markdown("---")

                with st.spinner('Carregando dados...'):
                    #load data from de uploaded file
                    df = pd.read_excel(uploaded_file)
                st.success('Pronto!')

        iptu = df['IPTU']
        res_clas = loaded_model.predict(iptu.to_frame())
        qntd_clas = pd.Series(res_clas).value_counts()
        qntd_dom = len(iptu)

        if(selected_model == 'Classificacao.sav'):
            media_classe_1 = pickle.load(open('./data/media_classe_1.sav', 'rb'))
            media_classe_2 = pickle.load(open('./data/media_classe_2.sav', 'rb'))
            media_classe_3 = pickle.load(open('./data/media_classe_3.sav', 'rb'))
            margem_classe_1 = pickle.load(open('./data/margem_classe_1.sav', 'rb'))
            margem_classe_2 = pickle.load(open('./data/margem_classe_2.sav', 'rb'))
            margem_classe_3 = pickle.load(open('./data/margem_classe_3.sav', 'rb'))
            media_p_emb_1 = pickle.load(open('./data/media_emb_1.sav', 'rb'))
            media_p_emb_2 = pickle.load(open('./data/media_emb_2.sav', 'rb'))
            media_p_emb_3 = pickle.load(open('./data/media_emb_3.sav', 'rb'))
            st.write(qntd_clas[1])
            st.write(qntd_clas[2])

            if(len(qntd_clas) == 1):
                total_classe_1 = media_classe_1 * qntd_clas[1]
                perc_marg_1 = margem_classe_1 / media_classe_1
                margemxpeso_1 = perc_marg_1 * qntd_clas[1]
                soma_mxp = margemxpeso_1
                soma_p = qntd_clas[1]
                saida = total_classe_1
                media_classes = media_classe_1
                media_p_emb = media_p_emb_1
            elif (len(qntd_clas) == 2):
                total_classe_1 = media_classe_1 * qntd_clas[1]
                total_classe_2 = media_classe_2 * qntd_clas[2]
                perc_marg_1 = margem_classe_1 / media_classe_1
                perc_marg_2 = margem_classe_2 / media_classe_2
                margemxpeso_1 = perc_marg_1 * qntd_clas[1]
                margemxpeso_2 = perc_marg_2 * qntd_clas[2]
                soma_mxp = margemxpeso_1 + margemxpeso_2
                soma_p = qntd_clas[1] + qntd_clas[2]
                saida = total_classe_1 + total_classe_2
                media_classes = media_classe_1 + media_classe_2 / 2
                media_p_emb = media_p_emb_1 + media_p_emb_2 / 2
            else:
                total_classe_1 = media_classe_1 * qntd_clas[1]
                total_classe_2 = media_classe_2 * qntd_clas[2]
                total_classe_3 = media_classe_3 * qntd_clas[3]
                perc_marg_1 = margem_classe_1 / media_classe_1
                perc_marg_2 = margem_classe_2 / media_classe_2
                perc_marg_3 = margem_classe_3 / media_classe_3
                margemxpeso_1 = perc_marg_1 * qntd_clas[1]
                margemxpeso_2 = perc_marg_2 * qntd_clas[2]
                margemxpeso_3 = perc_marg_3 * qntd_clas[3]
                soma_mxp = margemxpeso_1 + margemxpeso_2 + margemxpeso_3
                soma_p = qntd_clas[1] + qntd_clas[2] + qntd_clas[3]
                saida = total_classe_1 + total_classe_2 + total_classe_3
                media_classes = media_classe_1 + media_classe_2 + media_classe_3 / 3
                media_p_emb = media_p_emb_1 + media_p_emb_2 + media_p_emb_3 / 3
            
            media_p = soma_mxp / soma_p
            margem_err = media_p * saida
        else:
            st.write(" Ainda estamos trabalhando nisso...")

        plastico_g = saida['Plástico']
        papel_g = saida['Papel e Papelão']
        vidro_g = saida['Vidro']
        metais_g = saida['Metais']
        emb_m_g = saida['Emb. Mult.']
        tex_g = saida['Tex. Cour. Bor.']
        mat_g = saida['Mat. Org.']
        rej_g = saida['Rejeitos']

        plastico = round(saida['Plástico'].astype(float) / 1000000, 2)
        papel = round(saida['Papel e Papelão'].astype(float) / 1000000, 2)
        vidro = round(saida['Vidro'].astype(float) / 1000000, 2)
        metais = round(saida['Metais'].astype(float) / 1000000, 2)
        emb_m = round(saida['Emb. Mult.'].astype(float) / 1000000, 2)
        tex = round(saida['Tex. Cour. Bor.'].astype(float) / 1000000, 2)
        mat = round(saida['Mat. Org.'].astype(float) / 1000000, 2)
        rej = round(saida['Rejeitos'].astype(float) / 1000000, 2)

        total = plastico_g + papel_g + vidro_g + metais_g + emb_m_g + tex_g + mat_g + rej_g
        total_rec = plastico_g + papel_g + vidro_g + metais_g + emb_m_g + tex_g
        total_n_rec = mat_g + rej_g
        proporcao = saida / total[0]
        total_ton = round(total.astype(float) / 1000000, 2)
        total_text = str(total_ton[0]).replace('.', ',') + "t"

        m_plast_sup = round(margem_err['Plástico'][0].astype(float) / 1000000+plastico[0],2)
        m_papel_sup = round(margem_err['Papel e Papelão'][0].astype(float) / 1000000+papel[0],2)
        m_vidro_sup = round(margem_err['Vidro'][0].astype(float) / 1000000+vidro[0],2)
        m_met_sup = round(margem_err['Metais'][0].astype(float) / 1000000+metais[0],2)
        m_emb_sup = round(margem_err['Emb. Mult.'][0].astype(float) / 1000000+emb_m[0],2)
        m_tex_sup = round(margem_err['Tex. Cour. Bor.'][0].astype(float) / 1000000+tex[0],2)
        m_mat_sup = round(margem_err['Mat. Org.'][0].astype(float) / 1000000+mat[0],2)
        m_rej_sup = round(margem_err['Rejeitos'][0].astype(float) / 1000000+rej[0],2)
        if math.isnan(m_tex_sup):
            sum_sup = m_plast_sup + m_papel_sup + m_vidro_sup + m_met_sup + m_emb_sup + m_mat_sup + m_rej_sup
        else:
            sum_sup = m_plast_sup + m_papel_sup + m_vidro_sup + m_met_sup + m_emb_sup + m_tex_sup + m_mat_sup + m_rej_sup

        m_plast_inf = round(plastico[0]-margem_err['Plástico'][0].astype(float) / 1000000, 2)
        m_papel_inf = round(papel[0]-margem_err['Papel e Papelão'][0].astype(float) / 1000000, 2)
        m_vidro_inf = round(vidro[0]-margem_err['Vidro'][0].astype(float) / 1000000, 2)
        m_met_inf = round(metais[0]-margem_err['Metais'][0].astype(float) / 1000000, 2)
        m_emb_inf = round(emb_m[0]-margem_err['Emb. Mult.'][0].astype(float) / 1000000, 2)
        m_tex_inf = round(tex[0]-margem_err['Tex. Cour. Bor.'][0].astype(float) / 1000000, 2)
        m_mat_inf = round(mat[0]-margem_err['Mat. Org.'][0].astype(float) / 1000000, 2)
        m_rej_inf = round(rej[0]-margem_err['Rejeitos'][0].astype(float) / 1000000, 2)
        if math.isnan(m_tex_inf):
            sum_inf = m_plast_inf + m_papel_inf + m_vidro_inf + m_met_inf + m_emb_inf + m_mat_inf + m_rej_inf
        else:
            sum_inf = m_plast_inf + m_papel_inf + m_vidro_inf + m_met_inf + m_emb_inf + m_tex_inf + m_mat_inf + m_rej_inf

        c1, c2, c3 = st.columns(3)
        with c1:
            for i in range(1,15):
                st.write(" ")
            display_dial("Intervalo de confiança inferior", round(sum_inf,2), mat_color)

        with c2:
            tot_domicilio = f'{len(df):,}'.replace(',', '.')
            st.write("## ", municipio)
            display_dial("Total de domicílios ", tot_domicilio, mat_color)
            display_dial("Geração Domiciliar (Total por dia)", total_text, mat_color)

        with c3:
            for i in range(1,15):
                st.write(" ")
            display_dial("Intervalo de confiança superior", round(sum_sup,2), tot_color)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h3 style='text-align: center;'>Geração de materiais</h3>", unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: center;'>Valor estimado</h5>", unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")

            display_dial("PLÁSTICO", str(plastico[0]).replace('.', ',') + "t", mat_color)
            display_dial("PAPEL E PAPELÃO", str(papel[0]).replace('.', ',') + "t", mat_color)
            display_dial("VIDRO", str(vidro[0]).replace('.', ',') + "t", mat_color)
            display_dial("METAIS", str(metais[0]).replace('.', ',') + "t", mat_color)
            display_dial("EMB. MULTICAMADAS", str(emb_m[0]).replace('.', ',') + "t", mat_color)
            display_dial("TEX. COUR. BOR.", str(tex[0]).replace('.', ',') + "t", mat_color)
            display_dial("MAT. ORGANICA", str(mat[0]).replace('.', ',') + "t", mat_color)
            display_dial("REJEITOS", str(rej[0]).replace('.', ',') + "t", mat_color)

        with c2:
            st.markdown("<h3 style='text-align: center;'>Intervalos de confiança</h3>", unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: center;'>Estatística</h5>", unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")

            display_dial("PLÁSTICO", str(m_plast_inf).replace('.', ',') + ' — ' + str(m_plast_sup).replace('.', ',') + " t", int_color)
            display_dial("PAPEL E PAPELÃO", str(m_papel_inf).replace('.', ',') + ' — ' + str(m_papel_sup).replace('.', ',') + " t", int_color)
            display_dial("VIDRO", str(m_vidro_inf).replace('.', ',') + ' — ' + str(m_vidro_sup).replace('.', ',') + " t", int_color)
            display_dial("METAIS", str(m_met_inf).replace('.', ',') + ' — ' + str(m_met_sup).replace('.', ',') + " t", int_color)
            display_dial("EMB. MULTICAMADAS", str(m_emb_inf).replace('.', ',') + ' — ' + str(m_emb_sup).replace('.', ',') + " t", int_color)
            display_dial("TEX. COUR. BOR.", str(m_tex_inf).replace('.', ',') + ' — ' + str(m_tex_sup).replace('.', ',') + " t", int_color)
            display_dial("MAT. ORGANICA", str(m_mat_inf).replace('.', ',') + ' — ' + str(m_mat_sup).replace('.', ',') + " t", int_color)
            display_dial("REJEITOS", str(m_rej_inf).replace('.', ',') + ' — ' + str(m_rej_sup).replace('.', ',') + " t", int_color)

        names = ['Plástico','Papel e Papelão','Vidro','Metais','Emb. Mult.','Tex. Cour. Bor.','Mat. Org.','Rejeitos']
        df_prop = proporcao.transpose().reset_index(drop=True)
        df_prop = df_prop.rename(columns={0: 'Proporcao'})
        df_pie = pd.concat([df_prop, pd.DataFrame(names)], axis=1)
        df_pie = df_pie.rename(columns={0: 'Material'})
        
        fig = px.pie(df_pie, values=df_pie['Proporcao'], names=df_pie['Material'], title='Proporção dos resíduos sólidos')
        
        c1, c2, c3 = st.columns([1,2,1]) 
        with c2:
            st.write(fig)

        m_plast_sup_g = margem_err['Plástico'][0] +plastico_g[0]
        m_papel_sup_g = margem_err['Papel e Papelão'][0] +papel_g[0]
        m_vidro_sup_g = margem_err['Vidro'][0] +vidro_g[0]
        m_met_sup_g = margem_err['Metais'][0] +metais_g[0]
        m_emb_sup_g = margem_err['Emb. Mult.'][0] +emb_m_g[0]
        m_tex_sup_g = margem_err['Tex. Cour. Bor.'][0] +tex_g[0]
        m_mat_sup_g = margem_err['Mat. Org.'][0] +mat_g[0]
        m_rej_sup_g = margem_err['Rejeitos'][0] +rej_g[0]
        sum_sup_g_n_rec = m_mat_sup_g + m_rej_sup_g

        if math.isnan(m_tex_sup):
            sum_sup_g = m_plast_sup_g + m_papel_sup_g + m_vidro_sup_g + m_met_sup_g + m_emb_sup_g + m_mat_sup_g + m_rej_sup_g
            sum_sup_g_rec = m_plast_sup_g + m_papel_sup_g + m_vidro_sup_g + m_met_sup_g + m_emb_sup_g
        else:
            sum_sup_g = m_plast_sup_g + m_papel_sup_g + m_vidro_sup_g + m_met_sup_g + m_emb_sup_g + m_tex_sup_g + m_mat_sup_g + m_rej_sup_g
            sum_sup_g_rec = m_plast_sup_g + m_papel_sup_g + m_vidro_sup_g + m_met_sup_g + m_emb_sup_g + m_tex_sup_g

        dictionary = {
            "plastico": m_plast_sup_g,
            "papel": m_papel_sup_g,
            "vidro": m_vidro_sup_g,
            "metais": m_met_sup_g,
            "emb_m": m_emb_sup_g,
            "tex": m_tex_sup_g,
            "mat": m_mat_sup_g,
            "rej": m_rej_sup_g,
            "total": sum_sup_g,
            "total_rec": sum_sup_g_rec,
            "total_n_rec": sum_sup_g_n_rec,
            "qntd_clas_1": qntd_clas[1],
            "qntd_clas_2": qntd_clas[2],
            "qntd_dom": qntd_dom,
            "media_plast": media_classes['Plástico'][0],
            "media_papel": media_classes['Papel e Papelão'][0],
            "media_vid": media_classes['Vidro'][0],
            "media_met": media_classes['Metais'][0],
            "media_emb": media_classes['Emb. Mult.'][0],
            "media_tex": media_classes['Tex. Cour. Bor.'][0],
            "media_mat": media_classes['Mat. Org.'][0],
            "media_rej": media_classes['Rejeitos'][0],
            "media_p_emb": media_p_emb['P_Emb'][0],
            "media_p_n_emb": media_p_emb['P_N_Emb'][0]
        }

        arquivo = json.dumps(dictionary, cls=NpEncoder)
        with open("./data/result.json", "w") as outfile:
            outfile.write(arquivo)

        with c2:
            st.info("No menu **Visualização**, você terá acesso à mais opções.", icon='ℹ️')

# Page visualization
if selected == "Visualização":
    # Verify if the results exists
    files = os.listdir('./data/')
    is_there = "result.json" in files

    a, b, c= st.columns([1, 2, 1])

    b.write(
        """
    # Visualização
    Informe os parâmetros para calcular as projeção:
    """
    )

    medida = ['Tonelada (t)', 'Quilograma (kg)', 'Grama (g)']
    tempo = ['Dia', 'Mês', 'Ano']
    tipo = ['Domiciliar', 'Por pessoa']
    
    a, b, c, d = st.columns([1, 1, 1, 1])
    medida_proj = b.selectbox("Selecione a unidade de medida:", medida)
    tempo_proj = c.selectbox("Selecione o tempo:", tempo)

    
    tipo_proj = b.selectbox("Selecione o tipo de geração:", tipo)
    if tipo_proj == 'Por pessoa':
        media_pessoa = c.slider('Informe a média de pessoa por domicílio:', 1, 10, 3)

    material_tipo = c.radio(
        "Material:",
        ('Recicláveis', 'Não-recicláveis', 'Total (Não-recicláveis + recicláveis)'))

    c.write(" ")

    if medida_proj == 'Tonelada (t)':
        calc_volume = b.checkbox('Calcular volume de aterro')
        if calc_volume:
            den_comp = b.slider('Densidade compactada (ton/m³)', 0.6, 0.8, 0.6)
    else:
        calc_volume = 0

    comp_emb = b.checkbox('Exibir a proporção de embalagens e não embalagens')

    gerar = b.button('Gerar projeções')

    if gerar:
        if is_there:
            st.markdown("---")

            st.markdown("<h3 style='text-align: center;'>Projeções sobre gestão de resíduos sólidos </h3>", unsafe_allow_html=True)
            
            with open('./data/result.json', 'r') as openfile:
                # Reading from json file
                arquivo = json.load(openfile)
            plastico = arquivo["plastico"]
            papel = arquivo["papel"]
            vidro = arquivo["vidro"]
            metais = arquivo["metais"]
            emb_m = arquivo["emb_m"]
            tex = arquivo["tex"]
            mat = arquivo["mat"]
            rej = arquivo["rej"]
            total = arquivo["total"]
            total_rec = arquivo["total_rec"]
            total_n_rec = arquivo["total_n_rec"]
            qntd_clas_1 = arquivo["qntd_clas_1"]
            qntd_clas_2 = arquivo["qntd_clas_2"]
            qntd_dom = arquivo["qntd_dom"]
            media_plast = arquivo["media_plast"]
            media_papel = arquivo["media_papel"]
            media_vid = arquivo["media_vid"]
            media_met = arquivo["media_met"]
            media_emb = arquivo["media_emb"]
            media_tex = arquivo["media_tex"]
            media_mat = arquivo["media_mat"]
            media_rej = arquivo["media_rej"]
            media_p_emb = arquivo["media_p_emb"]
            media_p_n_emb = arquivo["media_p_n_emb"]

            names = ['Plástico','Papel e Papelão','Vidro','Metais','Emb. Mult.','Tex. Cour. Bor.','Mat. Org.','Rejeitos']
            materiais = [plastico, papel, vidro, metais, emb_m, tex, mat, rej]
            media_classes = [media_plast, media_papel, media_vid, media_met, media_emb, media_tex, media_mat, media_rej]
            media_p_emb = [media_p_emb, media_p_n_emb]
            mat_color = COLOR_BLUE
            tot_color = COLOR_RED

            c1, c2, c3 = st.columns(3)
            
            # Material
            if material_tipo == "Recicláveis":
                materiais = [materiais[0], materiais[1], materiais[2], materiais[3], materiais[4], materiais[5]]
                media_classes = [media_classes[0],media_classes[1],media_classes[2],media_classes[3],media_classes[4],media_classes[5]]
                names = ['Plástico','Papel e Papelão','Vidro','Metais','Emb. Mult.','Tex. Cour. Bor.']

                ###
                if tipo_proj == 'Por pessoa':
                    var_res = []
                    var_total_rec = 0
                    for material in materiais:
                        var_res.append((material / qntd_dom)/media_pessoa)
                        var_total_rec += (material / qntd_dom)/media_pessoa
                    materiais = var_res
                    total_rec = var_total_rec

                if tempo_proj == 'Mês':
                    var_res = []
                    for material in materiais:
                        var_res.append(material * 30)
                    materiais = var_res
                    total_rec = total_rec * 30
                elif tempo_proj == 'Ano':
                    var_res = []
                    for material in materiais:
                        var_res.append(material * 365)
                    materiais = var_res
                    total_rec = total_rec * 365
                else: # Dia
                    st.write('')

                total_v = total_rec

                # Medidas
                if medida_proj == "Tonelada (t)":
                    var_res = []
                    for material in materiais:
                        var_res.append(material / 1000000)
                    materiais = var_res
                    total_v = total_v / 1000000
                    st.write(" ")
                    
                    if tipo_proj == 'Por pessoa':
                        with c1:
                            display_dial("PLÁSTICO", str(f'{materiais[0]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("PAPEL E PAPELÃO", str(f'{materiais[1]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("VIDRO", str(f'{materiais[2]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("METAIS", str(f'{materiais[3]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("EMB. MULTICAMADAS", str(f'{materiais[4]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("TEX. COUR. BOR.", str(f'{materiais[5]:.6f}').replace('.', ',') + "t", mat_color)
                            st.write(" ")
                            st.write(" ")
                            display_dial("TOTAL", str(f'{total_v:.6f}').replace('.', ',') + "t", tot_color)
                    else:
                        with c1:
                            display_dial("PLÁSTICO", str(round(materiais[0],2)).replace('.', ',') + "t", mat_color)
                            display_dial("PAPEL E PAPELÃO", str(round(materiais[1],2)).replace('.', ',') + "t", mat_color)
                            display_dial("VIDRO", str(round(materiais[2],2)).replace('.', ',') + "t", mat_color)
                            display_dial("METAIS", str(round(materiais[3],2)).replace('.', ',') + "t", mat_color)
                            display_dial("EMB. MULTICAMADAS", str(round(materiais[4],2)).replace('.', ',') + "t", mat_color)
                            display_dial("TEX. COUR. BOR.", str(round(materiais[5],2)).replace('.', ',') + "t", mat_color)
                            st.write(" ")
                            st.write(" ")
                            display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "t", tot_color)

                elif medida_proj == 'Quilograma (kg)':
                    var_res = []
                    for material in materiais:
                        var_res.append(material / 1000)
                    materiais = var_res
                    total_v = total_v / 1000
                    st.write(" ")
                    
                    with c1:
                        display_dial("PLÁSTICO", str(round(materiais[0],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("PAPEL E PAPELÃO", str(round(materiais[1],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("VIDRO", str(round(materiais[2],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("METAIS", str(round(materiais[3],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("EMB. MULTICAMADAS", str(round(materiais[4],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("TEX. COUR. BOR.", str(round(materiais[5],2)).replace('.', ',') + "kg", mat_color)
                        st.write(" ")
                        st.write(" ")
                        display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "kg", tot_color)

                else: # medida == Grama (g)
                    st.write(" ")
                    with c1:
                        display_dial("PLÁSTICO", str(round(materiais[0],2)).replace('.', ',') + "g", mat_color)
                        display_dial("PAPEL E PAPELÃO", str(round(materiais[1],2)).replace('.', ',') + "g", mat_color)
                        display_dial("VIDRO", str(round(materiais[2],2)).replace('.', ',') + "g", mat_color)
                        display_dial("METAIS", str(round(materiais[3],2)).replace('.', ',') + "g", mat_color)
                        display_dial("EMB. MULTICAMADAS", str(round(materiais[4],2)).replace('.', ',') + "g", mat_color)
                        display_dial("TEX. COUR. BOR.", str(round(materiais[5],2)).replace('.', ',') + "g", mat_color)
                        st.write(" ")
                        st.write(" ")
                        display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "g", tot_color)

            elif material_tipo == "Não-recicláveis":
                materiais = [materiais[6], materiais[7]]
                media_classes = [media_classes[6],media_classes[7]]
                names = ['Mat. Org.','Rejeitos']

                if tipo_proj == 'Por pessoa':
                    var_res = []
                    var_total_n_rec = 0
                    for material in materiais:
                        var_res.append((material / qntd_dom)/media_pessoa)
                        var_total_n_rec += (material / qntd_dom)/media_pessoa
                    materiais = var_res
                    total_n_rec = var_total_n_rec

                if tempo_proj == 'Mês':
                    var_res = []
                    for material in materiais:
                        var_res.append(material * 30)
                    materiais = var_res
                    total_n_rec = total_n_rec * 30
                elif tempo_proj == 'Ano':
                    var_res = []
                    for material in materiais:
                        var_res.append(material * 365)
                    materiais = var_res
                    total_n_rec = total_n_rec * 365
                else: # Dia
                    st.write('')

                total_v = total_n_rec

                # Medidas
                if medida_proj == "Tonelada (t)":
                    var_res = []
                    for material in materiais:
                        var_res.append(material / 1000000)
                    materiais = var_res
                    total_v = total_v / 1000000
                    st.write(" ")

                    if tipo_proj == 'Por pessoa':
                        with c1:
                            display_dial("MAT. ORGANICA", str(f'{materiais[0]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("REJEITOS", str(f'{materiais[1]:.6f}').replace('.', ',') + "t", mat_color)
                            st.write(" ")
                            st.write(" ")
                            display_dial("TOTAL", str(f'{total_v:.6f}').replace('.', ',') + "t", tot_color)
                    else:
                        with c1:
                            display_dial("MAT. ORGANICA", str(round(materiais[0],2)).replace('.', ',') + "t", mat_color)
                            display_dial("REJEITOS", str(round(materiais[1],2)).replace('.', ',') + "t", mat_color)
                            st.write(" ")
                            st.write(" ")
                            display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "t", tot_color)

                elif medida_proj == 'Quilograma (kg)':
                    var_res = []
                    for material in materiais:
                        var_res.append(material / 1000)
                    materiais = var_res
                    total_v = total_v / 1000

                    with c1:
                        display_dial("MAT. ORGANICA", str(round(materiais[0],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("REJEITOS", str(round(materiais[1],2)).replace('.', ',') + "kg", mat_color)
                        st.write(" ")
                        st.write(" ")
                        display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "kg", tot_color)

                else: # medida == Grama (g)
                    with c1:
                        display_dial("MAT. ORGANICA", str(round(materiais[0],2)).replace('.', ',') + "g", mat_color)
                        display_dial("REJEITOS", str(round(materiais[1],2)).replace('.', ',') + "g", mat_color)
                        st.write(" ")
                        st.write(" ")
                        display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "g", tot_color)

            else:
                ###
                ###
                if tipo_proj == 'Por pessoa':
                    var_res = []
                    var_total = 0
                    for material in materiais:
                        var_res.append((material / qntd_dom)/media_pessoa)
                        var_total += (material / qntd_dom)/media_pessoa
                    materiais = var_res
                    total = var_total

                if tempo_proj == 'Mês':
                    var_res = []
                    for material in materiais:
                        var_res.append(material * 30)
                    materiais = var_res
                    total = total * 30
                elif tempo_proj == 'Ano':
                    var_res = []
                    for material in materiais:
                        var_res.append(material * 365)
                    materiais = var_res
                    total = total * 365
                else: # Dia
                    st.write('')

                total_v = total

                # Medidas
                if medida_proj == "Tonelada (t)":
                    var_res = []
                    for material in materiais:
                        var_res.append(material / 1000000)
                    materiais = var_res
                    total_v = total_v / 1000000
                    st.write(" ")

                    if tipo_proj == 'Por pessoa':
                        with c1:
                            display_dial("PLÁSTICO", str(f'{materiais[0]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("PAPEL E PAPELÃO", str(f'{materiais[1]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("VIDRO", str(f'{materiais[2]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("METAIS", str(f'{materiais[3]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("EMB. MULTICAMADAS", str(f'{materiais[4]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("TEX. COUR. BOR.", str(f'{materiais[5]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("MAT. ORGANICA", str(f'{materiais[6]:.6f}').replace('.', ',') + "t", mat_color)
                            display_dial("REJEITOS", str(f'{materiais[7]:.6f}').replace('.', ',') + "t", mat_color)
                            st.write(" ")
                            st.write(" ")
                            display_dial("TOTAL", str(f'{total_v:.6f}').replace('.', ',') + "t", tot_color)
                    else:
                        with c1:
                            display_dial("PLÁSTICO", str(round(materiais[0],2)).replace('.', ',') + "t", mat_color)
                            display_dial("PAPEL E PAPELÃO", str(round(materiais[1],2)).replace('.', ',') + "t", mat_color)
                            display_dial("VIDRO", str(round(materiais[2],2)).replace('.', ',') + "t", mat_color)
                            display_dial("METAIS", str(round(materiais[3],2)).replace('.', ',') + "t", mat_color)
                            display_dial("EMB. MULTICAMADAS", str(round(materiais[4],2)).replace('.', ',') + "t", mat_color)
                            display_dial("TEX. COUR. BOR.", str(round(materiais[5],2)).replace('.', ',') + "t", mat_color)
                            display_dial("MAT. ORGANICA", str(round(materiais[6],2)).replace('.', ',') + "t", mat_color)
                            display_dial("REJEITOS", str(round(materiais[7],2)).replace('.', ',') + "t", mat_color)
                            st.write(" ")
                            st.write(" ")
                            display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "t", tot_color)

                elif medida_proj == 'Quilograma (kg)':
                    var_res = []
                    for material in materiais:
                        var_res.append(material / 1000)
                    materiais = var_res
                    total_v = total_v / 1000
                    st.write(" ")
                    
                    with c1:
                        display_dial("PLÁSTICO", str(round(materiais[0],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("PAPEL E PAPELÃO", str(round(materiais[1],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("VIDRO", str(round(materiais[2],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("METAIS", str(round(materiais[3],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("EMB. MULTICAMADAS", str(round(materiais[4],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("TEX. COUR. BOR.", str(round(materiais[5],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("MAT. ORGANICA", str(round(materiais[6],2)).replace('.', ',') + "kg", mat_color)
                        display_dial("REJEITOS", str(round(materiais[7],2)).replace('.', ',') + "kg", mat_color)
                        st.write(" ")
                        st.write(" ")
                        display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "kg", tot_color)

                else: # medida == Grama (g)
                    st.write(" ")
                    with c1:
                        display_dial("PLÁSTICO", str(round(materiais[0],2)).replace('.', ',') + "g", mat_color)
                        display_dial("PAPEL E PAPELÃO", str(round(materiais[1],2)).replace('.', ',') + "g", mat_color)
                        display_dial("VIDRO", str(round(materiais[2],2)).replace('.', ',') + "g", mat_color)
                        display_dial("METAIS", str(round(materiais[3],2)).replace('.', ',') + "g", mat_color)
                        display_dial("EMB. MULTICAMADAS", str(round(materiais[4],2)).replace('.', ',') + "g", mat_color)
                        display_dial("TEX. COUR. BOR.", str(round(materiais[5],2)).replace('.', ',') + "g", mat_color)
                        display_dial("MAT. ORGANICA", str(round(materiais[6],2)).replace('.', ',') + "g", mat_color)
                        display_dial("REJEITOS", str(round(materiais[7],2)).replace('.', ',') + "g", mat_color)
                        st.write(" ")
                        st.write(" ")
                        display_dial("TOTAL", str(round(total_v,2)).replace('.', ',') + "g", tot_color)

            materiais_g = materiais

            # Resultados
            proporcao = []
            for i in materiais_g:
                proporcao.append(i / total_v)
            proporcao = pd.DataFrame(proporcao)

            #colors_pie = ['Plástico','Papel e Papelão','Vidro','Metais','Emb. Mult.','Tex. Cour. Bor.','Mat.Org.']
            colors_pie = ['#4e90cd','#46936e','#adc7cf','#565a68','#f1bd5d','#e48a37','#b25b32','#28333d']

            df_prop = proporcao.rename(columns={0: 'Proporcao'})
            df_pie = pd.concat([df_prop, pd.DataFrame(names)], axis=1)
            df_pie = df_pie.rename(columns={0: 'Material'})
            fig = px.pie(df_pie, values=df_pie['Proporcao'], names=df_pie['Material'], title='Proporção dos resíduos')
            fig.update_traces(marker=dict(colors=colors_pie))
            c2.write(fig)

            if calc_volume:
                if material_tipo == "Recicláveis":
                    total = total_rec / 1000000
                elif material_tipo == "Não-recicláveis":
                    total = total_n_rec / 1000000
                else:
                    total = total / 1000000

                volume_at = total / den_comp

                with c2:
                    st.markdown("<h5 style='text-align: center;'>Volume de aterro (ton)</h5>", unsafe_allow_html=True)
                    display_dial("VOLUME", str(round(volume_at,2)).replace('.', ',') + " t", mat_color)

            if comp_emb:
                proporcao = []
                proporcao = pd.DataFrame(media_p_emb)
                names = ['Embalagem','Não-embalagem']
                df_prop = proporcao.rename(columns={0: 'Proporcao'})
                df_pie = pd.concat([df_prop, pd.DataFrame(names)], axis=1)
                df_pie = df_pie.rename(columns={0: 'Material'})
                fig = px.pie(df_pie, values=df_pie['Proporcao'], names=df_pie['Material'], title='Proporção dos resíduos')
                c2.write(fig)

        else: # First run
            c1, c2, c3 = st.columns([1,2,1])
            st.write(' ')
            c2.error("É necessário primeiramente **realizar a predição** para visualizar os resultados.", icon="🤖")

# Page models
if selected == "Modelagem":
    a, b, c= st.columns([1, 2, 1])

    b.write(
        """
    # Modelagem
    Informe os parâmetros para construir um modelo de estimação:
    """
    )

    files_dir = []
    dir_path = './models/'
    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            files_dir.append(path)
    print(files_dir)

    default_municipio = 'Campo Grande'

    f = open('./data/cidades_ms.json', encoding="utf8") 
    data = json.load(f)
    municipios = data['cidades']
    municipio = b.selectbox("Selecione o município", municipios,index=19)
    f.close()

    new_gravimetria = b.checkbox('Enviar novos dados de gravimetria')
    if new_gravimetria:
            new_uploaded = b.file_uploader("Enviar arquivo .XLSX", type=".xlsx")

    new_param = b.checkbox('Alterar parâmetros do modelo')
    if new_param:
        selected_model = b.selectbox("Selecione o modelo", list(files_dir), 0)
        model_path = './models/' + selected_model
        loaded_model = pickle.load(open(model_path, 'rb'))

        qntd_clas_box = ['1', '2', '3', '4', '5', '6', '7']
        tipo_k = ['Linear', 'RBF','Sigmoid']
        
        a, b, c, d = st.columns([1, 1, 1, 1])
        param_clas = b.selectbox("Selecione a quantidade de classes:", qntd_clas_box)
        param_prop_train_test = c.slider('Informe a proporção de dados de teste:', 0.1, 1.0, 0.3)

        tipo_kernel = b.selectbox("Selecione o tipo de kernel:", tipo_k)

    c.write(" ")

    gerar = b.button('Treinar modelo')