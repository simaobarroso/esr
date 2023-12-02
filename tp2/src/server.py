"""
Este servidor já é oNode uma vez que é basicamente cliente e servidor ao mesmo tempo, recebendo e enviando mensagens ao mesmo tempo. 
"""
import socket
import threading
import pickle
from RtspPacket import RtspPacket
from RtpPacket import RtpPacket

class server:
    def __init__(self,ip,port,ipBootStrapper,portBootStrapper):
        self.ip = ip # IP do servidor que queremos criar 
        self.port = int(port) # Porta do servidor com a qual queremos estabelecer conexão
        self.ipBootStrapper = ipBootStrapper
        self.portBootStrapper = portBootStrapper
        self.runningVideos = ["teste.Mjpeg"]  # TEM DE SER ALTERADO 
        self.paths = {} # Dicionário que armazena os caminhos recebidos por um determinado servidor 
        self.connectToNetwork()
        self.messages={}
        self.clients=[]
        self.lock = threading.Lock()

    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor irá receber pedidos dos clientes """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))

    def dataTratamentType3(self, message,address):
        """ Função de tratamento de dados para mensagens com o type == 3 """
        self.clients.append(address)
        if message["subtype"] == 'request': # Pedido de streaming de um vídeo por parte de um cliente 
                if message["nameVideo"] in self.runningVideos: # O router possui as streams de vídeo desejadas 
                    print("Vou dar a streaming de vídeo que o cliente pediu ...")
                else : # O router não possui a stream de vídeo desejada, logo terá de perguntar aos vizinhos se têm 
                    print("Flood da rede propagado para os vizinhos ...")
                    self.messages[message["id"]]=address
                    id_message=message["id"]
                    message=pickle.dumps({"type":4,"subtype":"request","id":id_message,"nameVideo":message["nameVideo"]})
                    for a in self.neighbors:
                        ip_Porta = a.split('-')
                        ip = ip_Porta[0]
                        port = int(ip_Porta[1])
                        if ip != address[0]:
                            self.socket.sendto(message,(ip,port))

    def dataTratamentType4(self,message,address):
        """ Função de tratamento de dados para mensagens com o type == 4 """
        if message["subtype"] == 'request':
                if message["nameVideo"] in self.runningVideos: # O router possui as streams de vídeo desejadas por isso vou mandar para o router vizinho
                    print("Vou dar a streaming de vídeo que o cliente pediu ...")
                else : # O router não possui a stream de vídeo desejada, logo terá de perguntar aos vizinhos se têm 
                    print("Flood da rede propagado para os vizinhos ...")
                    self.messages[message["id"]]=address
                    id_message=message["id"]
                    message=pickle.dumps({"type":4,"subtype":"request","id":id_message,"nameVideo":message["nameVideo"]})
                    for a in self.neighbors:
                        ip_Porta = a.split('-')
                        ip = ip_Porta[0]
                        port = int(ip_Porta[1])
                        if ip != address[0]:
                            self.socket.sendto(message,(ip,port))
        elif message["subtype"] == 'answer':
                print("Answer da rede propagado para quem enviou a pergunta")
                ip_dest= self.messages[message["id"]]
                message = pickle.dumps(message)
                for a in self.neighbors:
                    ip_Porta = a.split('-')
                    ip = ip_Porta[0]
                    port = int(ip_Porta[1])
                    if ip==ip_dest:
                        self.socket.sendto(message,(ip_dest,port))
                for cl in self.clients:
                    message=pickle.dumps({"type":3,"subtype":"answer","id":ip_dest,"data":"A stream pedida irá ser transmitida ..."})
                    self.socket.sendto(message,cl)
                self.clients = []

    def dataTratament(self,message,address):
        """ Função de tratamento dos dados recebidos no socket UDP """
        message = pickle.loads(message)
        if message["type"] == 3 : # Se o tipo da mensagem for de pedir uma stream de video por parte de um cliente 
            self.dataTratamentType3(message,address)
        if message["type"] == 4: # Se o tipo da mensagem for de fazer flood na rede 
            self.dataTratamentType4(message,address)

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

    def openRtpPort(self):
        """ Cria um socket RTP para receber o vídeo """
        self.rtpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        # self.rtpSocket.settimeout(0.5)

        try:
            self.rtpSocket.bind(('',5543))
            print("Bind do socket RTP")
        except:
            print("Erro no bind do socket ...")

    def listenRtp(self):
        """ Leitura dos pacotes RTP """
        while True:
            try:
                data = self.rtpSocket.recv(1024)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)
                    print("recebi")
                    currentNumberFrame = rtpPacket.seqNum()
                    # print("Este é o current Number Frame:" + str(currentNumberFrame))
                    th = threading.Thread(target= self.sendRtpForServers, args=(rtpPacket,)).start()
                    # th.join()
                    # Agora é transmitir para os vizinhos 
                    if currentNumberFrame > self.frameNbr:
                        self.frameNbr = currentNumberFrame
                        # Temos de ver o que fazer 
            except: # Para o vídeo quando está em PAUSE ou em TEARDOWN 
                #if self.playEvent.isSet():
                    #break

                #if self.teardownAcked == 1:
                    #self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    #self.rtpSocket.close()
                break
    
    def sendRtpForServers(self,rtpPacket):
        self.lock.acquire()
        try:
            lista = self.paths[rtpPacket.nameVideo()]
        finally:
            self.lock.release()
        nameVideo = str(rtpPacket.nameVideo())
        data = rtpPacket.getPayload()
        frameNumber = int(rtpPacket.seqNum())
        socketForServers = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        for elem in lista:
            print("Estou a retransmitir as streams para o endereço: "+ str(elem))
            socketForServers.sendto(RtpPacket.makeNewRtp(nameVideo,data,frameNumber),elem)

    
    def run(self):
        self.openRtpPort()
        th = threading.Thread(target= self.serverWork).start()
        th1 = threading.Thread(target= self.listenRtp).start()

