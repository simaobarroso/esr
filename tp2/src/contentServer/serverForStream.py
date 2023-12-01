""" Esta classe é responsável por albergar tudo o que seja relacionado com a transmissão do vídeo que se encontra no Content Server para o bootstrapper """
from videoStream.videoStream import *
from RtpPacket.RtpPacket import *
from random import randint
import threading
import socket
# RTP Port
RTP_port = 5543

class serverForStream:
    # RTSP States 
    SETUP = 'setup'
    PLAY = 'play'
    PAUSE = 'pause' 
    TEARDOWN = 'teardown' 

    # Streaming states
    INIT = 0 
    READY = 1 
    PLAYING = 2
    state = INIT 

    OK_200 = 0
    FILE_NOT_FOUND_404 = 1
    CON_ERR_500 = 2

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
            if dados:
                print("Data received:\n" + dados.decode("utf-8"))
                self.processRtspRequest(dados.decode("utf-8"))
    
    def processRtspRequest(self,dados):
        """Process RTSP request sent from the client."""
		# Get the request type
        request = dados.split('\n')
        line1 = request[0].split(' ')
        requestType = line1[0]
		
		# Get the media file name
        filename = line1[1]
		
		# Get the RTSP sequence number 
        seq = request[1].split(' ')
		
		# Process SETUP request
        if requestType == self.SETUP:
            if self.state == self.INIT:
				# Update state
                print("processing SETUP\n")
				
                try:
                    self.infoClient['videoStream'] = videoStream(filename)
                    self.state = self.READY
                except IOError:
                    self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])

                # Generate a randomized RTSP session ID
                self.infoClient['session'] = randint(100000, 999999)

                # Send RTSP reply
                self.replyRtsp(self.OK_200, seq[1])

                # Get the RTP/UDP port from the last line
                self.infoClient['rtpPort'] = request[2].split(' ')[3]
		
        # Process PLAY request 		
        elif requestType == self.PLAY:
            if self.state == self.READY:
                print("processing PLAY\n")
                self.state = self.PLAYING
                
                # Create a new socket for RTP/UDP
                self.infoClient["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                
                self.replyRtsp(self.OK_200, seq[1])
                
                # Create a new thread and start sending RTP packets
                self.infoClient['event'] = threading.Event()
                self.infoClient['worker']= threading.Thread(target=self.sendRtp) 
                self.infoClient['worker'].start()

        # Process PAUSE request
        elif requestType == self.PAUSE:
            if self.state == self.PLAYING:
                print("processing PAUSE\n")
                self.state = self.READY
                
                self.infoClient['event'].set()

                self.replyRtsp(self.OK_200, seq[1])

        # Process TEARDOWN request
        elif requestType == self.TEARDOWN:
            print("processing TEARDOWN\n")

            self.infoClient['event'].set()

            self.replyRtsp(self.OK_200, seq[1])

            # Close the RTP socket
            self.infoClient['rtpSocket'].close()

    def sendRtp(self):
        """Send RTP packets over UDP."""
        while True:
            self.infoClient['event'].wait(0.05) 

        # Stop sending if request is PAUSE or TEARDOWN
            if self.infoClient['event'].isSet(): 
                break 

            data = self.infoClient['videoStream'].nextFrame()
            if data: 
                frameNumber = self.infoClient['videoStream'].frameNbr()
                try:
                    address = self.infoClient['rtspSocket'][1][0]
                    port = int(self.infoClient['rtpPort'])
                    self.infoClient['rtpSocket'].sendto(self.makeRtp(data, frameNumber),(address,port))
                except:
                    print("Connection Error")
                    #print('-'*60)
                    #traceback.print_exc(file=sys.stdout)
                    #print('-'*60)
            else:
                self.infoClient['videoStream'].reopen_stream() # Envio em loop
    
    def replyRtsp(self, code, seq):
        """Send RTSP reply to the client."""
        if code == self.OK_200:
            #print("200 OK")
            reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.infoClient['session'])
            connSocket = self.infoClient['rtspSocket'][0]
            connSocket.send(reply.encode())

        # Error messages
        elif code == self.FILE_NOT_FOUND_404:
            print("404 NOT FOUND")
        elif code == self.CON_ERR_500:
            print("500 CONNECTION ERROR")