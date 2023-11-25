"""
Este servidor é um servidor que serve de distribuidor de conteúdo para a rede. 
Possui os vídeos que tem de espalhar na rede, em loop, transmitindo-os em unicast para o bootstrapper
Possui também um ficheiro com metadados dos vídeos que irá transmitir quando tiver clientes ligados ao serviço 
"""
import socket
import threading
import json 
import pickle
from time import sleep
from threading import Thread
from typing import Union



class contentServer:
    

    def __init__(self,fileMetadados,ip,port,ipBootStrapper,portBootStrapper):
        self.ip = ip
        self.port = int(port) 
        self.port_TCP = int(5543)
        self.ip_RP= ipBootStrapper
        self.port_RP = portBootStrapper
        self.fileVideos = fileMetadados
        self.metadata = {}
        self.connectToNetwork()
        self.numberAnswer = 0 
        
    
    
    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor de conteúdo irá receber pedidos do bootstrapper e enviar os vídeos para serem transmitidos """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))
        self.RP_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.RP_socket.bind((self.ip,self.port_TCP))
        self.RP_socket.listen(1)

    
    def metadataVideos(self):
        """ Leitura dos metadados existentes no ficheiro self.fileVideos """
        f = open(self.fileVideos)
        self.metadata = json.load(f)
        f.close()

    def sendFirstMessage(self):
        """ Envio dos metadados dos vídeos que possui para o servidor bootstrapper """
        message = pickle.dumps({"type":2,"data":self.metadata})         # A mensagem segue serializada 
        self.socket.sendto(message,(self.ip_RP,self.port_RP))

    def dataTratamentType5(self,rp,message):
        """ Função de tratamento de dados para mensagens com o type == 5 """
        if self.numberAnswer < 1:
            if message["subtype"] == 'request' : # Pedido de uma stream de vídeo por parte de um RP ao contentServer 
                if message["data"] == self.metadata["nameMovie"]:
                    answer = pickle.dumps({"type":5,"subtype":"answer","data":"Frames do vídeo irão ser enviados ..."})
                    rp.send(answer)
                    self.numberAnswer = self.numberAnswer + 1
                else:
                    answer = pickle.dumps({"type":5,"subtype":"answer","data":"Não possuo esse vídeo ..."})
                    rp.send(answer)
                    self.numberAnswer = self.numberAnswer + 1

    def content_serverDataTratament(self,message,address):
        """ Função de tratamento de dados recebidos pelo servidor de bootstrapper """
        message = pickle.loads(message)
        if message["type"] == 5:
            self.dataTratamentType5(message,address)
    
    def videoStreaming(self,rp):
        """ Função de tratamento de pedidos de streaming recebidos pelo servidor de bootstrapper """
        message = rp.recv(232)
        message = pickle.loads(message)
        if message["type"] == 5:
            self.dataTratamentType5(rp,message)

    def content_serverWork_UDP(self):
        """ Trabalho realizado pelo servidor de conteúdo para responder aos pedidos de transmissão feitos pelo servidor bootstrapper """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.content_serverDataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos do bootstrapper
            t1.start()
    def content_serverWork_TCP(self):
        """ Trabalho realizado pelo servidor de conteúdo para responder aos pedidos de transmissão feitos pelo servidor bootstrapper """
        # rp.settimeout(self.RTSP_SOFT_TIMEOUT/1000.)
        while True:
            rp,address_rp = self.RP_socket.accept()
            t1 = threading.Thread(target=self.videoStreaming,args=(rp,),name='t1') # Criação de threads para responder aos pedidos do bootstrapper
            t1.start()
