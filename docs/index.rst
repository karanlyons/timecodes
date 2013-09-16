#########
Timecodes
#########

.. image:: https://badge.fury.io/py/timecodes.png
	:target: http://badge.fury.io/py/timecodes
.. image:: https://travis-ci.org/karanlyons/timecodes.png?branch=master
	:target: https://travis-ci.org/karanlyons/timecodes/
.. image:: https://coveralls.io/repos/karanlyons/timecodes/badge.png?branch=master
	:target: https://coveralls.io/r/karanlyons/timecodes

Working with timecodes can suck. It shouldn't have to:

.. code-block:: pycon

	>>> from timecodes import Timecode
	>>> t = Timecode('01:00:00;00', 29.97)
	>>> t.total_frames, t.dropped_frames
	(107892, 108)
	>>> t.hours += 1
	>>> t.timecode, t.total_frames
	(u'02:00:00;00', 215784)
	>>> t.convert_to(frame_rate=23.98, preserving='timecode')
	>>> t.timecode, t.total_frames
	(u'02:00:00:00', 172800)


Installation
============

Install Timecodes just like everything else:

.. code-block:: bash

	$ pip install timecodes


Developer Interface
===================

.. autoclass:: timecodes.Timecode
	:members:
	:undoc-members:


.. include:: ../HISTORY.rst
