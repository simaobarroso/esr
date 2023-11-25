from server.server import Server
import socket


if __name__ == '__main__':
    import sys
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = str(s.getsockname()[0])
    s.close()

    try:
        port = 5543 #int(sys.argv[1])
        #ip = sys.argv[2]
    except ValueError:
        raise ValueError('port value should be integer')

    while True:
        server = Server(port,ip)
        try:
            server.setup()
            server.handle_rtsp_requests()
        except ConnectionError as e:
            server.server_state = server.STATE.TEARDOWN
            print(f"Connection reset: {e}")
