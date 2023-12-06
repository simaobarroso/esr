from tkinter import *
import threading
from RtpPacket import RtpPacket
import socket
from PIL import Image,ImageTk
from RtspPacket import RtspPacket
import tkinter.messagebox
import pickle

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
    FINISHING = 3 
    state = INIT 

    def __init__(self,master,neighbourAddress,socketStream,ipHost):
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
        self.ipHost= ipHost
    
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
        self.state = self.FINISHING
        #self.rtpSocket.shutdown(socket.SOCK_DGRAM)
        #self.rtpSocket.close()
        #self.rtpSocket=None
        #self.master.destroy()

    def pauseMovie(self):
        """ Pause button handler """
        if self.state == self.PLAYING:
            print("aqui")
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
            print(self.state)
            print("ainda entrei aqui")
            try:
                if self.state == self.PLAYING:
                    data = self.rtpSocket.recv(20480000)
                    if data:
                        rtpPacket = RtpPacket()
                        rtpPacket.decode(data)
                        currentNumberFrame = rtpPacket.seqNum()
                        print("Estou a receber streams de vídeo dos meus vizinhos")
                        print("Este é o current Number Frame:" + str(currentNumberFrame))
                        if currentNumberFrame > self.frameNbr :
                            self.frameNbr = currentNumberFrame
                        cachename = self.writeFrame(rtpPacket.getPayload())
                        self.updateMovie(cachename)
                
                elif self.state == self.FINISHING:
                    print("oleoleoleole")
                    self.rtpSocket.close()
                    #self.rtpSocket=None
                    self.master.destroy()
                    break
                
            except Exception as e: # Para o vídeo quando está em PAUSE ou em TEARDOWN 
                print ("Problema detetado: "+str(e))
        print("Esta fechado")

    def writeFrame(self,data):
        cachename = str(self.ipHost)+"_"+CACHE_FILE_NAME + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()

        return cachename

    def updateMovie(self,imageFile):
       
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        
        self.label.configure(image = photo, height=288)
        
        self.label.image = photo
    
    def sendRtspRequest(self,requestCode):
        """ Send RTSP request to the server content """
        is_req_code=True
        if requestCode == self.SETUP and self.state == self.INIT:
            print("Vamos dar SETUP do vídeo")
            self.rtspSeq += 1
            type_request = self.SETUP
            #self.requestSent = self.SETUP  
        elif requestCode == self.PLAY and self.state == self.READY:
            self.rtspSeq += 1
            print("Vamos dar PLAY do vídeo")
            type_request = self.PLAY
            #self.requestSent = self.PLAY
        elif requestCode == self.PAUSE and self.state == self.PLAYING:
            self.rtspSeq += 1
            print("Vamos dar PAUSE do vídeo")
            type_request = self.PAUSE
            #self.requestSent = self.PAUSE
        elif requestCode == self.TEARDOWN:
            is_req_code=False
            self.rtspSeq += 1
            print("Vamos dar TEARDOWN do vídeo")
            type_request = self.TEARDOWN
            message= pickle.dumps({"type":6,"subtype":"request","data":"Close rtp connection ...","nameVideo":""})
        else:
            print("Comando errado")

        if is_req_code:    
            request = RtspPacket()
            request = request.encode(type_request,{})
            self.rtspSocket.sendto(request,self.rtspAddress)
        else:
            print("Caminho certo2")
            self.rtspSocket.sendto(message,('0.0.0.0',7777))
            print("Certissimo")

    def openRtpPort(self):
        """ Cria um socket RTP para receber o vídeo """
        self.rtpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        self.rtpSocket.settimeout(1)

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