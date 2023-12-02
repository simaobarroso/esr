""" Esta classe é responsável por albergar tudo o que seja relacionado com a transmissão do vídeo que se encontra no Content Server para o bootstrapper """
import traceback
from videoStream import videoStream
from RtpPacket import RtpPacket
from RtspPacket import RtspPacket
from random import randint
import threading
import socket
import sys
# RTP Port
RTP_port = 5555

class serverForStream:
    # RTSP States 
    SETUP = 'SETUP'
    PLAY = 'PLAY'
    PAUSE = 'PAUSE' 
    TEARDOWN = 'TEARDOWN' 

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
            dados = streamingSocket.recvfrom(1024)
            if dados:
                request = RtspPacket()
                request = request.decode(dados[0])
                print("Os dados recebidos foram:"+ request.type)
                self.processRtspRequest(request)


    
    def processRtspRequest(self,dados):
        """Process RTSP request sent from the client."""
        requestType = dados.type
        print(requestType)
        print("ESTOU AQUI ")
		# Process SETUP request
        if requestType == self.SETUP:
            if self.state == self.INIT:
				# Update state
                print("processing SETUP\n")
                self.infoClient['rtpSocket'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.state = self.READY
    
        # Process PLAY request 		
        elif requestType == self.PLAY:
            if self.state == self.READY:
                print("processing PLAY\n")
                self.state = self.PLAYING

        # Process PAUSE request
        elif requestType == self.PAUSE:
            if self.state == self.PLAYING:
                print("processing PAUSE\n")
                self.state = self.READY

        # Process TEARDOWN request
        elif requestType == self.TEARDOWN:
            print("processing TEARDOWN\n")

            # Close the RTP socket
            self.infoClient['rtpSocket'].close()

    def sendRtp(self):
        """Send RTP packets over UDP."""
        while True:
            self.infoClient['event'].wait(0.05) 
            data = self.infoClient['streaming'].nextFrame()
            if data: 
                frameNumber = self.infoClient['streaming'].frameNbr()
                try:
                    if self.state == self.PLAYING:
                        print("A enviar os pacotes do vídeo para o RP")
                        self.infoClient['rtpSocket'].sendto(self.makeRtp(data,frameNumber) ,self.client)
                except:
                    print("Connection Error")
                    print('-'*60)
                    traceback.print_exc(file=sys.stdout)
                    print('-'*60)
            else:
                self.infoClient['streaming'].reopen_video() # Envio em loop
    
    def makeRtp(self,payload,numberFrame):
        """ Criação de um pacote RTP para a streaming de vídeo """
        namevideo = self.infoClient['streaming'].filename
        version = 2
        padding = 0 
        extension = 0
        cc = 0 
        marker = 0
        pt = 26 # Type - MJPEG
        seqnum = numberFrame
        ssrc = 0

        rtp_packet = RtpPacket()
        rtp_packet.encode(namevideo,version,padding,extension,cc,seqnum,marker,pt,ssrc,payload)
        return rtp_packet.getPacket()