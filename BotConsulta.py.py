# -*- coding: utf-8 -*-
import shutil
import tempfile
import urllib.request
import time
import os
import re
import webbrowser
from os.path import isfile, join
import datetime
"Insira aqui o nome do arquivo que contem a lista de links do processo - obs, os links só, não o numero"
nomeLista="Database.txt"




NomeDiretorioAntigo="ProcessosDeOntem"
NomeDiretorioNovo="ProcessosDeHoje"
#NomeDiretorioNovoQuebrado="LinksQuebradosHoje"
#NomeDiretorioAntigoQuebrado="LinksQuebradosOntem"


def SalvarUrl(url,nomeArquivo):
    #print("salvando %s"%nomeArquivo)
    "Salva uma Url em um nome de arquivo"
    with urllib.request.urlopen(url) as response:
       html = response.read()
    
    
    if "captcha" in str(html):
        print("captcha Foi encontrado, tente em outro horario",str(url))
        return 1
    elif 'Processando a consulta, aguarde...' in str(html):
        print("Erro ao carregar esta pagina, verificação manual programada",str(url))
        return 2
        #pass
    else:
        print ("sucesso ao salvar pagina %s"%nomeArquivo)
    
    salvo=open(nomeArquivo,"wb")
    salvo.write(html)
    salvo.close()
    ultimaModificacao=MaiorData(nomeArquivo)
    now = datetime.datetime.now()
    
    if (str(now.day)+'/'+str(now.month)+'/'+str(now.year))==(ultimaModificacao):
        print("Modificacao mais recente em: %s : \nHOJEEEEEE!!!!!!\n"%ultimaModificacao)
    else:
        print("Modificacao mais recente em: %s"%ultimaModificacao)
    time.sleep(1)
    return 0


    
#ChecarDiff("proc3.html","proc3.html")
def MaiorData(nomeArquivo):
    datas=[]
    conteudos=ObterData(nomeArquivo)
    #print (conteudos[0])
    for datestring in conteudos[0]:
        dt = datetime.datetime.strptime(datestring, '%d/%m/%Y')
        datas.append(dt)
    maior=max(datas)
    return str(maior.day)+'/'+str(maior.month)+'/'+str(maior.year)
    
def GerarLista(nomeLista):
    saida=[]
    sublista=[]
    listaUrls=[]
    listaNomes=[]
    with open(nomeLista,"r") as arquivo:
        listaLinks=arquivo.readlines()
    for i in range(len(listaLinks)):
        sublista=listaLinks[i].split(';')
        #listaLinks[i][1]=listaLinks[i][:-1]
        if sublista[0]=='':
            break
        if sublista[1]=='':
            print ("erro em ",i)
     #   print (sublista)
        listaUrls+=[sublista]
        
    #print (listaUrls)
    return listaUrls

def CriarDataBase(NomeDiretorio):
    erro=0
    userResponse=''
    contadorDeBroken=0
    contadorCaptcha=0
    brokenLinks=[]
    if not(os.path.exists(NomeDiretorio)):
        os.makedirs(NomeDiretorio)
    links=GerarLista(nomeLista)
    for url in links:
        erro=SalvarUrl(url[0],NomeDiretorio+"\\"+url[1][:-1]+".html")
        if erro==2:
            contadorDeBroken+=1
            if url[0] in brokenLinks:
                print("URL REPETIDA",url[0])
            else:
                brokenLinks.append(url[0])
        if erro==1:
            contadorCaptcha+=1
    print ("Voce possui %i links quebrados e %i captchas, deseja abrir os links quebrados no browser agora para salva-los?"%(contadorDeBroken,contadorCaptcha))

    while (userResponse!='s' and userResponse!= 'n'):
        userResponse=input("deseja prosseguir? s/n")
        
        #print(userResponse)
    if userResponse=='s':
        print("faca o seguinte agr, para cada pagina aberta em seu navegador, vá ate '%s\\Quebrados' e salve o arquivo la com o nome padrao msm.\nPara faciliar aperte ctrl-s para salvar e ctrl w para fechar a guia"%NomeDiretorio)
        for url in brokenLinks:
            webbrowser.open(url, new=0, autoraise=True)
        RecursaoMudarNome(brokenLinks,NomeDiretorio)
    return brokenLinks

