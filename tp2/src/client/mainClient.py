import sys
from client import client

if __name__ == "__main__":
    try:
        ip_Dest = sys.argv[1]
        port_Dest = sys.argv[2]
    except:
        print("ERRO: Não foram inseridos o IP destino, bem como a Porta destino, logo não é possível realizar a comunicação ... ")

    # Criação do cliente 
    cl = client(ip_Dest,port_Dest)
    cl.sendMessage()