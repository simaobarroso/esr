
import sys
from time import time
HEADER_SIZE = 12

class RtpPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		pass
		
	def encode(self,nameVideo,version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
		"""Encode the RTP packet with header fields and payload."""
		timestamp = int(time())
		header = bytearray(HEADER_SIZE) 
		header[0] = (header[0] | version << 6) & 0xC0; # 2 bits
		header[0] = (header[0] | padding << 5); # 1 bit
		header[0] = (header[0] | extension << 4); # 1 bit
		header[0] = (header[0] | (cc & 0x0F)); # 4 bits
		header[1] = (header[1] | marker << 7); # 1 bit
		header[1] = (header[1] | (pt & 0x7f)); # 7 bits
		header[2] = (seqnum >> 8); 
		header[3] = (seqnum & 0xFF);
		header[4] = (timestamp >> 24);
		header[5] = (timestamp >> 16) & 0xFF;
		header[6] = (timestamp >> 8) & 0xFF;
		header[7] = (timestamp & 0xFF);
		header[8] = (ssrc >> 24);
		header[9] = (ssrc >> 16) & 0xFF;
		header[10] = (ssrc >> 8) & 0xFF;
		header[11] = ssrc & 0xFF
		# set header and  payload
		self.filenameSize = len(nameVideo).to_bytes(4, byteorder='big')
		self.filename = nameVideo.encode("utf-8")
		self.header = self.filenameSize + self.filename + header 
		self.payload = payload
		
	def decode(self, byteStream):
		"""Decode the RTP packet."""
		self.filenameSize = int.from_bytes(byteStream[:4], byteorder='big')
		self.filename = byteStream[4:self.filenameSize + 4].decode("utf-8")
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]
	
	def version(self):
		"""Return RTP version."""
		return int(self.header[0] >> 6)
	
	def nameVideo(self):
		""" Return a name video """
		return self.filename
	
	def seqNum(self):
		"""Return sequence (frame) number."""
		seqNum = self.header[2] << 8 | self.header[3]
		return int(seqNum)
	
	def timestamp(self):
		"""Return timestamp."""
		timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)
	
	def payloadType(self):
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)
	
	def getPayload(self):
		"""Return payload."""
		return self.payload
		
	def getPacket(self):
		"""Return RTP packet."""
		return self.header + self.payload

	#def printheader(self):
	#	print("[RTP Packet] Version: ...")
	
	def printheader(self):
		"""Pretty print header."""
		print("[RTP Packet] Version:", self.version())
		print("[RTP Packet] Name video:", self.nameVideo())
		print("[RTP Packet] Sequence Number:", self.seqNum())
		print("[RTP Packet] Timestamp:", self.timestamp())
		print("[RTP Packet] Payload Type:", self.payloadType())

	def makeNewRtp(name,data,frameNumber):

		version = 2
		padding = 0 
		extension = 0
		cc = 0 
		marker = 0
		pt = 26 # Type - MJPEG
		seqnum = frameNumber
		ssrc = 0
		payload = data
		nameVideo = name 

		rtpPacket = RtpPacket()
		rtpPacket.encode(nameVideo,version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		return rtpPacket.getPacket()