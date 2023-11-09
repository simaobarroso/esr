import sys
from contentServer import contentServer

if __name__ == "__main__":
    try:
        ip_Server = sys.argv[1]
        port_Server = sys.argv[2]
        fileMetadados = sys.argv[3]
        ipBootStrapper = sys.argv[4]
        portBootStrapper = sys.argv[5]
    except:
        print("ERRO: Não foi inserido o ficheiro de metadados dos vídeos ... ")
    
    # Criação do servidores de conteúdo 
    print("Servidor á escuta na porta "+ str(port_Server)+" com o IP "+str(ip_Server))
    content_server = contentServer(fileMetadados,ip_Server,port_Server,ipBootStrapper,int(portBootStrapper))
    content_server.metadataVideos()
    content_server.sendFirstMessage()
    content_server.content_serverWork()