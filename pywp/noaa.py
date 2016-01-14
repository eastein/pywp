from __future__ import absolute_import

import sys

try:
    import urllib2 as request_module
except ImportError:
    import urllib.request as request_module

import xml.parsers.expat

import pytz
import dateutil.parser
import datetime


class NoSuchDataException(Exception):
    """
    Used when the data requested does not exist in the prediction.
    """


class TimeOutOfRangeException(Exception):
    """
    Used when the data requested exists in the prediction, but not for the time specified.
    """


class TimeLayout(object):

    def __init__(self, key, layout_buckets):
        self.key = key
        self.layout_buckets = layout_buckets
        self.n_layouts = len(self.layout_buckets)

    def get_index(self, date_time):
        i = -1
        for start_time, end_time in self.layout_buckets:
            i += 1
            if date_time < start_time:
                continue
            elif date_time > end_time:
                continue
            else:
                return i
        raise TimeOutOfRangeException


class Trace(object):

    def __init__(self, layout, data):
        self.layout = layout
        self.data = data

    def get_data(self, date_time):
        return self.data[self.layout.get_index(date_time)]


class Predictor(object):

    @classmethod
    def now(cls):
        return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    class Prediction(object):

        def __init__(self, predictor, layouts, traces):
            self.predictor = predictor

            self._raw_layouts = layouts
            self.layouts = dict([
                (k, TimeLayout(k, v))
                for (k, v)
                in list(self._raw_layouts.items())
            ])

            self._raw_traces = traces
            self.traces = dict([
                (k, Trace(self.get_layout(trace['time_layout']), trace['data']))
                for
                (k, trace)
                in list(self._raw_traces.items())
            ])

        def get_layout(self, key):
            return self.layouts[key]

        def data_available(self):
            return list(self.traces.keys())

        def get_data(self, name, data_type, date_time):
            if (name, data_type) not in self.traces:
                raise NoSuchDataException
            else:
                return self.traces[(name, data_type)].get_data(date_time)

    URL_PATTERN = 'http://forecast.weather.gov/MapClick.php?lat=%0.6f&lon=%0.6f&FcstType=digitalDWML&product=time-series'

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def predict(self, dictionary_response=False):
        url = self.URL_PATTERN % (self.latitude, self.longitude)
        wstream = request_module.urlopen(url)
        try:
            return self.parse(wstream, dictionary_response=dictionary_response)
        finally:
            wstream.close()

    def parse(self, fh, dictionary_response=False):
        class ParseState(object):

            def __init__(self):
                self.layouts = {}
                self.layout_key = None
                self.element = None
                self.traces = {}
                self.current_trace = None
                self.converter = None

            def initiate_trace(self, name, data_type, time_layout):
                self.current_trace = {
                    'time_layout': time_layout,
                    'data': []
                }
                self.traces[(name, data_type)] = self.current_trace

            def add_data(self, value):
                self.current_trace['data'].append(value)

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

        def debug(s):
            pass  # print 'DEBUG %s' % s

        def start_element(name, attrs):
            debug('Start element: %s %s' % (name, attrs))
            ps.element = name
            if name in useful_elements:
                ps.initiate_trace(name, attrs['type'], attrs['time-layout'])
                if (attrs['type'] == 'floating'):
                    ps.converter = float
                else:
                    ps.converter = int
            if 'xsi:nil' in attrs and name == 'value':
                ps.add_data(None)

        def end_element(name):
            debug('End element: %s' % name)
            ps.element = None

        def char_data(data):
            debug('Character data: %s' % repr(data))
            if ps.element == 'layout-key':
                ps.layout_key = data
                ps.layouts[ps.layout_key] = []
            if ps.element == 'start-valid-time':
                ps.start_valid_time = dateutil.parser.parse(data)
            if ps.element == 'end-valid-time':
                ps.layouts[ps.layout_key].append((ps.start_valid_time, dateutil.parser.parse(data)))
                ps.start_valid_time = None
            if ps.element == 'value':
                value = data
                try:
                    value = ps.converter(data)
                except ValueError:
                    value = None
                ps.add_data(value)

        p = xml.parsers.expat.ParserCreate()
        p.SetParamEntityParsing(xml.parsers.expat.XML_PARAM_ENTITY_PARSING_NEVER)
        p.StartElementHandler = start_element
        p.EndElementHandler = end_element
        p.CharacterDataHandler = char_data

        p.Parse(fh.read())

        if dictionary_response:
            return {
                'layouts': ps.layouts,
                'traces': ps.traces
            }
        else:
            return self.__class__.Prediction(self, ps.layouts, ps.traces)

if __name__ == '__main__':
    import pprint
    pprint.pprint(predict(float(sys.argv[1]), float(sys.argv[2])))