import socket
import pickle
from tkinter import Tk
from clientGUI import clientGUI
class client:
    def __init__(self,ipHost):
        self.ipHost = ipHost # IP do próprio cliente
        self.connectToNetwork() # Socket responsável pela conexão entre o cliente e o servidor
        self.ip = "" #endereço do servidor a contactar
        self.port = 7777 # porta do servidor a contactar

    def connectToNetwork(self):
        """ Criação do socket UDP para a ligação entre cliente e servidor """
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind((self.ipHost,7777))
        self.socketStream = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socketStream.bind((self.ipHost,5555))

    def sendMessage(self):
        """ Envio de uma mensagem do cliente para o servidor vizinho """
        print("VOU ENVIAR UMA MENSAGEM PARA O MEU VIZINHO A PEDIR UMA STREAM DE VÍDEO")
        message = pickle.dumps({"type":4,"subtype":"request","id":self.ipHost,"nameVideo":"movie.Mjpeg"}) # Mensagem de um cliente para o servidor vizinho, para pedir uma stream 
        self.socket.sendto(message,(self.ip,self.port))
   
    # Mensagem para o bootstraper a pedir vizinhos
    def sendFirstMessage(self,ip,port):
        """ Envio da mensagem inicial de um cliente para um bootstrapper """
        message =pickle.dumps({"type":1,"ip":self.ipHost})
        self.socket.sendto(message,(ip,port))

    # Ler a Mensagem de resposta do bootstraper a pedir vizinhos
    def receiveFirstMessage(self):
        """ Receção da primeira mensagem vinda do bootstrapper e tratamento da mesma """
        message, address = self.socket.recvfrom(1024)
        print("O servidor com este endereço: %s enviou uma mensagem " % str(address))
        neighbors = pickle.loads(message)
        data = neighbors["data"][0]
        listData = data.split('-')
        self.ip = listData[0]
        self.port = int(listData[1])
        print("Mensagem recebida: O servidor contactável é este: "+self.ip+" na porta: "+str(self.port))

    def dataTratamentType3(self, message,address):
        """ Função de tratamento de dados para mensagens com o type == 3 """
        if message["subtype"] == 'answer': # Pedido de streaming de um vídeo por parte de um cliente 
            message = pickle.dumps({"type":5,"nameVideo":"movie.Mjpeg"})
            self.socket.sendto(message,(self.ip,7777))
            print("ENVIEI")
    
    # Dar teardown à stream
    def dataTratamentType6(self, message,address):
        """ Função de tratamento de dados para mensagens com o type == 3 """
        message["nameVideo"]="movie.Mjpeg"
        message = pickle.dumps(message)
        self.socket.sendto(message,(self.ip,7777))
        
                
    def receiveMessage(self):
        while True:
            """ Receção de mensagens e tratamento das mesmas por parte do cliente """
            message, address = self.socket.recvfrom(1024)
            message = pickle.loads(message)
            print(message)
            if message["type"]==6:
                self.dataTratamentType6(message,address) 
            else:
                self.dataTratamentType3(message,address)
    
    def client_run(self):
        """ Interface gráfica co cliente """
        root = Tk()
        app = clientGUI(root,self.ip,self.socketStream,self.ipHost)
        app.master.title(" Streaming de vídeo ")
        root.mainloop()

    def run(self):
        """ Criação da interface gráfica do cliente """
        self.client_run()

