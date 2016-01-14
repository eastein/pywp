<A name="toc1-0" title="What?" />
# What?

Python library for fetching data from NWS/NOAA (DWML) and making the XML file easily understood for your Python application.

<A name="toc1-5" title="Why?" />
# Why?

Because it seemed like a good idea at the time.

<A name="toc1-10" title="How?" />
# How?

	import pywp.noaa
	ord = pywp.noaa.Predictor(42.077338286382755, -87.70927656796923)
	pred = ord.predict()
	pred.get_data('temperature', 'hourly', pywp.noaa.Predictor.now())
