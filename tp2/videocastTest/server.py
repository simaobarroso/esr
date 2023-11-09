# Python
import socket
import time

def server():
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to a specific network interface and port number
    server_socket.connect(('10.0.1.20', 12345))

    # Open the video file
    with open('./file_example_MP4_640_3MG.mp4', 'rb') as video_file:
        while True:
            # Read video data
            video_data = video_file.read(4096)
            
            # If no more data, loop from the beginning
            if not video_data:
                video_file.seek(0)
                video_data = video_file.read(4096)
           
            # Send video data
            server_socket.sendto(video_data, ('10.0.1.20', 12345))

            # Wait for a short period of time
            time.sleep(0.02)

if __name__ == "__main__":
    server()