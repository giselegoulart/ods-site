import base64
from email.mime import base
from os import sep
from tempfile import gettempdir
from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib import messages
from .email import EmailSender
import time, glob, io
import csv as Csv


# importando bibliotecas

import pandas as pd
import math
import numpy as np
import glob
import unicodedata
import re
import nltk
import MySQLdb as mdb
import seaborn as sns
import matplotlib.pyplot as plt
import pdfplumber
from matplotlib.collections import QuadMesh

def index(request):
    return render(request, 'index.html')

def mapeamento(request):
    return render(request, 'mapeamento.html')

def sobre_ods(request):
    return render(request, 'sobre-os-ods.html')

def sobre_ferramenta(request):
    return render(request, 'sobre-a-ferramenta.html')

def sobre_nos(request):
    return render(request, 'sobre-nos.html')

def noticias(request):
    return render(request, 'noticias.html')

# def upload(request):
#     if request.method == 'POST' and request.FILES:
#         uploaded_file = request.FILES['file']
#         fs = FileSystemStorage()
#         if not request.session.session_key:
#             request.session.create()
#         name = fs.save(f"{uploaded_file.name.split('.csv')[0]}_key!{request.session.session_key}.csv", uploaded_file)
#         # print(name)
#         url = fs.url(name)
#         request.session['csv'] = url
#         request.session['csv-name'] = name
#         # print(f"{uploaded_file.name}: size {uploaded_file.size/1000} KB\nURL: {url}")
#         # return render(request, 'mapeamento.html', {'url': url})
#         return redirect('processamento')
#     elif request.method == 'GET':
#         # print('get')
#         return redirect('mapeamento')
#     else:
#         return redirect('mapeamento')

def upload(request):
    if request.method == 'POST' and request.FILES:
        uploaded_file = request.FILES['file']
        if not request.session.session_key:
            request.session.create()

        if uploaded_file.name[-4:len(uploaded_file):] == '.csv':
            csv_file = request.FILES['file']
            ret = map_csv(request, csv_file)
            
            return render(request, 'resultado.html', {'csv': ret[0], 'heatmap': ret[1]})

        elif uploaded_file.name[-4:len(uploaded_file):] == '.pdf':
            # name = fs.save(f"{uploaded_file.name.split('.pdf')[0]}_key!{request.session.session_key}.pdf", uploaded_file)
            # url = fs.url(name)
            # request.session['pdf'] = url
            # request.session['pdf-name'] = name
            # return redirect('resultado-pdf')
            pdf_file = request.FILES['file']
            ret = map_pdf(request, pdf_file)
            return render(request, 'resultado.html', {'csv': ret[0], 'heatmap': ret[1]})

        messages.error(request, "A extensão do arquivo enviado é invalida! Por favor, envie apenas arquivos .csv ou .pdf.")
        return redirect('mapeamento')
    elif request.method == 'GET':
        return redirect('mapeamento')
    else:
        return redirect('mapeamento')


