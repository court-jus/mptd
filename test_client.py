from twisted.internet import reactor, protocol
from twisted.protocols import basic

game = None
connection = None
serverFound = False

class Game(object):
    
    def __init__(self):
        print "INIT"

    def tick(self):
        print "TICK"

    def mainloop (self, fps = 10): 
        print "MAINLOOP"
    
        self._exit = 0 
    
        def _loop():
            if self._exit:
                return
        
            self.tick () 
        
            reactor.callLater(1./fps, _loop)
        _loop()    
   
class MyProtocol(basic.LineReceiver):
    delimiter = '\n'
    def connectionMade(self):
        global connection
        connection = self
        print 'Connection Made'
            
    def lineReceived(self, data):
        print "Data received", data
        
    def connectionLost(self, reason):
        print 'Connection Lost:', reason
        try:
            reactor.stop()
        except:
            pass

class MyFactory(protocol.ClientFactory):
    protocol = MyProtocol

class ServerFinder(protocol.DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
        global serverFound
        if not serverFound:
            reactor.connectTCP(host, int(data), MyFactory())
            serverFound = True
        
def main():
    global game
    t = reactor.listenUDP(0, ServerFinder())
    t.write('find', ('224.0.0.1', 9300))
    game = Game()

    # Initialize game looping
    game.mainloop()
    reactor.run()

if __name__ == '__main__':
    main()
