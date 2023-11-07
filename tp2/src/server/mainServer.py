import sys
from server import server

if __name__ == "__main__":
    try:
        ip_Server = sys.argv[1]
        port_Server = sys.argv[2]
        ipBootStrapper = sys.argv[3]
        portBootStrapper = sys.argv[4]
    except:
        print("ERRO: Não foram inseridos os inputs pedidos, logo não é possível realizar a comunicação ... ")
    
    # Criação do servidor 
    print("Servidor á escuta na porta "+ str(port_Server)+" com o IP "+str(ip_Server))
    sv = server(ip_Server,port_Server,ipBootStrapper,int(portBootStrapper))
    sv.sendFirstMessage(ipBootStrapper,int(portBootStrapper))
    sv.serverWork()