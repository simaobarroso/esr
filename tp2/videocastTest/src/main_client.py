from PyQt5.QtWidgets import QApplication

from client.client_gui import ClientWindow

import socket


if __name__ == '__main__':
    import sys

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = str(s.getsockname()[0])
    s.close()

    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0].split('/')[-1]} <file name> <host address> <host port> <RTP port>")
        exit(-1)

    file_name, host_address = *sys.argv[1:],

    try:
        host_port = 5543 #int(host_port)
        rtp_port = 5541 #int(rtp_port)
    except ValueError:
        raise ValueError('port values should be integer')

    app = QApplication(sys.argv)
    client = ClientWindow(file_name, host_address, host_port, rtp_port,ip)
    client.resize(400, 300)
    client.show()
    sys.exit(app.exec_())
