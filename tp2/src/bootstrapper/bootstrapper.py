"""
Este servidor é o servidor que serve de tracker/bootstrapper para a rede
É contactado pelos nodos existentes na rede, para estes poderem determinar quais são os seus nodos vizinhos 
"""
import socket
import threading
import json 
import pickle

from utils.rtsp_packet import RTSPPacket
from utils.rtp_packet import RTPPacket
from utils.video_stream import VideoStream

class bootstrapper:
    DEFAULT_CHUNK_SIZE = 4096
    DEFAULT_RECV_DELAY = 20  # in milliseconds
    RTP_SOFT_TIMEOUT = 5  # in milliseconds
    # for allowing simulated non-blocking operations
    # (useful for keyboard break)
    RTSP_SOFT_TIMEOUT = 100  # in milliseconds
    # if it's present at the end of chunk, client assumes
    # it's the last chunk for current frame (end of frame)
    PACKET_HEADER_LENGTH = 5

    def __init__(self,ip,port,fileNetwork):
        self.ip = ip # IP do servidor bootstrapper
        self.port = int(port) # Porta do servidor bootstrapper 
        self.fileNetwork = fileNetwork # Nome do ficheiro que possui a topologia da rede 
        self.connectToNetwork()
        self.dataNetwork()
        self.lock = threading.Lock()
        self.trees = {}
        self.movies = []
    
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
        self.contentServer = address[0]

    def dataTratamentType4(self,message,address):
        """ Função de tratamento de dados para mensagens com o type == 4 """
        if message["subtype"] == 'request':  # Resposta ás mensagens de flood recebidas pelo RP 
                if message["nameVideo"] in self.movies:
                    self.lock.acquire()
                    try:
                        self.trees[address] = message["nameVideo"]
                    finally:
                        self.lock.release()
                    answer=pickle.dumps({"type":4,"subtype":"answer","id":message["id"],"data":"I'm the RP ..."})
                    self.socket.sendto(answer,address)
                    # Conexão entre RP e o contentServer para pedir uma stream de vídeo ... 
                    """
                    self.cs_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.cs_socket.connect((self.contentServer,int(5543)))
                    request = pickle.dumps({"type":5,"subtype":"request","data":message["nameVideo"]})
                    self.cs_socket.send(request)
                    self.dataTratamentType5()
                    """
                    self._rtsp_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self._rtsp_connection.connect((self.contentServer, 5543))
                    self._rtsp_connection.settimeout(self.RTSP_SOFT_TIMEOUT / 1000.)
                    self.is_rtsp_connected = True
                    request_type=RTSPPacket.SETUP
                    self.file_path = message["nameVideo"]
                    self._current_sequence_number = 0 
                    self.session_id = ''
                    request = RTSPPacket(
                        request_type,
                        self.file_path,
                        self._current_sequence_number,
                        5543,
                        self.session_id
                    ).to_request()
                    print(f"Sending request: {repr(request)}")
                    self._rtsp_connection.send(request)
                    self._current_sequence_number += 1
                    return self._get_response()
                
    def _get_response(self, size=DEFAULT_CHUNK_SIZE) -> RTSPPacket:
        rcv = None
        while True:
            try:
                rcv = self._rtsp_connection.recv(size)
                break
            except socket.timeout:
                continue
        print(f"Received from server: {repr(rcv)}")
        response = RTSPPacket.from_response(rcv)
        return response
    def dataTratamentType5(self):
        """ Função de tratamento de dados para mensagens com o type == 5 """
        message = self.cs_socket.recv(1024)
        message = pickle.loads(message)
        if message["subtype"] == 'answer':  # Resposta ás mensagens de flood recebidas pelo RP 
            print(message)

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


    def bootstrapperWork(self):
        """ Trabalho realizado pelo servidor bootstrapper para responder aos pedidos feitos pelos clientes """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.bootstrapperDataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos dos clientes
            t1.start()
            t1.join()
        
        self.socket.close()