"""
Este servidor é o servidor que serve de tracker/bootstrapper para a rede
É contactado pelos nodos existentes na rede, para estes poderem determinar quais são os seus nodos vizinhos 
"""
import socket
import threading
import json 
import pickle
class bootstrapper:
    def __init__(self,ip,port,fileNetwork):
        self.ip = ip # IP do servidor bootstrapper
        self.port = int(port) # Porta do servidor bootstrapper 
        self.fileNetwork = fileNetwork # Nome do ficheiro que possui a topologia da rede 
        self.connectToNetwork()
        self.dataNetwork()
    
    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor bootstrapper irá receber pedidos dos clientes """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))
    
    def dataNetwork(self):
        """ Leitura dos dados existentes no ficheiro self.fileNetwork """
        f = open(self.fileNetwork)
        self.data = json.load(f)
        f.close()

    def bootstrapperDataTratament(self,message,address):
        """ Função de tratamento dos dados recebidos no socket UDP """
        print("O cliente com este endereço: %s submetou pedidos " % str(address))
        message = pickle.loads(message)
        if message["type"] == 1:
            print("Mensagem recebida : %s" % str(message))
            message = message["ip"]  # Mensagem recebida pelo bootstrapper ->  É apenas um endereço IP, no caso de ser contactado pleos clientes no início de conexão
            answer=pickle.dumps({"type":1,"data":self.data[message]})
            self.socket.sendto(answer,address)
        elif message["type"] == 2:  
            print("Mensagem recebida: %s" % str(message))
        elif message["type"] == 3:
            self.socket.sendto("I'm the RP".encode(),address)

    def bootstrapperWork(self):
        """ Trabalho realizado pelo servidor bootstrapper para responder aos pedidos feitos pelos clientes """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.bootstrapperDataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos dos clientes
            t1.start()
            t1.join()
        
        self.socket.close()