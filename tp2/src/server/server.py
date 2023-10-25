"""
Este servidor já é oNode uma vez que é basicamente cliente e servidor ao mesmo tempo, recebendo e enviando mensagens ao mesmo tempo. 
"""
import socket
import threading

class server:
    def __init__(self,ip,port):
        self.ip = ip # IP do servidor que queremos criar 
        self.port = int(port) # Porta do servidor com a qual queremos estabelecer conexão
        self.connectToNetwork()

    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor irá receber pedidos dos clientes """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))

    def dataTratament(self,message,address):
        """ Função de tratamento dos dados recebidos no socket UDP """
        # Tratamento da mensagem por parte do servidor
        print("O cliente com este endereço: %s submetou pedidos " % str(address))
        print("Mensagem recebida : %s" % message.decode())
        # Envio da resposta ao cliente 
        answer = "Teste de resposta a um cliente por parte de um servidor oNode ...".encode()
        self.socket.sendto(answer,address)

    def serverWork(self):
        """ Trabalho realizado pelo servidor para responder aos pedidos feitos pelos clientes """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.dataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos dos clientes
            t1.start()
            t1.join()
        
        self.socket.close()
    
