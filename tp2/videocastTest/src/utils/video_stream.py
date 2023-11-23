class VideoStream:
    FRAME_HEADER_LENGTH = 5
    DEFAULT_IMAGE_SHAPE = (380, 280)
    VIDEO_LENGTH = 500
    DEFAULT_FPS = 24

    # if it's present at the end of chunk,
    # it's the last chunk for current jpeg (end of frame)
    JPEG_EOF = b'\xff\xd9'

    def __init__(self, file_path: str):
        # for simplicity, mjpeg is assumed to be on working directory
        self._stream = open(file_path, 'rb')
        # frame number is zero-indexed
        # after first frame is sent, this is set to zero
        self.current_frame_number = -1

    def close(self):
        self._stream.close()
    
    def get_next_frame(self) -> bytes:
        try:
            frame_length = self._stream.read(self.FRAME_HEADER_LENGTH)
            if not frame_length:
                # Reset the stream to the beginning when reaching the end
                self._stream.seek(0)
                frame_length = self._stream.read(self.FRAME_HEADER_LENGTH)
                if not frame_length:
                    raise EOFError
        except EOFError:
            raise EOFError

        frame_length = int(frame_length.decode())
        frame = self._stream.read(frame_length)

        if self.current_frame_number == self.VIDEO_LENGTH - 1:
            self.current_frame_number = 0
            print(self.current_frame_number)
        else:
            self.current_frame_number += 1

        return bytes(frame)
