# Python
import socket
import subprocess

def client():
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Connect to the server
    client_socket.bind(('10.0.1.20', 12345))

    # Open a file to write the video data
    with open('received_video.mp4', 'wb') as video_file:
        while True:
            # Receive video data
            video_data, server_address = client_socket.recvfrom(4096)
            print("recebi")
            # Write video data to file
            video_file.write(video_data)

            # Open Firefox to play the video
            subprocess.call(['firefox', 'received_video.mp4'])
            #subprocess.call('xvfb-run firefox received_video.mp4', shell=True)

if __name__ == "__main__":
    client()