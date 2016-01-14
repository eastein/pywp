# What?

Python library for fetching data from NWS/NOAA (DWML) and making the XML file easily understood for your Python application.

# Why?

Because it seemed like a good idea at the time.

# How?

	import pywp.noaa
	ord = pywp.noaa.Predictor(42.077338286382755, -87.70927656796923)
	pred = ord.predict()
	pred.get_data('temperature', 'hourly', pywp.noaa.Predictor.now())