def map_csv(request, csv_file):
    decoded_file = csv_file.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    # file = pd.read_csv(io_string, sep=';')

    # if request.method != "GET" or not 'csv' in request.session or not fs.exists(request.session['csv-name']):
    #     return redirect('mapeamento')

    # nltk.download('punkt')
    # nltk.download('stopwords')
    # nltk.download('rslp')
    # %%
    # ABRINDO PLANILHA DE DADOS .CSV

    # fn_list = request.session['csv']
    # if '%20' in fn_list:
    #     fn_spl = fn_list.split('%20')
    #     fn_list = ' '.join(fn_spl)
    # print(fn_list)
    A = []
    # aux = fn_list.lower()
    campus = 'ODS'
    ano = '2021'
    df = pd.read_csv(io_string, sep=';')
    df['Ano'] = ano
    A.append(df)

    # dataframe unificado com campus e ano

    A = pd.concat(A, ignore_index=True)

    # selecao da coluna de resumos - serie
    A['Resumo Original'] = A['Resumo'].copy()
    A['Resumo_limpo'] = [text_to_id(s, request) for s in A['Resumo']]

    # %%
    # TOKENIZACAO - SEPARACAO DAS PALAVRAS DOS TEXTOS RECEBIDOS
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from string import punctuation
    from nltk.probability import FreqDist

    stemmer = nltk.stem.RSLPStemmer()
    stopwords = set(stopwords.words('portuguese'))
    stopwords = [text_to_id(w, request) for w in stopwords] + list(punctuation)

    ######################################## Processamento das palavras ################################

    # Cria Tokens
    A['tokens'] = [word_tokenize(s) for s in A['Resumo_limpo']]

    # Retira stopwords e transforma palavras para stemmers
    A['tokens_clean'] = [[text_to_id(str(stemmer.stem(p)), request) for p in s if p not in stopwords] for s in A['tokens']]

    # Calcula frequencia de palavras
    A['freqs'] = [dict(FreqDist(s)) for s in A['tokens_clean']]

    plot_all = False

    # %%
    ####################################### Frequencia em cada resumo #################################

    # for i, d in zip(A.index, A['freqs']):
    #    if plot_all:
    #        plt.barh(range(len(d)), list(d.values()), align='center')
    #        plt.yticks(range(len(d)), list(d.keys()))
    #        plt.savefig('freq_grafs/id_'+str(i)+'freq.png')
    #    else:
    #        d_ord = dict(sorted(d.items(), key=lambda item: item[1], reverse=True))
    #        if(len(d_ord)<15):
    #            plt.barh(range(len(d_ord)), list(d_ord.values())[0:len(d_ord)], align='center')
    #            plt.yticks(range(len(d_ord)), list(d_ord.keys())[0:len(d_ord)])
    #        else:
    #            plt.barh(range(15), list(d_ord.values())[0:15], align='center')
    #            plt.yticks(range(15), list(d_ord.keys())[0:15])
    #        plt.savefig('freq_grafs/id_'+str(i)+'_top15_freq.png')

    ####################################### Frequencia geral nos projetos #############################

    from itertools import chain
    from collections import defaultdict

    dict_geral = defaultdict(list)

    for k, v in chain(*[d.items() for d in A['freqs']]):
        dict_geral[k].append(v)

    for k, v in dict_geral.items():
        dict_geral[k] = sum(dict_geral[k])

    print("Limpeza e stemming dos resumos - OK")

    # %%
    # LEITURA DAS PALAVRAS-CHAVE DO BANCO DE DADOS
    db_name = "mapa_ods_2"

    # Conectando com o Banco de Dados
    print("Conectando com o Banco de Dados...")
    con = mdb.connect(host="127.0.0.1", user="root", port=3306, passwd="", db=db_name)
    con.select_db(db_name)

    # Iniciando o cursor e permitindo o Autocommit
    print("Inicializando cursor...")
    cursor = con.cursor()
    cursor.connection.autocommit(True)

    print("Criando listas de palavras-chave para cada ODS")
    columns = ['Área do Projeto', 'Projeto', 'Orientador', 'Email Orientador', 'Campus']
    resultados_PC = pd.DataFrame(A, columns=columns)

    for ods in range(17):
        ods = str(ods + 1)
        query2 = "SELECT pc.palavra_chave_meta, m.id_real_meta FROM palavras_chave pc JOIN class_enrol ce ON pc.id_pc = ce.id_pc JOIN metas m ON m.id_meta=ce.id_meta JOIN ods o ON o.id_ods = m.id_ods WHERE o.id_ods="
        query2 = query2 + ods
        dfPC = pd.read_sql(query2, con)
        # dfPC.to_csv('./palavras_chave_ODS_'+ods+'.csv', index=False)
        num_PC_ods = []

        # Limpando palavras-chave
        dfPC['PC_limpo'] = [text_to_id(s, request) for s in dfPC['palavra_chave_meta']]

        dfPC['tokens_PC'] = [word_tokenize(s) for s in dfPC['PC_limpo']]

        dfPC['tokens_PC'] = [[text_to_id(str(stemmer.stem(p)), request) for p in s if p not in stopwords] for s in
                             dfPC['tokens_PC']]

        palavras_metas_projetos = []

        for i, resumo in zip(A.index, A['tokens_clean']):
            resumo = convert_list_to_string(resumo, request)
            num_palavras = 0
            palavras_metas = ''
            for j, palavra_token, palavra_limpo in zip(dfPC.index, dfPC['tokens_PC'], dfPC['PC_limpo']):
                palavra_token = convert_list_to_string(palavra_token, request)
                if palavra_token in resumo:
                    num_palavras += 1
                    palavras_metas += palavra_limpo + '(' + dfPC['id_real_meta'][
                        j] + ') | '  # .append([palavra_limpo,dfPC['id_real_meta'][j]])
            palavras_metas_projetos.append(palavras_metas)
            num_PC_ods.append(num_palavras)

        resultados_PC['ODS' + str(ods) + '_PC'] = palavras_metas_projetos
        resultados_PC['ODS' + str(ods)] = num_PC_ods

    # Escrita do arquivo relatorio
    areas = resultados_PC['Área do Projeto'].unique()
    # print('------',areas,'-------')
    # campi = ['JF','GV']
    campi = ['ODS']
    ods_name = ['ODS1', 'ODS2', 'ODS3', 'ODS4', 'ODS5', 'ODS6', 'ODS7', 'ODS8', 'ODS9',
                'ODS10', 'ODS11', 'ODS12', 'ODS13', 'ODS14', 'ODS15', 'ODS16', 'ODS17', ]
    resultados_PC = resultados_PC[['Área do Projeto',
                                   'Projeto',
                                   'Orientador',
                                   'Email Orientador',
                                   'Campus',
                                   'ODS1',
                                   'ODS1_PC',
                                   'ODS2',
                                   'ODS2_PC',
                                   'ODS3',
                                   'ODS3_PC',
                                   'ODS4',
                                   'ODS4_PC',
                                   'ODS5',
                                   'ODS5_PC',
                                   'ODS6',
                                   'ODS6_PC',
                                   'ODS7',
                                   'ODS7_PC',
                                   'ODS8',
                                   'ODS8_PC',
                                   'ODS9',
                                   'ODS9_PC',
                                   'ODS10',
                                   'ODS10_PC',
                                   'ODS11',
                                   'ODS11_PC',
                                   'ODS12',
                                   'ODS12_PC',
                                   'ODS13',
                                   'ODS13_PC',
                                   'ODS14',
                                   'ODS14_PC',
                                   'ODS15',
                                   'ODS15_PC',
                                   'ODS16',
                                   'ODS16_PC',
                                   'ODS17',
                                   'ODS17_PC'
                                   ]]
    resultados_PC['Total'] = resultados_PC['ODS1'] + resultados_PC['ODS2'] + resultados_PC['ODS3'] + resultados_PC[
        'ODS4'] + resultados_PC['ODS5'] + resultados_PC['ODS6'] + resultados_PC['ODS7'] + resultados_PC['ODS8'] + \
                             resultados_PC['ODS9'] + resultados_PC['ODS10'] + resultados_PC['ODS11'] + resultados_PC[
                                 'ODS12'] + resultados_PC['ODS13'] + resultados_PC['ODS14'] + resultados_PC['ODS15'] + \
                             resultados_PC['ODS16'] + resultados_PC['ODS17']

    # resultados_PC.to_csv('./relatorio_palavras_metas_bd2' + '.csv', index=False)
    buf_csv = io.BytesIO()
    resultados_PC.to_csv(buf_csv, index=False)
    buf_csv.seek(0)
    csv = base64.b64encode(buf_csv.getvalue())
    csv = csv.decode('utf8')

    df_result_areas = pd.DataFrame()
    for campus in campi:
        # df = resultados_PC.loc[(resultados_PC['Campus']==campus)]
        df = resultados_PC
        for area in areas:
            df2 = df.loc[(df['Área do Projeto'] == area)]
            soma_palavras = df2.sum(axis=0, skipna=False)
            soma_palavras.pop('Área do Projeto')
            soma_palavras.pop('Projeto')
            soma_palavras.pop('Campus')
            soma_palavras.pop('Orientador')
            soma_palavras.pop('Email Orientador')
            for k in ods_name:
                soma_palavras.pop(k + '_PC')

            df_result_areas[area] = soma_palavras
        df_result_areas = df_result_areas.apply(pd.to_numeric)
        print(80 * '=', '\n', 'Palavras-chave por área de conhecimento - ', campus.upper(), '\n', 80 * '=')
        sns.heatmap(df_result_areas, annot=True, fmt='.3g')
        yticks_labels = ods_name
        #    #yticks_labels.append('TOTAL')
        plt.yticks(np.arange(df_result_areas.shape[0]) + .5, labels=yticks_labels, rotation='horizontal',
                   fontweight=550)
        #
        # Modificacao das labels das areas
        #    xticks_labels = []
        #    for pos in areas:
        #        xticks_labels.append(replace_names(pos))
        xticks_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
                         '10', '11', '12', '13', '14', '15', '16', '17', ]
        xticks_labels.append('TOTAL')

        plt.xticks(np.arange(df_result_areas.shape[1]) + .5, labels=xticks_labels, rotation='horizontal',
                   fontweight=550)
        plt.xlabel('')
        plt.ylabel('')
        plt.title('BD2')
        # plt.savefig('./media/heatmap_' + "key!" + request.session.session_key + '.png')
        buf_img = io.BytesIO()
        plt.savefig(buf_img, format='png')
        buf_img.seek(0)
        image = base64.b64encode(buf_img.getvalue())
        image = image.decode('utf8')
        plt.clf()
        buf_img.flush()
        buf_img.close()
        buf_csv.flush()
        buf_csv.close()

    # session = request.session
    # sessions = Session.objects.all()
    # for session in sessions:
    #     print(getattr(session, 'expire_date'))
    # print(Session.objects.all().filter())

    # return render(request, 'resultado.html', {'csv': f"{settings.MEDIA_URL}relatorio_palavras_metas_bd2_key!{session_key}.csv", 'heatmap': f"{settings.MEDIA_URL}heatmap_key!{session_key}.png"})
    
    # return render(request, 'resultado.html', {'csv': csv, 'heatmap': image})
    return csv, image


