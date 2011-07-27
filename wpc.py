from zmq.core import context, socket, poll
import zmq
import json

class WPC(threading.Thread) :
        def __init__(self, url) :
                self.zmq_ctx = context.Context()
                self.zmq_sock = socket.Socket(self.zmq_ctx, zmq.REQ)
                self.zmq_sock.connect(url)

	def predict(self, lat, long) :
		req = json.dumps({'lat' : lat, 'long' : long})
		self.zmq_sock.send(req)
		return json.loads(self.zmq_sock.recv())
