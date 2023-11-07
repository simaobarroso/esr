"""
Esta classe serve para a criação de frames para o vídeo que irá ser transmitido na stream 
"""
class VideoStreaming:
    def __init__(self,fileVideo):
        self.fileVideo = fileVideo   # Nome do ficheiro que contêm o vídeo
        self.numFrame = 0           # Número de frame que em que o vídeo está
        try:
            self.file = open(self.fileVideo, 'rb')    # Ficheiro de vídeo 
        except:
            print("ERRO: Erro na leitura do ficheiro de vídeo ...")

    def anotherFrame(self):
        """ Função que nos dá o próximo frame de um determinado vídeo  """
        dados = self.file.read(5) # Obtenção do framelength dos primeiros 5 bits do vídeo 
        if dados:
            frameLength = int(dados)   # Irá possuir o comprimento de cada frame do vídeo
            dados = self.file.read(frameLength) # Leitura do frame atual do vídeo que está a ser transmitido 
            self.numFrame += 1
        return dados

    def getNumFrame(self):
        """ Função que nos dá o frame atual do vídeo que está a ser transmitido """
        return self.numFrame

        
