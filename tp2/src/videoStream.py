""" Classe responsável pela transmissão do vídeo em streaming """
class videoStream:
    def __init__(self,filename):
        """ Leitura do ficheiro de video e inicialização do número de frames """
        self.filename = filename
        try:
            self.ficheiro = open(filename,'rb')
        except:
            raise IOError
        self.frameNumber = 0 
    
    def nextFrame(self):
        """ Função que nos dá a próxima frame do vídeo """
        dados = self.ficheiro.read(5) # Comprimento das frames dos primeiros 5 bits 
        if dados:
            framelength = int(dados)
            # Leitura do frame atual 
            dados = self.ficheiro.read(framelength)
            self.frameNumber += 1
        return dados
    
    def frameNbr(self):
        """ Função que nos dá o número de frames """
        return self.frameNumber
    
    def reopen_video(self):
        """ Reabre novamente o ficheiro de vídeo """
        try:
            self.ficheiro = open(self.filename, 'rb')
            self.frameNumber = 0 
        except:
            raise IOError