def map_pdf(request, pdf_file):
    # if request.method != "GET" or not 'pdf' in request.session or not fs.exists(request.session['pdf-name']):
    #     return redirect('mapeamento')

    # nltk.download('punkt')
    # nltk.download('stopwords')
    # nltk.download('rslp')

    # %%
    # ABRINDO ARQUIVO .PDF

    # fn_list = glob.glob('./pdf--ods/ods*.pdf')
    fn = pdf_file.name
    pdf_byt = io.BytesIO(pdf_file.read())
    if '%20' in fn:
        fn_spl = fn.split('%20')
        fn = ' '.join(fn_spl)
    aux = fn.lower()
    num_ods = aux.split('.pdf')[0].split('_')[1]
    campus = 'ODS'
    ano = '2021'
    text = ""
    A = []
    vet_ods = []
    with pdfplumber.open(pdf_byt) as pdf:
        for i, p in enumerate(pdf.pages):
            s = p.extract_text()
            #print(s)
            text = text + ' ' + str(s)

    text = text.replace('\n', ' ')
    text = text.replace('.', ' ')
    text = text.replace('•', ' ')

    num_ods = float(num_ods)
    vet_ods.append(num_ods)
    A.append([text,ano])

    # for fn in fn_list:
    #     aux = fn.lower()
    #
    #     # _, campus, ano = aux.split('.csv')[0].split('__')
    #     _, num_ods = aux.split('.pdf')[0].split('_')
    #     campus = 'ODS'
    #     ano = '2021'
    #     text = ""
    #     # df=pd.DataFrame()
    #     with pdfplumber.open(fn) as pdf:
    #         for i, p in enumerate(pdf.pages):
    #             s = p.extract_text()
    #             # print(s)
    #             text = text + ' ' + str(s)
    #
    #     text = text.replace('\n', ' ')
    #     text = text.replace('.', ' ')
    #     text = text.replace('•', ' ')
    #
    #     num_ods = float(num_ods)
    #
    #     vet_ods.append(num_ods)
    #
    #     # df['Resumo'] = text
    #     # df['Campus'] = campus
    #     # df['Ano']= ano
    #     # df['ODS'] = num_ods
    #     # df['Meta'] = meta
    #     # df['Palavra-chave'] = palavra_chave_meta
    #     A.append([text, ano])
    #     # print(text)

    # dataframe unificado
    A = pd.DataFrame(A, columns={'Resumo', 'Ano'})
    # A = pd.concat(A,ignore_index=True)
    # A=A.replace(np.nan, 'NC')
    # A.rename(columns={'E-mail orientador': 'Email Orientador'})
    # selecao da coluna de resumos - serie
    A['Resumo Original'] = A['Resumo'].copy()
    A['Resumo_limpo'] = [text_to_id(s, request) for s in A['Resumo']]

    A['Área do Projeto'] = vet_ods
    A = A.sort_values(['Área do Projeto'])

    # %%
    # TOKENIZACAO - SEPARACAO DAS PALAVRAS DOS TEXTOS RECEBIDOS
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from string import punctuation
    from nltk.probability import FreqDist

    stemmer = nltk.stem.RSLPStemmer()
    stopwords = set(stopwords.words('portuguese'))
    stopwords = [text_to_id(w, request) for w in stopwords] + list(punctuation)

    ######################################## Processamento das palavras ################################

    # Cria Tokens
    A['tokens'] = [word_tokenize(s) for s in A['Resumo_limpo']]

    # Retira stopwords e transforma palavras para stemmers
    A['tokens_clean'] = [[text_to_id(str(stemmer.stem(p)), request) for p in s if p not in stopwords] for s in A['tokens']]
    
    # Calcula frequencia de palavras
    A['freqs'] = [dict(FreqDist(s)) for s in A['tokens_clean']]

    plot_all = False

    # %%
    ####################################### Frequencia em cada resumo #################################

    # for i, d in zip(A.index, A['freqs']):
    #    if plot_all:
    #        plt.barh(range(len(d)), list(d.values()), align='center')
    #        plt.yticks(range(len(d)), list(d.keys()))
    #        plt.savefig('freq_grafs/id_'+str(i)+'freq.png')
    #    else:
    #        d_ord = dict(sorted(d.items(), key=lambda item: item[1], reverse=True))
    #        if(len(d_ord)<15):
    #            plt.barh(range(len(d_ord)), list(d_ord.values())[0:len(d_ord)], align='center')
    #            plt.yticks(range(len(d_ord)), list(d_ord.keys())[0:len(d_ord)])
    #        else:
    #            plt.barh(range(15), list(d_ord.values())[0:15], align='center')
    #            plt.yticks(range(15), list(d_ord.keys())[0:15])
    #        plt.savefig('freq_grafs/id_'+str(i)+'_top15_freq.png')

    ####################################### Frequencia geral nos projetos #############################

    from itertools import chain
    from collections import defaultdict

    dict_geral = defaultdict(list)

    for k, v in chain(*[d.items() for d in A['freqs']]):
        dict_geral[k].append(v)

    for k, v in dict_geral.items():
        dict_geral[k] = sum(dict_geral[k])

    # d_ord = dict(sorted(d.items(), key=lambda item: item[1], reverse=True))
    # n_words = 20
    # plt.barh(range(n_words), list(d.values())[0:n_words], align='center')
    # plt.yticks(range(n_words), list(d.keys())[0:n_words])
    # plt.savefig('freq_grafs/__overall_top'+str(n_words)+'_freq.png')


    print("Limpeza e stemming dos resumos - OK")

    # %%
    # LEITURA DAS PALAVRAS-CHAVE DO BANCO DE DADOS
    db_name = "mapa_ods_2"
    # Conectando com o Banco de Dados
    print("Conectando com o Banco de Dados...")
    con = mdb.connect(host="127.0.0.1", user="root", port=3306, passwd="", db=db_name)
    con.select_db(db_name)

    # Iniciando o cursor e permitindo o Autocommit
    print("Inicializando cursor...")
    cursor = con.cursor()
    cursor.connection.autocommit(True)

    print("Criando listas de palavras-chave para cada ODS")
    columns = ['Área do Projeto', 'Projeto', 'Orientador', 'Email Orientador', 'Campus']
    resultados_PC = pd.DataFrame(A, columns=columns)

    for ods in range(17):
        ods = str(ods + 1)
        query2 = "SELECT pc.palavra_chave_meta, m.id_real_meta FROM palavras_chave pc JOIN class_enrol ce ON pc.id_pc = ce.id_pc JOIN metas m ON m.id_meta=ce.id_meta JOIN ods o ON o.id_ods = m.id_ods WHERE o.id_ods="
        query2 = query2 + ods
        dfPC = pd.read_sql(query2, con)
        # dfPC.to_csv('./palavras_chave_ODS_'+ods+'.csv', index=False)
        num_PC_ods = []
        # Limpando palavras-chave
        dfPC['PC_limpo'] = [text_to_id(s, request) for s in dfPC['palavra_chave_meta']]

        dfPC['tokens_PC'] = [word_tokenize(s) for s in dfPC['PC_limpo']]

        dfPC['tokens_PC'] = [[text_to_id(str(stemmer.stem(p)), request) for p in s if p not in stopwords] for s in dfPC['tokens_PC']]

        palavras_metas_projetos = []

        for i, resumo in zip(A.index, A['tokens_clean']):
            resumo = convert_list_to_string(resumo, request)
            num_palavras = 0
            palavras_metas = ''
            for j, palavra_token, palavra_limpo in zip(dfPC.index, dfPC['tokens_PC'], dfPC['PC_limpo']):
                palavra_token = convert_list_to_string(palavra_token, request)
                if palavra_token in resumo:
                    num_palavras += 1
                    palavras_metas += palavra_limpo + '(' + dfPC['id_real_meta'][
                        j] + ') | '  # .append([palavra_limpo,dfPC['id_real_meta'][j]])
            palavras_metas_projetos.append(palavras_metas)
            num_PC_ods.append(num_palavras)

        resultados_PC['ODS' + str(ods) + '_PC'] = palavras_metas_projetos
        resultados_PC['ODS' + str(ods)] = num_PC_ods

    # Escrita do arquivo relatorio
    areas = resultados_PC['Área do Projeto'].unique()
    # print('------',areas,'-------')
    # campi = ['JF','GV']
    campi = ['ODS']
    ods_name = ['ODS1', 'ODS2', 'ODS3', 'ODS4', 'ODS5', 'ODS6', 'ODS7', 'ODS8', 'ODS9',
                'ODS10', 'ODS11', 'ODS12', 'ODS13', 'ODS14', 'ODS15', 'ODS16', 'ODS17']
    resultados_PC = resultados_PC[['Área do Projeto',
                                   'Projeto',
                                   'Orientador',
                                   'Email Orientador',
                                   'Campus',
                                   'ODS1',
                                   'ODS1_PC',
                                   'ODS2',
                                   'ODS2_PC',
                                   'ODS3',
                                   'ODS3_PC',
                                   'ODS4',
                                   'ODS4_PC',
                                   'ODS5',
                                   'ODS5_PC',
                                   'ODS6',
                                   'ODS6_PC',
                                   'ODS7',
                                   'ODS7_PC',
                                   'ODS8',
                                   'ODS8_PC',
                                   'ODS9',
                                   'ODS9_PC',
                                   'ODS10',
                                   'ODS10_PC',
                                   'ODS11',
                                   'ODS11_PC',
                                   'ODS12',
                                   'ODS12_PC',
                                   'ODS13',
                                   'ODS13_PC',
                                   'ODS14',
                                   'ODS14_PC',
                                   'ODS15',
                                   'ODS15_PC',
                                   'ODS16',
                                   'ODS16_PC',
                                   'ODS17',
                                   'ODS17_PC'
                                   ]]
    resultados_PC['Total'] = resultados_PC['ODS1'] + resultados_PC['ODS2'] + resultados_PC['ODS3'] + resultados_PC['ODS4'] + \
                             resultados_PC['ODS5'] + resultados_PC['ODS6'] + resultados_PC['ODS7'] + resultados_PC['ODS8'] + \
                             resultados_PC['ODS9'] + resultados_PC['ODS10'] + resultados_PC['ODS11'] + resultados_PC[
                                 'ODS12'] + resultados_PC['ODS13'] + resultados_PC['ODS14'] + resultados_PC['ODS15'] + \
                             resultados_PC['ODS16'] + resultados_PC['ODS17']
    # print(resultados_PC)
    # Arquivo relatorio estruturado

    # for area in areas:
    #    df = resultados_PC.loc[(resultados_PC['Área do Projeto']==area)]
    #    for index_projeto, nome_projeto, orientador, campus in zip(df.index, df['Projeto'], df['Orientador'], df['Campus']):
    #        string_relatorio += nome_projeto+';'+area+';'+orientador+';'+campus+';'
    #        for ods in ods_name:
    #            if df[ods][index_projeto]!=0:
    #                string_relatorio+= ods+'('+str(df[ods][index_projeto])+') -'
    #                for pc_meta in df[ods+'_PC'][index_projeto]:
    #                    string_relatorio+= pc_meta[0]+'('+pc_meta[1]+')'+','
    #                string_relatorio+= ';'
    #
    #        string_relatorio+= '\n'

    # f = open("./relatorio_palavras_metas.csv", "w")
    # f.write(string_relatorio)
    # f.close()
    # resultados_PC.to_csv('./media/relatorio_palavras_metas_bd1_key!' + request.session.session_key + '.csv', index=False)
    # resultados_PC.to_csv(f'.{settings.MEDIA_URL}relatorio_palavras_metas_bd1_key!{request.session.session_key}.csv', index=False)
    # print(f'.{settings.MEDIA_URL}relatorio_palavras_metas_bd1_key!{request.session.session_key}.csv')
    buf_csv = io.BytesIO()
    resultados_PC.to_csv(buf_csv, index=False)
    buf_csv.seek(0)
    csv = base64.b64encode(buf_csv.getvalue())
    csv = csv.decode('utf8')

    # %%
    # Geracao de arquivo relatorio nao estruturado
    # string_relatorio = ''
    # for area in areas:
    #    df = resultados_PC.loc[(resultados_PC['Área do Projeto']==area)]
    #    for index_projeto, nome_projeto, orientador, campus in zip(df.index, df['Projeto'], df['Orientador'], df['Campus']):
    #        string_relatorio += nome_projeto+';'+area+';'+orientador+';'+campus+';'
    #        for ods in ods_name:
    #            if df[ods][index_projeto]!=0:
    #                string_relatorio+= ods+'('+str(df[ods][index_projeto])+') -'
    #                for pc_meta in df[ods+'_PC'][index_projeto]:
    #                    string_relatorio+= pc_meta[0]+'('+pc_meta[1]+')'+','
    #                string_relatorio+= ';'
    #        string_relatorio+= '\n'
    #
    # f = open("./relatorio_palavras_metas.csv", "w")
    # f.write(string_relatorio)
    # f.close()
    # %%
    # COMENTADO

    df_result_areas = pd.DataFrame()
    for campus in campi:
        # df = resultados_PC.loc[(resultados_PC['Campus']==campus)]
        df = resultados_PC
        for area in areas:
            df2 = df.loc[(df['Área do Projeto'] == area)]
            soma_palavras = df2.sum(axis=0, skipna=False)
            soma_palavras.pop('Área do Projeto')
            soma_palavras.pop('Projeto')
            soma_palavras.pop('Campus')
            soma_palavras.pop('Orientador')
            soma_palavras.pop('Email Orientador')
            for k in ods_name:
                soma_palavras.pop(k + '_PC')

            df_result_areas[area] = soma_palavras
        df_result_areas = df_result_areas.apply(pd.to_numeric)
        print(80 * '=', '\n', 'Palavras-chave por área de conhecimento - ', campus.upper(), '\n', 80 * '=')
        try:
            sns.heatmap(df_result_areas, annot=True, fmt='.3g')
        except Exception as e:
            print(e)
            return redirect('resultado-pdf')
        yticks_labels = ods_name
        #    #yticks_labels.append('TOTAL')
        # plt.yticks(np.arange(df_result_areas.shape[0]+0.5), labels=yticks_labels, rotation='horizontal',fontweight=550)
        #
        # Modificacao das labels das areas
        #    xticks_labels = []
        #    for pos in areas:
        #        xticks_labels.append(replace_names(pos))
        xticks_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
                         '10', '11', '12', '13', '14', '15', '16', '17']
        # xticks_labels.append('TOTAL')

        # plt.xticks(np.arange(df_result_areas.shape[1]), labels=xticks_labels, rotation='horizontal',fontweight=550)
        plt.xlabel('')
        plt.ylabel('')
        plt.title('BD1')
        # plt.show()
        buf_img = io.BytesIO()
        # plt.savefig('./media/heatmap_' + "key!" + request.session.session_key + '.png')
        plt.savefig(buf_img, format='png')
        buf_img.seek(0)
        image = base64.b64encode(buf_img.getvalue())
        image = image.decode('utf8')
        plt.clf()
        buf_img.flush()
        buf_img.close()
        buf_csv.flush()
        buf_csv.close()

    # print(df_result_areas)
    # return render(request, 'resultado.html', {'csv': f"{settings.MEDIA_URL}relatorio_palavras_metas_bd1_key!{session_key}.csv", 'heatmap': f"{settings.MEDIA_URL}heatmap_key!{session_key}.png", 'download': False})
    return csv, image

