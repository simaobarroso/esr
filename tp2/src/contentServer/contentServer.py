"""
Este servidor é um servidor que serve de distribuidor de conteúdo para a rede. 
Possui os vídeos que tem de espalhar na rede, em loop, transmitindo-os em unicast para o bootstrapper
Possui também um ficheiro com metadados dos vídeos que irá transmitir quando tiver clientes ligados ao serviço 
"""
import socket
import threading
import json 
import pickle
from time import sleep
from threading import Thread
from typing import Union

from utils.video_stream import VideoStream
from utils.rtsp_packet import RTSPPacket
from utils.rtp_packet import RTPPacket

class contentServer:
    FRAME_PERIOD = 1000//VideoStream.DEFAULT_FPS  # in milliseconds
    SESSION_ID = '123456'
    DEFAULT_CHUNK_SIZE = 4096
    # for allowing simulated non-blocking operations
    # (useful for keyboard break)
    RTSP_SOFT_TIMEOUT = 100  # in milliseconds

    class STATE:
        """ Classe para definir o estado vídeo """
        INIT = 0
        PAUSED = 1
        PLAYING = 2
        FINISHED = 3
        TEARDOWN = 4

    def __init__(self,fileMetadados,ip,port,ipBootStrapper,portBootStrapper):
        self.ip = ip
        self.port = int(port) 
        self.port_TCP = int(5543)
        self.ip_RP= ipBootStrapper
        self.port_RP = portBootStrapper
        self.fileVideos = fileMetadados
        self.metadata = {}
        self.connectToNetwork()
        self.numberAnswer = 0 
        self._video_stream: Union[None, VideoStream] = None
        self._rtp_send_thread: Union[None, Thread] = None
        self._rtsp_connection: Union[None, socket.socket] = None
        self._rtp_socket: Union[None, socket.socket] = None
        self._client_address: (str, int) = None
        self.server_state: int = self.STATE.INIT
        
    
    
    def connectToNetwork(self):
        """ Criação do socket UDP a partir do qual o servidor de conteúdo irá receber pedidos do bootstrapper e enviar os vídeos para serem transmitidos """
        self.socket = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip,self.port))
        self.RP_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
        self.RP_socket.bind((self.ip,self.port_TCP))
        self.RP_socket.listen(1)

    
    def metadataVideos(self):
        """ Leitura dos metadados existentes no ficheiro self.fileVideos """
        f = open(self.fileVideos)
        self.metadata = json.load(f)
        f.close()

    def sendFirstMessage(self):
        """ Envio dos metadados dos vídeos que possui para o servidor bootstrapper """
        message = pickle.dumps({"type":2,"data":self.metadata})         # A mensagem segue serializada 
        self.socket.sendto(message,(self.ip_RP,self.port_RP))

    def _get_rtsp_packet(self) -> RTSPPacket:
        return RTSPPacket.from_request(self._rtsp_recv())
    
    def _rtsp_recv(self, size=DEFAULT_CHUNK_SIZE) -> bytes:
        recv = None
        while True:
            try:
                recv = self._rtsp_connection.recv(size)
                break
            except socket.timeout:
                continue
        print(f"Received from client: {repr(recv)}")
        return recv
    
    def _setup_rtp(self, video_file_path: str):
        print(f"Opening up video stream for file {video_file_path}")
        self._video_stream = VideoStream(video_file_path)
        print('Setting up RTP socket...')
        self._rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._start_rtp_send_thread()

    def _start_rtp_send_thread(self):
        self._rtp_send_thread = Thread(target=self._handle_video_send)
        self._rtp_send_thread.setDaemon(True)
        self._rtp_send_thread.start()

    def _handle_video_send(self):
        print(f"Sending video to {self._client_address[0]}:{self._client_address[1]}")
        while True:
            if self.server_state == self.STATE.TEARDOWN:
                return
            if self.server_state != self.STATE.PLAYING:
                sleep(0.5)  # diminish cpu hogging
                continue
            if self._video_stream.current_frame_number >= VideoStream.VIDEO_LENGTH-1:  # frames are 0-indexed
                print('Reached end of file.')
                print('Video begin again ...')
            frame = self._video_stream.get_next_frame()
            frame_number = self._video_stream.current_frame_number
            rtp_packet = RTPPacket(
                payload_type=RTPPacket.TYPE.MJPEG,
                sequence_number=frame_number,
                timestamp=frame_number*self.FRAME_PERIOD,
                payload=frame
            )
            print(f"Sending packet #{frame_number}")
            print('Packet header:')
            rtp_packet.print_header()
            packet = rtp_packet.get_packet()
            self._send_rtp_packet(packet)
            sleep(self.FRAME_PERIOD/1000.)

    def _send_rtp_packet(self, packet: bytes):
        to_send = packet[:]
        while to_send:
            try:
                self._rtp_socket.sendto(to_send[:self.DEFAULT_CHUNK_SIZE], self._client_address)
            except socket.error as e:
                print(f"failed to send rtp packet: {e}")
                return
            # trim bytes sent
            to_send = to_send[self.DEFAULT_CHUNK_SIZE:]

    def _rtsp_send(self, data: bytes) -> int:
        print(f"Sending to client: {repr(data)}")
        return self._rtsp_connection.send(data)
    
    def _send_rtsp_response(self, sequence_number: int):
        response = RTSPPacket.build_response(sequence_number, self.SESSION_ID)
        self._rtsp_send(response.encode())
        print('Sent response to client.')

    def setupVideo(self,address_rp):
        """ Envio dos pacotes com a streaming de vídeo """
        if self.numberAnswer < 1:
            while True:
                packet = self._get_rtsp_packet()
                self._client_address = (address_rp[0], packet.rtp_dst_port)
                self._setup_rtp(packet.video_file_path)
                self._send_rtsp_response(packet.sequence_number)
                self.numberAnswer = self.numberAnswer + 1
                break
    
    def content_serverDataTratament(self,message,address):
        """ Função de tratamento de dados recebidos pelo servidor de bootstrapper """
    
    def content_serverWork_UDP(self):
        """ Trabalho realizado pelo servidor de conteúdo para responder aos pedidos de transmissão feitos pelo servidor bootstrapper """
        while True:
            message, address = self.socket.recvfrom(1024)     # O servidor pode receber até 1024 bytes de informação
            t1 = threading.Thread(target=self.content_serverDataTratament,args=(message,address),name='t1') # Criação de threads para responder aos pedidos do bootstrapper
            t1.start()
    def content_serverWork_TCP(self):
        """ Trabalho realizado pelo servidor de conteúdo para responder aos pedidos de transmissão feitos pelo servidor bootstrapper """
        self._rtsp_connection,address_rp = self.RP_socket.accept()  
        self._rtsp_connection.settimeout(self.RTSP_SOFT_TIMEOUT/1000.)
        t1 = threading.Thread(target=self.setupVideo,args=(address_rp,),name='t1') # Criação de threads para responder aos pedidos do bootstrapper
        t1.start()
