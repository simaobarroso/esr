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
        """ Envio de uma mensagem do cliente para o servidor escolhido """
        message = "Esta mensagem é um teste há conexão da rede, para a etapa 1 do TP de ESR ...".encode()
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
        self.neighbors_IP_Port = neighbors[self.ipHost][0].split('-')
        self.ip = self.neighbors_IP_Port[0]
        self.port = int(self.neighbors_IP_Port[1])
        print("Mensagem recebida: O servidor contactável é este: "+self.ip+" na porta: "+str(self.port))

    def receiveMessage(self):
        """ Receção de mensagens e tratamento das mesmas por parte do cliente """
        message, address = self.socket.recvfrom(1024)
        print("O servidor com este endereço: %s enviou uma mensagem " % str(address))
        print("Mensagem recebida : %s" % str(message.decode()))
    