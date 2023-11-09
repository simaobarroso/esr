"""
Este servidor já é oNode uma vez que é basicamente cliente e servidor ao mesmo tempo, recebendo e enviando mensagens ao mesmo tempo. 
"""
import socket
import threading
import pickle

class server:
    def __init__(self,ip,port,ipBootStrapper,portBootStrapper):
        self.ip = ip # IP do servidor que queremos criar 
        self.port = int(port) # Porta do servidor com a qual queremos estabelecer conexão
        self.ipBootStrapper = ipBootStrapper
        self.portBootStrapper = portBootStrapper
        self.runningVideos = []
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

    def sendFirstMessage(self,ip,port):
        """ Envio da mensagem inicial de um servidor oNode para um bootstrapper, para saber os seus vizinhos """
        message =pickle.dumps({"type":1,"ip":self.ip})
        self.socket.sendto(message,(ip,port))
    
    def receiveFirstMessage(self):
        """ Receção da primeira mensagem vinda do bootstrapper e tratamento da mesma """
        message, address = self.socket.recvfrom(1024)
        print("O servidor com este endereço: %s enviou uma mensagem " % str(address))
        message = pickle.loads(message)
        if message["type"] == 1: # Pedido dos vizinhos por parte de um router ao RP
            self.neighbors = message["data"]
            print("Mensagem recebida: Os servidores contactáveis são estes: "+str(self.neighbors))
        elif message["type"] == 3 : # Pedido de flooding recebido por um router
            print("Reenchaminhamento das mensagens de flood ...")
        elif message["Type"] == 4: # Pedido de streaming de um vídeo por parte de um cliente 
            if message["nameVideo"] in self.runningVideos:
                print("Vou dar a streaming de vídeo que o cliente pediu ...")
            else :
                print("Acontece a mesma coisa que no message[type] == 3")

    def serverWork(self):
        """ Trabalho realizado pelo servidor para responder aos pedidos feitos pelos clientes """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.dataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos dos clientes
            t1.start()
            t1.join()
        
        self.socket.close()
    
