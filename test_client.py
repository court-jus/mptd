#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol
from twisted.protocols import basic

game = None
connection = None
serverFound = False

class GameNetwork(object):
    
    def tick(self, serverFound, connection):
        pass

    def mainloop (self, fps = 10): 
        global connection, serverFound
        self._exit = 0 
    
        def _loop():
            if self._exit:
                return
            self.tick(serverFound, connection) 
            reactor.callLater(1./fps, _loop)
        _loop()    
   
class MptdLineReceiver(basic.LineReceiver):

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

class MptdClientFactory(protocol.ClientFactory):
    protocol = MptdLineReceiver

class ServerFinder(protocol.DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
        global serverFound
        if not serverFound:
            reactor.connectTCP(host, int(data), MptdClientFactory())
            serverFound = True
        
def main():
    global game
    t = reactor.listenUDP(0, ServerFinder())
    t.write('find', ('224.0.0.1', 9300))
    game = GameNetwork()

    # Initialize game looping
    game.mainloop()

    # Launch twisted main loop
    reactor.run()

if __name__ == '__main__':
    main()
