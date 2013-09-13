# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function, unicode_literals

import unittest

from timecodes import Timecode


class TimecodesTestCase(unittest.TestCase):
	def setUp(self):
		self.timecodes = (
			Timecode('00:00:00;01', 29.97), # 0.0333333333333, 1
			Timecode('00:00:01;00', 29.97), # 1.0, 30
			Timecode('00:01:00;02', 29.97), # 120.0, 3598
			Timecode('00:02:00;04', 29.97), # 120.0, 3598
			Timecode('00:10:00;00', 29.97), # 600.0, 17982
			Timecode('01:00:00;00', 29.97), # 3600.0, 107892
			Timecode(61.0, 29.97), # 120.0, 3598
			Timecode('00:02:00;01', 29.97),
			Timecode('00:59:59;31', 29.97),
			Timecode('01:00:00;00', 29.97), # 3600.0, 107892
			Timecode('02:00:00:00', 29.97, starting_timecode=107892),
			Timecode('24:00:00:00', 29.97),
		)
	
	def test(self):
		for timecode in self.timecodes:
			print("%s:\n\tTotal Seconds:\t%s\n\tTotal Frames:\t%s\n\tDropped Frames:\t%s\n" % (timecode.timecode, timecode.total_seconds, timecode.total_frames, timecode.dropped_frames))
