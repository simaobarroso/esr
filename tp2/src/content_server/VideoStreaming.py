"""
Esta classe serve para a criação de frames para o vídeo que irá ser transmitido na stream 
"""
class VideoStreaming:
    def __init__(self,fileVideo):
        self.fileVideo = fileVideo   # Nome do ficheiro que contêm o vídeo
        self.numFrames = 0 # Número de frames que o vídeo possui 
