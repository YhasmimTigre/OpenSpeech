import os
import re
import pandas as pd
from stop_words import get_stop_words


def get_speech():
    # Recebendo os discursos
    discursos = []
    for j in os.listdir('discursos'):
        file = open(f'discursos/{j}', 'r', encoding="utf-8")
        text = file.read()
        discursos.append(text)
        file.close
    discursos = pd.Series(discursos)
    return discursos

def verify_speech():
    revisado = []
    for j in range(len(get_speech())):
        if(re.search(r'Sem revisão', get_speech()[j])):
            revisado.append(False)
        else:
            revisado.append(True)
    revisao = pd.Series(revisado)
    df_discursos = {"discursos" : get_speech(),
                    "revisao" : revisao}
    df_discursos = pd.concat(df_discursos, axis=1)
    return df_discursos

def clean_speech():

    df = verify_speech()
    conectivos_lista = []
    conectivos_lista = get_stop_words('pt')
    conectivos_lista.append('é')
    conectivos_lista = [conectivo.upper() for conectivo in conectivos_lista]


    #Retirando a introdução
    discursos = df['discursos'].str.split('.\) -')
    df['discursos'] = [i[1:] for i in discursos]

    discursos_lista = []
    discurso_limpo = []

    for i in df['discursos']:
        discursos_lista.append(" ".join(i))

    termos_discursos = []
    for i in range(len(discursos_lista)):

        #Retirando os sons ambientes
        sons_ambiente = ['<tr><td align="center">(<i>Soa a campainha.</i>)</td></tr></table>', '<i>(Palmas.)</i>']
        for j in sons_ambiente:
            discursos_lista[i] = discursos_lista[i].replace(j, '')
        
        #Retirando as tags
        tags = ['<i>', '</i>', f'\n']
        for j in tags:
            discursos_lista[i] = discursos_lista[i].replace(j, '')

        #Retirando pontuacoes
        pontuacoes = ['.', ':', '...', '(', ')', '[', ']', '{', '}', '!', '?', ',', ';', '-', '_', "'", "\"", "nº", '<', '>', '\\', '|', '/', ', , ', ']\n']
        for j in pontuacoes:
            discursos_lista[i] = discursos_lista[i].replace(j, '')

        #retirando numeros
        for j in range(10):
            discursos_lista[i] = discursos_lista[i].replace(str(j), '')

        discurso_limpo.append(discursos_lista[i])
        discursos_lista[i] = discursos_lista[i].split(' ')
        
        #separando os termos e retirando conectivos
        termos = []
        for j in range(len(discursos_lista[i])):
            if (discursos_lista[i][j] != '') and (type(discursos_lista[i][j]) == str):
                termos.append(discursos_lista[i][j].upper())
        termos = [termo for termo in termos if not termo in conectivos_lista]
        termos_discursos.append(termos)

    df['discursos'] = discurso_limpo
    df['termos'] = [pd.Series(i) for i in termos_discursos]

    return df

def count_words():
    df = clean_speech()
    dict_termos = []
    for i in range(len(df['termos'])):
        new_dict = {df['termos'][i].value_counts().index[j]: df['termos'][i].value_counts()[j] for j in range(len(df['termos'][i].value_counts()))}
        dict_termos.append(new_dict)
    df['qtd_termos'] = dict_termos
    df['termos'] = [df['termos'][i].tolist() for i in range(len(df['termos']))]

    return df


count_words().to_csv('df_discursos.csv', encoding='utf-8', index=False)