def EstaContido(lista1,listaPai):
    for i in lista1:
        if i not in listaPai:
            return 1
    return 0
def RecursaoMudarNome(brokenLinks,NomeDiretorio):
    

    if not(os.path.exists(NomeDiretorio+"Quebrado")):
        os.makedirs(NomeDiretorio+"Quebrado")
    
    while EstaContido([ObeterUrlLink(f)+".html" for f in brokenLinks],os.listdir(NomeDiretorio+"Quebrado")):
        if "Resultado da consulta processual.html" in os.listdir(NomeDiretorio+"Quebrado"):
            #print([ObeterUrlLink(f)+".html" for f in brokenLinks],"\r\ne\r\n ",os.listdir(NomeDiretorio+"Quebrado"))
            #print("achei um resultado,renomeando")
            RenomearArquivo(NomeDiretorio+"Quebrado"+"\\Resultado da consulta processual.html")
        else:
            time.sleep(0.01)
    return 0

def RenomearArquivo(nomeArquivo):
    print("renomeado: %s"%nomeArquivo)
    data=ObterUrlNome(nomeArquivo)
    
    lista=nomeArquivo.split('\\')
    #print("nome separado:",lista)
    #data=ObterNumeroProcesso(nomeArquivo)
    #print (lista)
    #print ("argumento do rename",nomeArquivo,lista[0]+'\\'+data+'.html')
    try:
        os.rename(nomeArquivo,lista[0]+'\\'+data+'.html')
        return 0
    except:
        print("mesmo arquivo ja salvo, removendo arquivo: "+nomeArquivo)
        os.remove(nomeArquivo)

def ObeterUrlLink(link):
    numeroUrl = re.compile('[N][=][0-9]{12}')
    numeroUrl2 = re.compile('[N][=][0-9]{4}[\.][0-9]{3}[\.][0-9]{5}')
    if re.search(numeroUrl,link)!=None:
            encontro=re.search(numeroUrl,link)
            return encontro.group()[2:]
    elif re.search(numeroUrl2,link)!=None:
            encontro=re.search(numeroUrl2,link)
            return encontro.group()[2:]
    else:
        print("erro ao obter link")
        return -1
            

def ObterUrlNome(nomeArquivo):
    data=[]
    saida=''
    arquivo=open(nomeArquivo,"r")
    linhas=arquivo.readlines()
    numeroUrl = re.compile('[N][=][0-9]{12}')
    numeroUrl2 = re.compile('[N][=][0-9]{4}[\.][0-9]{3}[\.][0-9]{5}')
    for i in range(len(linhas)):
        #print (i,linhas[i])
        if re.search(numeroUrl,linhas[i])!=None:
            encontro=re.search(numeroUrl,linhas[i])
            #print ("encontrado",numeroUrl)
            saida=encontro.group()[2:]
            break
        elif re.search(numeroUrl2,linhas[i])!=None:
            encontro=re.search(numeroUrl2,linhas[i])
            #print ("encontrado",numeroUrl2)
            saida=encontro.group()[2:]
            break

    arquivo.close()
    print("saida:",saida)
    return saida

def RemoverDuplicatas(lista):
    indice=0
    while  indice<len(lista):
        if lista.count(lista[indice])>1:
            lista.remove(lista[indice])
        else:
            indice+=1
    return lista

