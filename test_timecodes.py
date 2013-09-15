# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function, unicode_literals

import sys
from decimal import Decimal

from nose.tools import assert_equal, assert_raises

from timecodes import Timecode


if sys.version_info[0] >= 3:
	long = int
	basestring = str


class TestTimecodes(object):
	def __init__(self):
		self.timecodes = [
			{
				'obj': Timecode('00:00:00:00', 29.97),
				'frame_rate': Decimal('29.97'),
				'_frame_rate_int': 30,
				'timecode': '00:00:00;00',
				'hours': 0,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': 0,
				'total_frames': 0,
				'is_drop_frame': True,
				'dropped_frames': 0,
			},
			{
				'obj': Timecode(0.0, 29.97),
				'frame_rate': Decimal('29.97'),
				'_frame_rate_int': 30,
				'timecode': '00:00:00;00',
				'hours': 0,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': 0,
				'total_frames': 0,
				'is_drop_frame': True,
				'dropped_frames': 0,
			},
			{
				'obj': Timecode(Timecode('01:00:00:00', 29.97), 100),
				'frame_rate': Decimal('100'),
				'_frame_rate_int': 100,
				'timecode': '01:00:00:00',
				'hours': 1,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': Decimal('3600'),
				'total_frames': 360000,
				'is_drop_frame': False,
				'dropped_frames': 0,
			},
			{
				'obj': Timecode(107892, 29.97),
				'frame_rate': Decimal('29.97'),
				'_frame_rate_int': 30,
				'timecode': '01:00:00;00',
				'hours': 1,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': Decimal('3600'),
				'total_frames': 107892,
				'is_drop_frame': True,
				'dropped_frames': 108,
			},
			{
				'obj': Timecode('01:01:00;00', 29.97),
				'frame_rate': Decimal('29.97'),
				'_frame_rate_int': 30,
				'timecode': '01:01:00;02',
				'hours': 1,
				'minutes': 1,
				'seconds': 0,
				'frames': 2,
				'total_seconds': Decimal('3660'),
				'total_frames': 109692,
				'is_drop_frame': True,
				'dropped_frames': 110,
			},
			{
				'obj': Timecode('01:01:00;00', 59.94),
				'frame_rate': Decimal('59.94'),
				'_frame_rate_int': 60,
				'timecode': '01:01:00;04',
				'hours': 1,
				'minutes': 1,
				'seconds': 0,
				'frames': 4,
				'total_seconds': Decimal('3660'),
				'total_frames': 219384,
				'is_drop_frame': True,
				'dropped_frames': 220,
			},
			{
				'obj': Timecode('01:01:00;04', 59.94),
				'frame_rate': Decimal('59.94'),
				'_frame_rate_int': 60,
				'timecode': '01:01:00;04',
				'hours': 1,
				'minutes': 1,
				'seconds': 0,
				'frames': 4,
				'total_seconds': Decimal('3660'),
				'total_frames': 219384,
				'is_drop_frame': True,
				'dropped_frames': 220,
			},
			{
				'obj': Timecode(215784, 59.94),
				'frame_rate': Decimal('59.94'),
				'_frame_rate_int': 60,
				'timecode': '01:00:00;00',
				'hours': 1,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': Decimal('3600'),
				'total_frames': 215784,
				'is_drop_frame': True,
				'dropped_frames': 216,
			},
			{
				'obj': Timecode(long(215784), 59.94),
				'frame_rate': Decimal('59.94'),
				'_frame_rate_int': 60,
				'timecode': '01:00:00;00',
				'hours': 1,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': Decimal('3600'),
				'total_frames': 215784,
				'is_drop_frame': True,
				'dropped_frames': 216,
			},
			{
				'obj': Timecode('24:00:00;00', 60),
				'frame_rate': Decimal('60'),
				'_frame_rate_int': 60,
				'timecode': '00:00:00:00',
				'hours': 24,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': Decimal('86400'),
				'total_frames': 5184000,
				'is_drop_frame': False,
				'dropped_frames': 0,
			},
			{
				'obj': Timecode('00:00:00;00', 60) + 1,
				'frame_rate': Decimal('60'),
				'_frame_rate_int': 60,
				'timecode': '00:00:00:01',
				'hours': 0,
				'minutes': 0,
				'seconds': 0,
				'frames': 1,
				'total_seconds': Decimal('1') / Decimal('60'),
				'total_frames': 1,
				'is_drop_frame': False,
				'dropped_frames': 0,
			},
			{
				'obj': Timecode('00:00:00;00', 60) + 1.0,
				'frame_rate': Decimal('60'),
				'_frame_rate_int': 60,
				'timecode': '00:00:01:00',
				'hours': 0,
				'minutes': 0,
				'seconds': 1,
				'frames': 0,
				'total_seconds': Decimal('1'),
				'total_frames': 60,
				'is_drop_frame': False,
				'dropped_frames': 0,
			},
			{
				'obj': Timecode(0, 29.97) + '01:00:00;00',
				'frame_rate': Decimal('29.97'),
				'_frame_rate_int': 30,
				'timecode': '01:00:00;00',
				'hours': 1,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': Decimal('3600'),
				'total_frames': 107892,
				'is_drop_frame': True,
				'dropped_frames': 108,
			},
			{
				'obj': Timecode('00:00:01;00', 60) + Timecode('01:00:00;00', 60),
				'frame_rate': Decimal('60'),
				'_frame_rate_int': 60,
				'timecode': '01:00:01:00',
				'hours': 1,
				'minutes': 0,
				'seconds': 1,
				'frames': 0,
				'total_seconds': Decimal('3601'),
				'total_frames': 216060,
				'is_drop_frame': False,
				'dropped_frames': 0,
			},
		]
		
		t = Timecode('01:00:00:00', 60)
		t.hours = 1.5
		t.frames = 120
		
		self.timecodes.append(
			{
				'obj': t,
				'frame_rate': Decimal('60'),
				'_frame_rate_int': 60,
				'timecode': '01:30:02:00',
				'hours': 1,
				'minutes': 30,
				'seconds': 2,
				'frames': 0,
				'total_seconds': Decimal('5402'),
				'total_frames': 324120,
				'is_drop_frame': False,
				'dropped_frames': 0,
			}
		)
		
		t = Timecode('01:00:00;00', 60)
		t.hours += 1
		
		self.timecodes.append(
			{
				'obj': t,
				'frame_rate': Decimal('60'),
				'_frame_rate_int': 60,
				'timecode': '02:00:00:00',
				'hours': 2,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': Decimal('7200'),
				'total_frames': 432000,
				'is_drop_frame': False,
				'dropped_frames': 0,
			}
		)
		
		t = Timecode('01:00:00;00', 29.97, is_drop_frame=False)
		t.is_drop_frame = True
		
		self.timecodes.append(
			{
				'obj': t,
				'frame_rate': Decimal('29.97'),
				'_frame_rate_int': 30,
				'timecode': '01:00:03;18',
				'hours': 1,
				'minutes': 0,
				'seconds': 3,
				'frames': 18,
				'total_seconds': Decimal('3603.6'),
				'total_frames': 108000,
				'is_drop_frame': True,
				'dropped_frames': 108,
			}
		)
		
		t = Timecode('02:00:00;00', 29.97)
		t.frame_rate = 59.94
		
		self.timecodes.append(
			{
				'obj': t,
				'frame_rate': Decimal('59.94'),
				'_frame_rate_int': 60,
				'timecode': '01:00:00;00',
				'hours': 1,
				'minutes': 0,
				'seconds': 0,
				'frames': 0,
				'total_seconds': Decimal('3600'),
				'total_frames': 215784,
				'is_drop_frame': True,
				'dropped_frames': 216,
			}
		)
		
		t = Timecode('01:00:00;00', 60)
		t.frame_rate = 59.94
		
		self.timecodes.append(
			{
				'obj': t,
				'frame_rate': Decimal('59.94'),
				'_frame_rate_int': 60,
				'timecode': '01:00:03;36',
				'hours': 1,
				'minutes': 0,
				'seconds': 3,
				'frames': 36,
				'total_seconds': Decimal('3603.6'),
				'total_frames': 216000,
				'is_drop_frame': True,
				'dropped_frames': 216,
			}
		)
	
	def assert_equal(self, index, attr, x, y):
		assert_equal(x, y)
	
	def test_timecodes(self):
		for index, entry in enumerate(self.timecodes):
			for attr in ('frame_rate', 'timecode', 'hours', 'minutes', 'seconds', 'frames', 'total_seconds', 'total_frames', 'is_drop_frame', 'dropped_frames'):
				yield self.assert_equal, index, attr, getattr(entry['obj'], attr), entry[attr]
			
			for attr in ('timecode', 'total_seconds', 'total_frames'):
				if entry['obj'].total_seconds < 86400:
					yield self.assert_equal, index, attr, entry['obj'], entry[attr]
	
	def test_attr_exceptions(self):
		t = Timecode(0, 30)
		
		exceptions = [
			{
				'exception': RuntimeError,
				'attr': 'is_drop_frame',
				'value': True,
			},
			{
				'exception': TypeError,
				'attr': 'timecode',
				'value': None,
			},
			{
				'exception': ValueError,
				'attr': 'timecode',
				'value': '',
			},
			{
				'exception': TypeError,
				'attr': 'frame_rate',
				'value': None,
			},
			{
				'exception': ValueError,
				'attr': 'is_drop_frame',
				'value': 'Whoops.',
			},
		]
		
		for entry in exceptions:
			assert_raises(entry['exception'], setattr, t, entry['attr'], entry['value'])
