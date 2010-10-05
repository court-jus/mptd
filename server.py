from twisted.internet import reactor, protocol
from itertools import count

# list of clients currently connected
clients = []

# an incrementing number
clientcounter = count(1)

class MyProtocol(protocol.Protocol):
	def connectionMade(self):
		'''
		When a connection is made, we tell everyone that that person
		has joined, using a number from the clientcounter
		'''
		self.clientnum = clientcounter.next()
		clients.append(self)
		print 'Client joined', self.clientnum
		for client in clients:
			client.transport.write("%s joined\n" % (self.clientnum,))

		
	def dataReceived(self, data):
		'''
		Announce data to everyone connected when it arrives.
		
		if 'quit' is sent, we disconnect from that client.
		'''
		print self.clientnum, 'said', data.strip()
		for client in clients:
			client.transport.write("%s said %s\n" % (self.clientnum, data.rstrip()))
		if data.strip() == 'quit':
			self.transport.loseConnection()
			
	def connectionLost(self, reason):
		'''
		Clean up clients list to not include this client.
		'''
		clients.remove(self)
		print 'Client quit', self.clientnum

class MyFactory(protocol.Factory):
	protocol = MyProtocol
	
class AnnounceServer(protocol.DatagramProtocol): 
	def datagramReceived(self, data, (host, port)):
        	self.transport.write(str(theport) + '\n', (host, port))

def main():
	global theport
	
	# start a chat server
	port = reactor.listenTCP(0, MyFactory())
	
	# start a udp listener
	reactor.listenUDP(9300, AnnounceServer())
	
	# record the port the chat server is listening on
	theport = port.getHost().port
	
	# print it out so we can see.
	print 'the port is', theport
		
	# Run The Network Event Loop
	reactor.run()
	
	
if __name__ == '__main__':
	main()
