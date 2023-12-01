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
from serverForStream import serverForStream

class contentServer:

    def __init__(self,fileMetadados,ip,port,ipBootStrapper,portBootStrapper):
        self.ip = ip
        self.port = int(port) 
        self.ip_RP= ipBootStrapper
        self.port_RP = portBootStrapper
        self.fileVideos = fileMetadados
        self.metadata = {}
        self.connectToNetwork()
        
    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor de conteúdo irá receber pedidos do bootstrapper e enviar os vídeos para serem transmitidos """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))
        self.socketStream = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        
    def metadataVideos(self):
        """ Leitura dos metadados existentes no ficheiro self.fileVideos """
        f = open(self.fileVideos)
        self.metadata = json.load(f)
        f.close()

    def sendFirstMessage(self):
        """ Envio dos metadados dos vídeos que possui para o servidor bootstrapper """
        message = pickle.dumps({"type":2,"data":self.metadata})         # A mensagem segue serializada 
        self.socket.sendto(message,(self.ip_RP,self.port_RP))

    def run(self):
        """ Função responsável por ler o ficheiro de metadados, enviar esse mesmo ficheiro para o bootstrapper, e lançar o serverForStream """
        self.metadataVideos()
        self.sendFirstMessage()
        serverForStream(self.ip_RP,self.metadata,self.socket).run()

  
