import socket
class server:
    def __init__(self,ip,port):
        self.ip = ip # IP do servidor que queremos criar 
        self.port = int(port) # Porta do servidor com a qual queremos estabelecer conexão
        self.connectToNetwork()

    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor irá receber pedidos dos clientes """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))

    def serverWork(self):
        """ Trabalho realizado pelo servidor para responder aos pedidos feitos pelos clientes """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            print("O cliente com este endereço: %s submetou pedidos " % str(address))
            print("Mensagem recebida : %s" % message.decode())

