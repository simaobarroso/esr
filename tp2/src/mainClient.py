import sys
from client import client
import threading

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
    th2 = threading.Thread(target = cl.receiveMessage,name="th2")
    th1 = threading.Thread(target= cl.run,name="th1")
    th1.start()
    th2.start()
    th1.join()
    th2.join()