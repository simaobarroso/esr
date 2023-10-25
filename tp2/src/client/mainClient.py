import sys
from client import client

if __name__ == "__main__":
    try:
        ip_Dest = sys.argv[1]
        port_Dest = sys.argv[2]
        ipHost = sys.argv[3]
        ip_bootstrapper = sys.argv[4]
        port_bootstrapper = sys.argv[5]
    except:
        print("ERRO: Não foram inseridos o IP destino, a Porta destino e o IP do host logo não é possível realizar a comunicação ... ")

    # Criação do cliente 
    cl = client(ip_Dest,port_Dest,ipHost)
    cl.sendFirstMessage(ip_bootstrapper,int(port_bootstrapper))
    cl.receiveFirstMessage()
    cl.sendMessage()
    cl.receiveMessage()