#!/usr/bin/env python

import sys
import pprint
import urllib2
import xml.parsers.expat

def predict(latitude, longitude) :
	url = 'http://forecast.weather.gov/MapClick.php?lat=%0.6f&lon=%0.6f&FcstType=digitalDWML&product=time-series' % (latitude, longitude)
	wstream = urllib2.urlopen(url)
	try :
		return parse(wstream)
	finally :
		wstream.close()

# TODO use time-layout to parse time zone correctly

def parse(fh) :
	class ParseState(object) :
		def __init__(self) :
			self.layouts = {}
			self.layout_key = None
			self.element = None
			self.traces = {}
			self.trace_key = None
			self.converter = None

		def add_data(self, value) :
			a, b = self.trace_key
			self.traces.setdefault(a, dict())
			self.traces[a].setdefault(b, list())
			self.traces[a][b].append(value)

	ps = ParseState()

	useful_elements = [
		'temperature',
		'probability-of-precipitation',
		'wind-speed',
		'direction',
		'cloud-amount',
		'humidity',
		'hourly-qpf'
	]

	def debug(s) :
		pass#print 'DEBUG %s' % s

	def start_element(name, attrs):
		debug('Start element: %s %s' % (name, attrs))
		ps.element = name
		if name in useful_elements :
			ps.trace_key = (name, attrs['type'])
			if (attrs['type'] == 'floating') :
				ps.converter = float
			else :
				ps.converter = int
		if 'xsi:nil' in attrs and name == 'value' :
			ps.add_data(None)
	def end_element(name):
		debug('End element: %s' % name)
		ps.element = None
	def char_data(data):
		debug('Character data: %s' % repr(data))
		if ps.element == 'layout-key' :
			ps.layout_key = data
			ps.layouts[ps.layout_key] = []
		if ps.element == 'start-valid-time' :
			ps.layouts[ps.layout_key].append(data)
		if ps.element == 'value' :
			value = data
			try :
				value = ps.converter(data)
			except ValueError :
				value = None
			ps.add_data(value)

	p = xml.parsers.expat.ParserCreate()
	p.SetParamEntityParsing(xml.parsers.expat.XML_PARAM_ENTITY_PARSING_NEVER)
	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data

	p.Parse(fh.read())

	return {'layouts' : ps.layouts, 'traces' : ps.traces}

if __name__ == '__main__' :
	pprint.pprint(predict(float(sys.argv[1]), float(sys.argv[2])))