def ChecarDiferencas(nomeArquivo1,nomeArquivo2):
    arquivo1=open(nomeArquivo1,"r")
    arquivo2=open(nomeArquivo2,"r")
    linhas1=arquivo1.readlines()
    linhas2=arquivo2.readlines()
    #print ("linhas1:",linhas1)
    data1=ObterData(nomeArquivo1)
    data2=ObterData(nomeArquivo2)
    if data1[0]==[] or data2[0]==[]:
        pass
        #print("ERRO DATA VAZIA")
    if data1[0]!=data2[0]:
        #print ("datas diferentes: ",data1,data2)
        return 1,data1[1],data2[1],data1[0],data2[0]
    else:
        return 0,data1[1],data2[1],data1[0],data2[0]

def CompararDataBase(raiz1,raiz2):
    diferencas=0
    userResponse=''
    arquivosParaComparar=[]
    print("comparando diretorios %s e %s"%(raiz1,raiz2))
    listaArquivos=os.listdir(raiz2)
    listaArquivos+=os.listdir(raiz1)
    listaArquivos=RemoverDuplicatas(listaArquivos)
    #print(listaArquivos,len(listaArquivos))
    for nome in listaArquivos:
        print (nome)
        if not os.path.isfile(raiz2+nome) and not os.path.isfile(raiz1+nome):
            print("nao e arquivo, continuando")
            continue
        correto=ChecarDiferencas(raiz1+nome,raiz2+nome)
        if correto[0]==1:
            print("diferenca em: ",nome)
            print("datas do antigo",correto[3],"datas do novo",correto[4])
            arquivosParaComparar.append([raiz1+nome,raiz2+nome])
            #print(correto[1]," vs ",correto[2])
            diferencas+=1
        #    z=input("prosseguir ")
    print("total de diferencas",diferencas)

    while (userResponse!='s' and userResponse!= 'n'):
        userResponse=input("deseja abrir arquivos agr? s/n")
    if userResponse=='s':
        for url in arquivosParaComparar:
            webbrowser.open(url[0], new=0, autoraise=True)
            webbrowser.open(url[1], new=1, autoraise=True)
    return 0
        
        
        
        
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


def ObterData(nomeArquivo):
    data=[]
    data2=[]
    arquivo=open(nomeArquivo,"r")
    linhas=arquivo.readlines()
    formatData = re.compile('[0-9]{2}[/][0-9]{2}[/][0-9]{4}')
    for i in range(len(linhas)):
        if re.findall(formatData,linhas[i])!=[]:
            encontro=re.findall(formatData,linhas[i])
            data+=encontro#.group()
            data2.append(striphtml(linhas[i-1]))
        
    arquivo.close()
    #print (data)
    #print (data2)
    del data[0]
    del data2[0]
    #print ("sucesso")
    return data,data2

def ObterNumeroProcesso(nomeArquivo):
    data=[]
    arquivo=open(nomeArquivo,"r")
    linhas=arquivo.readlines()
    numeroProcesso = re.compile('[:][ ][0-9]{7}[-][0-9]{2}[\.][0-9]{4}[\.][0-9]{1}[\.][0-9]{2}[\.][0-9]{4}') #regex to find numvber do processo
    for i in range(len(linhas)):
        try:
            numero=re.search(numeroProcesso,linhas[i])
            data.append(numero.group()[1:])
        except:
            pass
    arquivo.close()
    print (data)
    return data
def AtualizarDiretorios():
    print("removendo",NomeDiretorioAntigo)
    try:
        shutil.rmtree(NomeDiretorioAntigo)
    except:
        print("Diretorio ja nao existe")
        
    print("removendo",NomeDiretorioAntigo+"Quebrado")
    try:
        shutil.rmtree(NomeDiretorioAntigo+"Quebrado")
    except:
        print("Diretorio ja nao existe")
    try:
        os.rename(NomeDiretorioNovo,NomeDiretorioAntigo)
        os.rename(NomeDiretorioNovo+"Quebrado",NomeDiretorioAntigo+"Quebrado")
    except:
        print("diretorios novos nao existem")

    print("atualizado com sucesso")
    return 0
    
