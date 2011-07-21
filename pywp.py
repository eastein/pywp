#!/usr/bin/env python

import sys
import pprint
import urllib2
import xml.parsers.expat

def predict(latitude, longitude) :
	url = 'http://forecast.weather.gov/MapClick.php?lat=%0.6f&lon=%0.6f&FcstType=digitalDWML' % (latitude, longitude)
	wstream = urllib2.urlopen(url)
	try :
		return parse(wstream)
	finally :
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
	ps.converter = None

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
			ps.trace_key = '%s.%s' % (name, attrs['type'])
			if (attrs['type'] == 'floating') :
				ps.converter = float
			else :
				ps.converter = int
			ps.traces.setdefault(ps.trace_key, [])
		if 'xsi:nil' in attrs and name == 'value' :
			ps.traces[ps.trace_key].append(None)
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
				pass # TODO handle this better?
			ps.traces[ps.trace_key].append(value)

	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data

	p.Parse(fh.read())

	return {'layouts' : ps.layouts, 'traces' : ps.traces}

if __name__ == '__main__' :
	pprint.pprint(predict(float(sys.argv[1]), float(sys.argv[2])))
