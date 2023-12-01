""" Esta classe é responsável por albergar tudo o que seja relacionado com a transmissão do vídeo que se encontra no Content Server para o bootstrapper """
from videoStream.videoStream import *
from RtpPacket.RtpPacket import *
import threading
# RTP Port
RTP_port = 5543

class serverForStream:
    # RTSP States 
    SETUP = 'setup'
    PLAY = 'play'
    PAUSE = 'pause' 
    TEARDOWN = 'teardown' 

    # RTP Port
    RTP_port = 5543

    # Streaming states
    INIT = 0 
    READY = 1 
    PLAYING = 2
    state = INIT 


    def __init__(self, ipBootstrapper,metadata,socket):
        """ Inicialização do servidor de streaming de video """
        self.infoClient={}
        self.client=(ipBootstrapper,RTP_port)
        try:
            self.infoClient['streaming'] = videoStream(metadata["nameMovie"])
        except:
            print("404 - Ficheiro não encontrado")
        self.infoClient["socketStream"] = socket

    def makeRtp(payload,numberFrame):
        """ Criação de um pacote RTP para a streaming de vídeo """
        version = 2
        padding = 0 
        extension = 0
        cc = 0 
        marker = 0
        pt = 26 # Type - MJPEG
        seqnum = numberFrame
        ssrc = 0

        rtp_packet = RtpPacket()
        rtp_packet = RtpPacket.encode(version,padding,extension,cc,seqnum,marker,pt,ssrc,payload)
        return rtp_packet.getPacket()
    
    def run(self):
        """Função responsável por responder a pedidos RTSP e de enviar as respostas a esses mesmos pedidos """
        threading.Thread(target = self.receiveRtsp).start()

        # Criamos uma nova thread para simplesmente responder aos pedidos dos cliente 
        self.infoClient['event'] = threading.Event()
        self.infoClient['worker'] = threading.Thread(target = self.sendRtp).start()
    
    def receiveRtsp(self):
        """ Tratamento dos pedidos de controlo de RTP , isto é RTSP """
        streamingSocket = self.infoClient["socketStream"]
        while True:
            dados = streamingSocket.recvfrom()
            #TO DO 