import socket
class client:
    def __init__(self,ip,port):
        self.ip = ip # IP do servidor que é contactado pelo cliente
        self.port = int(port) # Número da porta do servidor que é contactado pelo cliente
        self.connectToNetwork() # Socket responsável pela conexão entre o cliente e o servidor
    
    def connectToNetwork(self):
        """ Criação do socket UDP para a ligação entre cliente e servidor """
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    def sendMessage(self):
        """ Envio de uma mensagem do cliente para o servidor escolhido """
        message = "Isto é um teste para o checkpoint 1 de ESR ...".encode() 
        self.socket.sendto(message,(self.ip,self.port))
    
    def receiveMessage(self):
        message, address = self.socket.recvfrom(1024)
        print("O servidor com este endereço: %s enviou uma mensagem " % str(address))
        print("Mensagem recebida : %s" % message.decode())
    