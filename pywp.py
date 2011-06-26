import urllib2
import xml.parsers.expat

def predict(latitude, longitude) :
	url = 'http://forecast.weather.gov/MapClick.php?lat=%0.6f&lon=%0.6f&FcstType=digitalDWML' % (latitude, longitude)
	wstream = urllib2.urlopen(url)
	parse(wstream)
	wstream.close()

def parse(fh) :
	def start_element(name, attrs):
	    print 'Start element:', name, attrs
	def end_element(name):
	    print 'End element:', name
	def char_data(data):
	    print 'Character data:', repr(data)

	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data

	p.Parse(fh.read())

if __name__ == '__main__' :
	predict(41.837, -87.685)
