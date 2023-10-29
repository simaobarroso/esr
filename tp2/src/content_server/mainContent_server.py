import sys
from content_server import content_server

if __name__ == "__main__":
    try:
        ip_Server = sys.argv[1]
        port_Server = sys.argv[2]
        fileMetadados = sys.argv[3]
    except:
        print("ERRO: Não foi inserido o ficheiro de metadados dos vídeos ... ")
    
    # Criação do servidores de conteúdo 
    print("Servidor á escuta na porta "+ str(port_Server)+" com o IP "+str(ip_Server))
    content_server = content_server(fileMetadados,ip_Server,port_Server)
    content_server.sendFirstMessage()
    content_server.content_serverWork()