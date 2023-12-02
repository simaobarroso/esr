import sys
from client import client

if __name__ == "__main__":
    try:
        ipHost = sys.argv[1]
        ip_bootstrapper = sys.argv[2]
        port_bootstrapper = sys.argv[3]
    except:
        print("ERRO: Não foram inseridos o IP destino, a Porta destino e o IP do host logo não é possível realizar a comunicação ... ")

    # Criação do cliente 
    cl = client(ipHost)
    cl.sendFirstMessage(ip_bootstrapper,int(port_bootstrapper))
    cl.receiveFirstMessage()
    cl.sendMessage()
    cl.receiveMessage()
    cl.run()