"""
Este servidor é um servidor que serve de distribuidor de conteúdo para a rede. 
Possui os vídeos que tem de espalhar na rede, em loop, transmitindo-os em unicast para o bootstrapper
Possui também um ficheiro com metadados dos vídeos que irá transmitir quando tiver clientes ligados ao serviço 
"""
import socket
import threading

class content_server:
    def __init__(self,fileVideos):
        self.fileVideos = fileVideos # Ficheiro que contém os metadados dos vídeos que o servidor possui para transmissão
        self.connectToNetwork()
    
    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor de conteúdo irá receber pedidos do bootstrapper e enviar os vídeos para serem transmitidos """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))
    
    def metadataVideos(self):
        """ Leitura dos metadados existentes no ficheiro self.fileVideos """
        f = open(self.fileVideos)