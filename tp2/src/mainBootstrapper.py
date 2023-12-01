import sys
from bootstrapper import bootstrapper

if __name__ == "__main__":
    try:
        ip_Server = sys.argv[1]
        port_Server = sys.argv[2]
        fileNetwork = sys.argv[3]
    except:
        print("ERRO: Não foram inseridos o IP do servidor, a Porta do servidor e o ficheiro de network logo não é possível realizar a comunicação ... ")

    # Criação do servidor bootstrapper
    print("Servidor á escuta na porta "+ str(port_Server)+" com o IP "+str(ip_Server))
    bootstrapper = bootstrapper(ip_Server,port_Server,fileNetwork)
    bootstrapper.bootstrapperWork()