def Main():
    userResponse=''
    print("Ola bem vindo ao autobot de downloads\n")
    print(
          """
             _________            .___         .___ ___.           ________        _______       __
             \_   ___ \  ____   __| _/____   __| _/ \_ |__ ___.__. \_____  \  _____\   _  \     |__|
             /    \  \/ /  _ \ / __ |/ __ \ / __ |   | __ <   |  |   _(__  < /  ___/  /_\  \    |  |
             \     \___(  <_> ) /_/ \  ___// /_/ |   | \_\ \___  |  /       \\___ \\  \_/   \   |  |
              \______  /\____/\____ |\___  >____ |   |___  / ____| /______  /____  >\_____  /\__|  |
                     \/            \/    \/     \/       \/\/             \/     \/       \/\______|\n""")

    while (userResponse!='s' and userResponse!= 'n'):
        userResponse=input("É a sua primeira vez rodando Esta aplicacao? (s/n)\n")
    if  userResponse=='s':
        
        userResponse=''
        while (userResponse!='sim' and userResponse!= 'nao'):
            userResponse=input("Voce tem certeza q ira sobreEscrever a base de dados, digite sim? sim/nao\n")
            if userResponse=='sim':
                print("Vamos criar o dataBase de instalacao")
                CriarDataBase(NomeDiretorioAntigo)
                print("Tudo pronto, volte amanha para comparar os dados, por hj fique atento a maior data de cada arquivo")
            elif userResponse=='nao':
                break

    userResponse=''
    while (userResponse!='s' and userResponse!= 'n'):
        userResponse=input("Deseja baixar os novos arquivos e tentar atualizar o database? (s/n)\n")
    if userResponse=='s':
        print("criando banco de dados")
        CriarDataBase(NomeDiretorioNovo)
        print("banco de dados criado")
    userResponse=''
    while (userResponse!='s' and userResponse!= 'n'):
        userResponse=input("Deseja comparar os novos arquivos com o database original? (s/n)\n")
    if userResponse=='s':
        CompararDataBase(NomeDiretorioAntigo+'\\',NomeDiretorioNovo+'\\')
        CompararDataBase(NomeDiretorioAntigo+"Quebrado\\",NomeDiretorioNovo+"Quebrado\\")
        
    userResponse=''
    while (userResponse!='s' and userResponse!= 'n'):
        userResponse=input("Deseja atualizar o banco de dados com os arquivos recém baixados? (s/n)\n")
    if userResponse=='s':
        AtualizarDiretorios()
    print("fim da aplicacao")
        
        
    
        
        
        
Main()    
#ChecarDiferencas('ProcessosDeOntemQuebrado\\'+'2011.134.00199.html','ProcessosDeHojeQuebrado\\'+'2011.134.00199.html')
#ObterData('ProcessosDeHojeQuebrado\\'+'2011.134.00199.html')
#CriarDataBase(NomeDiretorioAntigo)

#CriarDataBase(NomeDiretorioNovo)



#CompararDataBase(NomeDiretorioAntigo+'\\',NomeDiretorioNovo+'\\')
#CompararDataBase(NomeDiretorioAntigo+"Quebrado\\",NomeDiretorioNovo+"Quebrado\\")
#ObterNumeroProcesso("Resultado da consulta processual.html")
#links=GerarLista(nomeLista)[0][0]
#print (links)
#RenomearArquivo("LinksQuebrados\\Resultado da consulta processual.html")#
#RecursaoMudarNome(30)

#print (ObterData(NomeDiretorioAntigo+"\\"+'1995.001.058367-5'+".html"))
    

#SalvarUrl('http://www4.tjrj.jus.br/consultaProcessoWebV2/consultaProc.do?v=2&FLAGNOME=&back=1&tipoConsulta=publica&numProcesso=2014.202.022796-4','testeutl.html')
#links=GerarLista(nomeLista)
#for url in links:
#    ConverterNome(url)

#AtualizarDiretorios()

#SalvarUrl("http://www4.tjrj.jus.br/ejud/ConsultaProcesso.aspx?N=2016.252.04264&USER=","proc3.html")








