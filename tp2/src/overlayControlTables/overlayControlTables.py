""" Esta classe vai ser responsável pelo controlo da rede overlay, desde pedidos de streaming até cancelamento de streaming """
from threading import *
class streamRequest:
    """ Esta classe streamRequest gere os pedidos de stream de um determinado cliente """
    def __init__(self,destinoPedidoStream):
        self.destinoStream = destinoPedidoStream
        self.state = "closed"

class overlayControlTables:
    """ Esta classe é responsável pelo controlo dos pedidos de streaming que existem ao longo da rede de overlay """

    def __init__(self):
        self.lock = Lock()
        self.overlayStreams = {}
        self.statusOverlay = "closed"
    
    def no_overlayStreams(self):
        """ Verifica se existem overlayStreams ativas """
        self.lock.acquire()
        try:
            return len(self.overlayStreams) == 0
        finally:
            self.lock.release()
    
    def overlayStreams_Add(self,destinoStream):
        """Adiciona novas streams de overlay ao Controlo """
        self.lock.acquire()
        try:
            self.overlayStreams[destinoStream] = streamRequest(destinoStream)
        finally:
            self.lock.release()
    
    def overlayStreams_Status(self):
        """ Indica-nos o estado global das streams da rede overlay """
        self.lock.acquire()
        try:
            return self.statusOverlay
        finally:
            self.lock.release()
    
    def overlayStream_Status_Open(self,destinoStream):
        """ Muda o estado de uma stream de Overlay para open """
        self.lock.acquire()
        try:
            if destinoStream in self.overlayStreams:
                self.overlayStreams[destinoStream].state = "open"
                if self.overlayStreams[destinoStream].state != "open":
                    self.overlayStreams[destinoStream].state = "open"
        finally:
            self.lock.release()

    def overlayStream_Status_Close(self,destinoStream):
        """ Muda o estado de uma stream de Overlay para close """
        self.lock.acquire()
        try:
            if destinoStream in self.overlayStreams:
                self.overlayStreams[destinoStream].state = "close"
            self.check_statusOverlay()
        finally:
            self.lock.release()
    
    def check_statusOverlay(self):
        """ Verifica o status da rede overlay """
        fechado = True
        for k in self.overlayStreams.keys():
            if self.overlayStreams[k].state == 'open':
                fechado = False
        if fechado:
            self.statusOverlay = "closed"

    def overlayStream_Delete(self,destinoStream):
        """ Remoção de uma stream da rede de overlay """
        self.lock.acquire()
        try:
           del self.overlayStreams[destinoStream]
           if self.statusOverlay != "closed":
               self.check_statusOverlay()
        finally:
            self.lock.release()

    def allStreams_Opened(self):
        """ Streams de vídeo que se encontram todas a 'open' """
        self.lock.acquire()
        try:
            entradas = []
            for k in self.overlayStreams.keys():
               if self.overlayStreams[k].state == 'open':
                   entradas.append(self.overlayStreams[k])
            return entradas
        finally:
            self.lock.release()