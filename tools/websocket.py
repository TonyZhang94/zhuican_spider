# -*- coding: utf-8 -*-
import socket
import sys
import base64
import hashlib
import time

HOST = '127.0.0.1'
# PORT = 4567
MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
                   "Upgrade:WebSocket\r\n" \
                   "Connection: Upgrade\r\n" \
                   "Sec-WebSocket-Accept: {1}\r\n" \
                   "WebSocket-Location: ws://{2}/chat\r\n" \
                   "WebSocket-Protocol:chat\r\n\r\n"


class websocket():
	def __init__(self, port):
		self.port = port
		
	def start(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			self.sock.bind((HOST, self.port))  # 绑定ip port
			self.sock.listen(100)
		except Exception, e:
			print('bind error')
			print(e)
			sys.exit()
		while True:
			self.conn, self.address = self.sock.accept()  # sock, addr = self._sock.accept()
			try:
				headers = {}
				shake = self.conn.recv(1024)  # 接收握手数据
				
				# print shake
				
				if not len(shake):
					print('len error')
					return False
				
				header, data = shake.split('\r\n\r\n', 1)
				for line in header.split('\r\n')[1:]:
					key, value = line.split(': ', 1)
					headers[key] = value
				
				if 'Sec-WebSocket-Key' not in headers:
					print('this is not websocket, client close.')
					print headers
					self.conn.close()
					
					return False
				
				sec_key = headers['Sec-WebSocket-Key']
				res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())
				
				str_handshke = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', HOST + ":" + str(self.port))
				# print str_handshke
				
				self.conn.send(str_handshke)  # 握手
				time.sleep(2)
				return self.conn, self.sock
			except Exception as e:
				print '握手失败'
				print(e)
				
	def close(self):
		self.conn.close()
		self.sock.close()


if __name__ == '__main__':
	websocket = websocket(5788)
	print '5788'
	try:
		conn, sock = websocket.start()
		print 'conn success'
		i = 0
		while i < 10:
			conn.send('%c%c%s' % (0x81, len(str(i)), str(i)))
			time.sleep(1)
			i += 1
		conn.close()
		sock.close()
	
	except Exception as e:
		print(e)
