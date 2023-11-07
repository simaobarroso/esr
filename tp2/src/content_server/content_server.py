"""
Este servidor é um servidor que serve de distribuidor de conteúdo para a rede. 
Possui os vídeos que tem de espalhar na rede, em loop, transmitindo-os em unicast para o bootstrapper
Possui também um ficheiro com metadados dos vídeos que irá transmitir quando tiver clientes ligados ao serviço 
"""
import socket
import threading
import json 
import pickle

class content_server:
    def __init__(self,fileMetadados,ip,port,ipBootStrapper):
        self.ip = ip
        self.port = int(port) 
        self.ip_RP= ipBootStrapper
        self.port_RP = 7777
        self.fileVideos = fileMetadados
        self.metadata = {}
        self.connectToNetwork()
    
    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor de conteúdo irá receber pedidos do bootstrapper e enviar os vídeos para serem transmitidos """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))
    
    def metadataVideos(self):
        """ Leitura dos metadados existentes no ficheiro self.fileVideos """
        f = open(self.fileVideos)
        self.metadata = json.load(f)
        f.close()

    def sendFirstMessage(self):
        """ Envio dos metadados dos vídeos que possui para o servidor bootstrapper """
        message = pickle.dumps({"type":2,"data":self.metadata})         # A mensagem segue serializada 
        self.socket.sendto(message,(self.ip_RP,self.port_RP))
    
    def content_serverDataTratament(self,message,address):
        """ Função de tratamento de dados recebidos pelo servidor de bootstrapper """
        print("O cliente com este endereço: %s submetou pedidos " % str(address))
        print("Mensagem recebida : %s" % message.decode())

    def content_serverWork(self):
        """ Trabalho realizado pelo servidor de conteúdo para responder aos pedidos de transmissão feitos pelo servidor bootstrapper """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.content_serverDataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos do bootstrapper
            t1.start()
            t1.join()

        self.socket.close()