import sys
from contentServer import contentServer
import threading
if __name__ == "__main__":
    try:
        ip_Server = sys.argv[1]        # Ip do servidor de conteúdo
        port_Server = sys.argv[2]      # Porta do servidor de conteúdo
        fileMetadados = sys.argv[3]    # Ficheiro de metadados do servidor de conteúdo
        ipBootStrapper = sys.argv[4]   # Ip do RP
        portBootStrapper = sys.argv[5] # Porta do RP
       
    except:
        print("ERRO: Não foi inserido o ficheiro de metadados dos vídeos ... ")
    
    # Criação do servidores de conteúdo 
    print("Servidor á escuta na porta "+ str(port_Server)+" com o IP "+str(ip_Server))
    content_server = contentServer(fileMetadados,ip_Server,port_Server,ipBootStrapper,int(portBootStrapper))
    content_server.run()
    
    