def contact(request):
    if request.method == 'POST':
        sender = EmailSender()
        data = {
            'name': request.POST['name'],
            'email': request.POST['email'],
            'content': request.POST['message'],
        }
        subject = f'Nova mensagem de {data["email"]} no site ODS Mapeados'
        # message = data['content']
        to_list = ['capriles@ice.ufjf.br']
        template_path = 'email_temp.html'


        sender.send(
            to_list=to_list,
            from_email=data['email'],
            template_path=template_path,
            subject=subject,
            content=data,
            image_path='roda_ODS_colorido_80.png',
            )

        messages.success(request, 'Sua mensagem foi enviada com sucesso!')
        return redirect('index')

    else:
        return redirect('index')

        
def strip_accents(text, request):
    """
    Strip accents from input String.
    :param text: The input string.
    :type text: String.
    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError):  # unicode is a default on python 3
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def text_to_id(text, request):
    """
    Convert input text to id.
    :param text: The input string.
    :type text: String.
    :returns: The processed String.
    :rtype: String.
    """
    # Removendo todos os numerais do texto
    # print(type(text))
    # if(math.isnan(text)==True):
    # text='NC'
    # text = ''.join([i for i in text if not i.isdigit()])
    # print(text)
    text = strip_accents(text.upper(), request)
    text = re.sub('[.]+', '', text)
    # text = re.sub('[ ]+', '_', text)
    text = re.sub('[^ 0-9a-zA-Z_-]', '', text)
    return text

'''
def fazstemmer(texto):
    stemmer = nltk.stem.RSLPStemmer()
    resumossemstemming = []
    for palavras in texto:
        comstemming = [str(stemmer.stem(p))
                       for p in palavras.split() if p not in stopwords]
        resumossemstemming.append(comstemming)
    return resumossemstemming
'''

def convert_list_to_string(org_list, request, seperator=' '):
    """ Convert list to string, by joining all item in list with given separator.
        Returns the concatenated string """
    return seperator.join(org_list)

def replace_names(s, request):
    sv = [
        ('CIENCIAS BIOLOGICAS', 'C. BIO.'),
        ('CIENCIAS DA SAUDE', 'C.SAU.'),
        ('CIENCIAS EXATAS E DA TERRA', 'C.EXA.'),
        ('CIENCIAS HUMANAS', 'C.HUM.'),
        ('CIENCIAS SOCIAIS APLICADAS', 'C.SOC.'),
        ('ENGENHARIAS E CIENCIA DA COMPUTACAO', 'ENG. E \n C.COMP.'),
        ('LINGUISTICA, LETRAS E ARTES', 'LING., LET.\n E ART.'),
        ('Saúde', 'SAUDE'),
        ('Meio Ambiente', 'MEIO \n AMB.'),
        ('Direitos Humanos e Justiça', 'DIR. HUM E \n JUS'),
        ('Educação', 'EDUC'),
        ('Cultura', 'CULT'),
        ('NC', 'NC'),
        ('Tecnologia e Produção', 'TEC. E \n PROD.'),
        ('Comunicação', 'COMUN'),
        ('Trabalho', 'TRAB'),
    ]
    for s1, s2 in sv:
        r = s.replace(s1, s2)
        if (r != s):
            return r
    return s

