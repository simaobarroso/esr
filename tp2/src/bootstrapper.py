"""
Este servidor é o servidor que serve de tracker/bootstrapper para a rede
É contactado pelos nodos existentes na rede, para estes poderem determinar quais são os seus nodos vizinhos 
"""
import socket
import threading
import json 
import pickle
from RtspPacket import RtspPacket
from RtpPacket import RtpPacket
import time 

packet_times = []
packet_counter = 0 
throughput = 0.0
latency = 0.0
reliability = 0.0 
class bootstrapper:

    # Estado de streaming de video entre o RP e o content Server
    INIT = 0 
    READY = 1 
    PLAYING = 2
    state = INIT 

    # Tipos de mensagens RTSP 
    SETUP = 'SETUP'
    PLAY = 'PLAY'
    TEARDOWN = 'TEARDOWN'

    
    def __init__(self,ip,port,fileNetwork):
        self.ip = ip # IP do servidor bootstrapper
        self.port = int(port) # Porta do servidor bootstrapper 
        self.fileNetwork = fileNetwork # Nome do ficheiro que possui a topologia da rede 
        self.connectToNetwork()
        self.dataNetwork()
        self.lock = threading.Lock()
        self.trees = {}
        self.movies = []
        self.rtspSeq = 0
        self.frameNbr = 0 
        self.contentServer = ""
        self.listContentServer = []
        self.rtspSocket=None

    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor bootstrapper irá receber pedidos dos clientes """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))
    
    def dataNetwork(self):
        """ Leitura dos dados existentes no ficheiro self.fileNetwork """
        f = open(self.fileNetwork)
        self.data = json.load(f)
        f.close()

    def dataTratamentType2(self,message,address):
        """ Função de tratamento de dados para mensagens com o type == 2 """
        self.movies.append(message["data"]["nameMovie"])
        self.listContentServer.append(address[0])
        global packet_counter
        packet_counter += 1 # Cálculo do número de pacotes recebidos
        current_time = time.time() # Cálculo do timestamp do pacote 
        packet_times.append(current_time) # Inserção dos timestamp numa lista
        self.calculate_metrics()

    def dataTratamentType4(self,message,address):
        """ Função de tratamento de dados para mensagens com o type == 4 """
        if message["subtype"] == 'request':  # Resposta ás mensagens de flood recebidas pelo RP
            print(message["id"]) 
            answer=pickle.dumps({"type":4,"subtype":"answer","id":message["id"],"data":0,"nameVideo":message["nameVideo"]})
            self.socket.sendto(answer,address)
            # Conexão entre RP e o contentServer para pedir uma stream de vídeo ... 
            #self.rtspSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            #self.rtspSocket.bind(('',5543))
            #self.setupMovie()
            #self.playMovie()
    
    def dataTratamentType5(self,message,address):
        print("AQUI AGORA")
        """ Função de tratamento de dados para mensagens com o type == 5 """
        if message["nameVideo"] in self.movies:
            self.lock.acquire()
            try:
                if message["nameVideo"] not in self.trees:
                    self.trees[message["nameVideo"]] = []
                self.trees[message["nameVideo"]].append(address)
            finally:
                self.lock.release()
        # Conexão entre RP e o contentServer para pedir uma stream de vídeo ...
        if self.rtspSocket == None or not isinstance(self.rtspSocket, socket.socket):
            self.rtspSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.rtspSocket.bind(('',5543))
            self.rtpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.rtpSocket.bind(('',5555))
        self.setupMovie()
        self.playMovie()

    def dataTratamentType6(self,message,address):
        """ Tratamento das mensagens do tipo 6 """
        print("ESTOU A TRATAR AS MENSAGENS COM O TIPO 6 ")
        if message["subtype"] == "request" and message["data"] == "Close rtp connection ...":
            if message["nameVideo"] in self.movies:
                print("Lista de envio de streams antes da remoção: "+str(self.trees[message["nameVideo"]]))
                self.lock.acquire()
                try:
                    self.trees[message["nameVideo"]].remove(address)
                    #if self.trees[message["nameVideo"]]==[]:
                        #self.trees.pop(message["nameVideo"])
                    #self.state=self.INIT
                finally:
                    self.lock.release()
                print("Lista de envio de streams depois da remoção: "+str(self.trees[message["nameVideo"]]))
                self.sendRtspRequest(self.TEARDOWN)
            if len(self.trees)==0:
                print("AQUI")
                self.rtpSocket.close()
                self.rtpSocket=None
                self.rtspSocket.close()
                self.rtspSocket=None
            else:
                print("NÃO ESTOU A TRANSMITIR ESSE VÍDEO ...")
        
                    
  
    def bootstrapperDataTratament(self,message,address):
        """ Função de tratamento dos dados recebidos no socket UDP """
        print("O cliente com este endereço: %s submetou pedidos " % str(address))
        message = pickle.loads(message)
        if message["type"] == 1: # Resposta a pedidos dos routers, para saberem os seus vizinhos
            print("Mensagem recebida : %s" % str(message))
            message = message["ip"]  # Mensagem recebida pelo bootstrapper ->  É apenas um endereço IP, no caso de ser contactado pelos clientes no início de conexão
            answer=pickle.dumps({"type":1,"data":self.data[message]})
            self.socket.sendto(answer,address)
        elif message["type"] == 2:  # Receção do ficheiro de metadados proveniente do servidor de conteúdos
            self.dataTratamentType2(message,address)
        elif message["type"] == 4:
            self.dataTratamentType4(message,address)
        elif message["type"] == 5:
            self.dataTratamentType5(message,address)    
        elif message["type"] == 6:
            self.dataTratamentType6(message,address) 


    def bootstrapperWork(self):
        """ Trabalho realizado pelo servidor bootstrapper para responder aos pedidos feitos pelos clientes """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.bootstrapperDataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos dos clientes
            t1.start()
    
    def sendRtspRequest(self,requestCode):
        """ Send RTSP request to the server content """
        if requestCode == self.SETUP and self.state == self.INIT:
            print("Vamos dar SETUP do vídeo")
            self.rtspSeq += 1
            type_request = self.SETUP
            self.requestSent = self.SETUP  
        elif requestCode == self.PLAY and self.state == self.READY:
            self.rtspSeq += 1
            print("Vamos dar PLAY do vídeo")
            type_request = self.PLAY
            self.requestSent = self.PLAY
        elif requestCode == self.TEARDOWN and self.state == self.PLAYING:
            self.rtspSeq += 1
            print("Vamos dar TEARDOWN do vídeo")
            type_request = self.TEARDOWN
            self.requestSent = self.TEARDOWN
        else:
            print(requestCode)
            print(self.state)

        request = RtspPacket()
        request = request.encode(type_request,{})
        #print("Estou a enviar um pedido RTSP para este contentServer: "+ str(self.contentServer))
        self.rtspSocket.sendto(request,(self.contentServer,7777))

    def setupMovie(self):
        print("VOU MANDAR SEGUNDO PEDIDO")
        print(self.state)
        """Vamos dar SETUP do vídeo"""
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)
            self.state = self.READY
            self.openRtpPort()
        
        else:
            self.state=self.INIT
            self.sendRtspRequest(self.SETUP)
            self.state = self.READY
            self.openRtpPort()
    
    def openRtpPort(self):
        """ Cria um socket RTP para receber o vídeo """
        self.rtpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        self.rtpSocket.settimeout(0.5)

        try:
            self.rtpSocket.bind(('',5555))
            print("Bind do socket RTP")
        except:
            print("Erro no bind do socket ...")

    def listenRtp(self):
        """ Leitura dos pacotes RTP """
        while True:
            try:
                data = self.rtpSocket.recv(20480000)
            except:
                print("Socket desativado")
                break
            global packet_counter
            packet_counter += 1 # Cálculo do número de pacotes recebidos
            current_time = time.time() # Cálculo do timestamp do pacote 
            packet_times.append(current_time) # Inserção dos timestamp numa lista
            self.calculate_metrics()
            #print("Estou a enviar um pedido RTSP para este contentServer: "+ str(self.contentServer))
            if data:
                rtpPacket = RtpPacket()
                rtpPacket.decode(data)
                

                currentNumberFrame = rtpPacket.seqNum()
                # print("Este é o current Number Frame:" + str(currentNumberFrame))
                th = threading.Thread(target= self.sendRtpForServers, args=(rtpPacket,)).start()
                # th.join()
                # Agora é transmitir para os vizinhos 
                if currentNumberFrame > self.frameNbr:
                    self.frameNbr = currentNumberFrame
                    # Temos de ver o que fazer

    def playMovie(self):
        """ O RP pede o vídeo ao Contente Server """
        if self.state == self.READY:
            threading.Thread(target=self.listenRtp).start()
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)
            self.state = self.PLAYING

    def sendRtpForServers(self,rtpPacket):
        self.lock.acquire()
        try:
            lista = self.trees[rtpPacket.nameVideo()]
        finally:
            self.lock.release()
        nameVideo = str(rtpPacket.nameVideo())
        data = rtpPacket.getPayload()
        frameNumber = int(rtpPacket.seqNum())
        #print("Estou a mandar este frame number:"+ str(frameNumber))
        socketForServers = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        for ip,port in lista:
            
            #print("Estou a retransmitir as streams para o endereço: "+ str((ip,5543)))
            socketForServers.sendto(RtpPacket.makeNewRtp(nameVideo,data,frameNumber),(ip,5543))
    
    def calculate_metrics(self):
        """ Função para monitorização dos servidores de conteúdo """

        global packet_counter, packet_times, throughput, latency, reliability
        throughputTemp = packet_counter / 10 # assume 10 segundos como janela de tempo
        latencyTemp = sum(packet_times) / len(packet_times)
        reliabilityTemp = (1 - len(packet_times) / 1000) * 100 # supondo 1000 pacotes na janela de tempo
        if latencyTemp > latency:
            latency = latencyTemp
            throughput = throughputTemp
            reliability = reliabilityTemp
            for item in self.listContentServer:
                if item != self.contentServer:
                    self.contentServer = item
        else:
            latency = latencyTemp
            throughput = throughputTemp
            reliability = reliabilityTemp


