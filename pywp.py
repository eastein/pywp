import pprint
import urllib2
import xml.parsers.expat

def predict(latitude, longitude) :
	url = 'http://forecast.weather.gov/MapClick.php?lat=%0.6f&lon=%0.6f&FcstType=digitalDWML' % (latitude, longitude)
	wstream = urllib2.urlopen(url)
	parse(wstream)
	wstream.close()

# TODO use time-layout to parse time zone correctly

def parse(fh) :
	class ParseState(object) :
		pass

	ps = ParseState()

	ps.layouts = {}
	ps.layout_key = None
	ps.element = None
	ps.traces = {}
	ps.trace_key = None

	useful_elements = [
		'temperature',
		'probability-of-precipitation',
		'wind-speed',
		'direction',
		'cloud-amount',
		'humidity',
		'hourly-qpf'
	]

	def start_element(name, attrs):
		print 'DEBUG Start element:', name, attrs
		ps.element = name
		if name in useful_elements :
			ps.trace_key = '%s.%s' % (name, attrs['type'])
			ps.traces.setdefault(ps.trace_key, [])
		if 'xsi:nil' in attrs and name == 'value' :
			ps.traces[ps.trace_key].append(None)
	def end_element(name):
		print 'DEBUG End element:', name
		ps.element = None
	def char_data(data):
		print 'DEBUG Character data:', repr(data)
		if ps.element == 'layout-key' :
			ps.layout_key = data
			ps.layouts[ps.layout_key] = []
		if ps.element == 'start-valid-time' :
			ps.layouts[ps.layout_key].append(data)
		if ps.element == 'value' :
			ps.traces[ps.trace_key].append(data)

	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data

	p.Parse(fh.read())

	pprint.pprint(ps.layouts)
	pprint.pprint(ps.traces)

if __name__ == '__main__' :
	predict(41.837, -87.685)
