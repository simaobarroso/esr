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
        self.runningVideos = ["teste.Mjpeg"]  # TEM DE SER ALTERADO 
        self.paths = {} # Dicionário que armazena os caminhos recebidos por um determinado servidor 
        self.connectToNetwork()

    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor irá receber pedidos dos clientes """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))

    def dataTratament(self,message,address):
        """ Função de tratamento dos dados recebidos no socket UDP """
        # Tratamento da mensagem por parte do servidor
        message = pickle.loads(message)
        if message["type"] == 3 : # Pedido de flooding recebido por um router
            if message["subtype"] == 'request': # Pedido do flood
                # Temos de propagar o flood para os vizinhos do servidor 
                print("Flood da rede propagado para os vizinhos ...")
                message=pickle.dumps({"type":3,"subtype":'request'})
                for a in self.neighbors:
                    ip_Porta = a.split('-')
                    ip = ip_Porta[0]
                    port = int(ip_Porta[1])
                    self.socket.sendto(message,(ip,port))
            else : # Resposta do Flood 
                # Temos de propagar a resposta que o RP deu para o flood da rede, para os vizinhos 
                print("Esta parte é para a resposta de flood")
        elif message["type"] == 4 and message["subtype"] == 'request': # Pedido de streaming de um vídeo por parte de um cliente 
            if message["nameVideo"] in self.runningVideos:
                print("Vou dar a streaming de vídeo que o cliente pediu ...")
            else :
                print("Flood da rede propagado para os vizinhos ...")
                message=pickle.dumps({"type":3,"subtype":'request'})
                for a in self.neighbors:
                    ip_Porta = a.split('-')
                    ip = ip_Porta[0]
                    port = int(ip_Porta[1])
                    self.socket.sendto(message,(ip,port))

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

    def serverWork(self):
        """ Trabalho realizado pelo servidor para responder aos pedidos feitos pelos clientes """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.dataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos dos clientes
            t1.start()
            t1.join()
        
        self.socket.close()
    
