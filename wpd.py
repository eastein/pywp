import pywp
from zmq.core import context, socket, poll
import zmq
import memcache_exceptional
import time
import threading
import json

class WPD(threading.Thread) :
	def __init__(self) :
		threading.Thread.__init__(self)
		self.zmq_ctx = context.Context()
		self.zmq_sock = socket.Socket(self.zmq_ctx, zmq.REP)
		self.zmq_sock.bind('tcp://127.0.0.1:5555')

	def run(self) :
		while True :
			req = self.zmq_sock.recv()
			req = json.loads(req)
			print 'predicting... '
			pred = pywp.predict(req['lat'], req['long'])
			print 'predicted!'
			self.zmq_sock.send(json.dumps(pred))

if __name__ == '__main__' :
	d = WPD()
	d.run()#start()
	#d.join()
