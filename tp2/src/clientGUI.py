from tkinter import *
import threading
from RtpPacket import RtpPacket
import socket
from PIL import Image,ImageTk
from RtspPacket import RtspPacket
import tkinter.messagebox

CACHE_FILE_NAME = "cache"
CACHE_FILE_EXT = ".jpg"

class clientGUI:
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

    def __init__(self,master,neighbourAddress,socketStream):
        """ Inicialização do cliente """
        self.master = master 
        self.master.protocol("WM_DELETE_WINDOW",self.handler)
        self.createWidgets()
        self.rtspAddress = (neighbourAddress,5555)
        self.rtspSocket = socketStream
        self.rtspSeq = 0 
        self.requestSent = -1
        self.teardownAcked = 0
        self.frameNbr = 0
    
    def createWidgets(self):
        """Build GUI."""
        # Create Setup button
        self.setup = Button(self.master, width=20, padx=3, pady=3)
        self.setup["text"] = "Setup"
        self.setup["command"] = self.setupMovie
        self.setup.grid(row=1, column=0, padx=2, pady=2)

        # Create Play button		
        self.start = Button(self.master, width=20, padx=3, pady=3)
        self.start["text"] = "Play"
        self.start["command"] = self.playMovie
        self.start.grid(row=1, column=1, padx=2, pady=2)

        # Create Pause button			
        self.pause = Button(self.master, width=20, padx=3, pady=3)
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pauseMovie
        self.pause.grid(row=1, column=2, padx=2, pady=2)

        # Create Teardown button
        self.teardown = Button(self.master, width=20, padx=3, pady=3)
        self.teardown["text"] = "Teardown"
        self.teardown["command"] =  self.exitClient
        self.teardown.grid(row=1, column=3, padx=2, pady=2)

        # Create a label to display the movie
        self.label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 

    def setupMovie(self):
        """Setup button handler."""
        if self.state == self.INIT:
            self.sendRtspRequest(self.SETUP)
            self.state = self.READY
            self.openRtpPort()

    def exitClient(self):
        """ Teardown button handler """
        self.sendRtspRequest(self.TEARDOWN)
        self.master.destroy()

    def pauseMovie(self):
        """ Pause button handler """
        if self.state == self.PLAYING:
            self.sendRtspRequest(self.PAUSE)
            self.state = self.READY
            self.playEvent.set()
    
    def playMovie(self):
        """ Play button handler """
        if self.state == self.READY:
            threading.Thread(target=self.listenRtp).start()
            self.playEvent = threading.Event()
            self.playEvent.clear()
            self.sendRtspRequest(self.PLAY)
            self.state = self.PLAYING
    
    def listenRtp(self):
        """ Listen for RTP packets """
        while True:
            print("TESTE1")
            try:
                data = self.rtpSocket.recv(1024)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)
                    currentNumberFrame = rtpPacket.seqNum()
                    print("Estou a receber streams de vídeo dos meus vizinhos")
                    print("Este é o current Number Frame:" + str(currentNumberFrame))

                    #if currentNumberFrame > self.frameNbr:
                    #    self.frameNbr = currentNumberFrame
                    #    self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
            except: # Para o vídeo quando está em PAUSE ou em TEARDOWN 
                if self.playEvent.isSet():
                    print("TESTE2")
                    break

                if self.teardownAcked == 1:
                    print("TESTE3")
                    self.rtpSocket.shutdown(socket.SHUT_RDWR)
                    self.rtpSocket.close()
                break
    
    def writeFrame(self,data):
        print("TESTE5")
        cachename = CACHE_FILE_NAME + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()
        return cachename

    def updateMovie(self,imageFile):
        print("TESTE4")
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        print("TESTE6")
        self.label.configure(image = photo, heigth=288)
        print("TESTE7")
        self.label.image = photo
    
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
        elif requestCode == self.PAUSE and self.state == self.PLAYING:
            self.rtspSeq += 1
            print("Vamos dar PAUSE do vídeo")
            type_request = self.PAUSE
            self.requestSent = self.PAUSE
        elif requestCode == self.TEARDOWN and not self.state == self.INIT:
            self.rtspSeq += 1
            print("Vamos dar PAUSE do vídeo")
            type_request = self.TEARDOWN
            self.requestSent = self.TEARDOWN

        request = RtspPacket()
        request = request.encode(type_request,{})
        
        self.rtspSocket.sendto(request,self.rtspAddress)
    
    def openRtpPort(self):
        """ Cria um socket RTP para receber o vídeo """
        self.rtpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        # self.rtpSocket.settimeout(0.5)

        try:
            self.rtpSocket.bind(('',5543))
            print("Bind do socket RTP")
        except:
            tkinter.messagebox.showwarning("Bind error")
    
    def handler(self):
        self.pauseMovie()
        if tkinter.messagebox.askokcancel("Exit?"):
            self.exitClient()
        else:
            self.playMovie()