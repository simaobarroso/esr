import socket
import pickle
class client:
    def __init__(self,ipHost):
        self.ipHost = ipHost # IP do próprio cliente
        self.connectToNetwork() # Socket responsável pela conexão entre o cliente e o servidor
        self.neighbors_IP_Port = []
    
    def connectToNetwork(self):
        """ Criação do socket UDP para a ligação entre cliente e servidor """
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def sendMessage(self):
        """ Envio de uma mensagem do cliente para o servidor vizinho """
        print("VOU ENVIAR UMA MENSAGEM PARA O MEU VIZINHO A PEDIR UMA STREAM DE VÍDEO")
        message = pickle.dumps({"type":4,"subtype":"request","id":self.ipHost,"nameVideo":"movie.Mjpeg"}) # Mensagem de um cliente para o servidor vizinho, para pedir uma stream 
        self.socket.sendto(message,(self.ip,self.port))
    
    def sendFirstMessage(self,ip,port):
        """ Envio da mensagem inicial de um cliente para um bootstrapper """
        message =pickle.dumps({"type":1,"ip":self.ipHost})
        self.socket.sendto(message,(ip,port))

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

    def receiveMessage(self):
        """ Receção de mensagens e tratamento das mesmas por parte do cliente """
        message, address = self.socket.recvfrom(1024)
        print("O servidor com este endereço: %s enviou uma mensagem " % str(address))
        print("Mensagem recebida : %s" % str(message.decode()))
    