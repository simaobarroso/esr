""" Classe que contêm os pedidos de streaming que se encontram em toda a rede """

class RtspPacket:
    
    def __init__(self):
        pass

    def encode(self,type,payload):
        data = type + "."
        if payload:
            for value in payload:
                data = data + str(value)+";"
            
            data = data[:-1] + "."
        else:
            data += "."
        data.ljust(250,"0")
        return data.encode("utf-8")
    
    def decode(self,bytes):
        dados = bytes.decode("utf-8")
        dadosCampos = dados.split(".")

        self.type = dadosCampos[0]
        self.payload = dadosCampos[1].split(";")
        return self