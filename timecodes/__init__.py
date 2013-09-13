# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function, unicode_literals

import operator
import re
import sys
from decimal import Decimal
from math import floor


VERSION = (0, 0, 1)

__title__ = 'Timecodes'
__version__ = '.'.join((str(i) for i in VERSION)) # str for compatibility with setup.py under Python 3.
__author__ = 'Karan Lyons'
__contact__ = 'karan@karanlyons.com'
__homepage__ = 'https://github.com/karanlyons/timecodes'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 Karan Lyons'


if sys.version_info[0] >= 3:
	long = Decimal
	basestring = str


class Timecode(object):
	"""
	The Timecode object represents SMPTE timecodes of any possible frame rate,
	and allows for intuitive handling and conversion.
	
	Drop frame timecodes are supported for both 29.97 and 59.94 frame rates. If
	is_drop_frame is None, these timecodes are to be drop frame.
	
	An optional starting timecode may be declared.
	
	When passed values for arithmetic functions or initialization, ints/longs
	are assumed to be frame counts, floats/Decimals are assumed to be seconds,
	and basestrings are attempted to be parsed into timecodes.
	
	"""
	
	def __init__(self, timecode, frame_rate=None, is_drop_frame=None, starting_timecode=None):
		if type(timecode) != Timecode:
			frame_rate = float(frame_rate)
			is_drop_frame = is_drop_frame if is_drop_frame in (True, False, None) else None
			starting_timecode = Timecode(starting_timecode, frame_rate=frame_rate, is_drop_frame=is_drop_frame) if starting_timecode else None
			
			self.__dict__.update({
				'is_drop_frame': is_drop_frame,
				'starting_timecode': starting_timecode,
				'hours': None,
				'minutes': None,
				'seconds': None,
				'frames': None,
				'total_seconds': None,
				'total_frames': None,
			})
			
			self.frame_rate = frame_rate
			self.timecode = timecode
		
		else:
			self.__dict__.update(timecode.__dict__)
	
	def __setattr__(self, name, value):
		self.__validate_inputs(name, value)
		
		if name == 'timecode' and not isinstance(value, basestring):
			if type(value) in (float, Decimal):
				name = 'total_seconds'
			
			elif type(value) in (int, long):
				name = 'total_frames'
		
		super(Timecode, self).__setattr__(name, value)
		
		if name == 'is_drop_frame':
			if self.is_drop_frame is None:
				self.is_drop_frame = True if self.frame_rate in (29.97, 59.94) else False
		
		elif name == 'frame_rate':
			self.__dict__['frame_rate'] = 23.976 if value == 23.98 else value
			self._frame_rate_int = int(round(self.frame_rate))
			self.is_drop_frame = None
		
		if name in ('frame_rate', 'is_drop_frame') and self.starting_timecode:
			self.__dict__['starting_timecode'] = Timecode(self.starting_timecode.total_frames, frame_rate=self.frame_rate, is_drop_frame=self.is_drop_frame)
		
		elif name == 'starting_timecode':
			self.__dict__['starting_timecode'] = Timecode(self.starting_timecode, frame_rate=self.frame_rate, is_drop_frame=self.is_drop_frame)
			self.__dict__.update(self.__components_to_total_seconds())
			self.__dict__.update(self.__components_to_total_frames())
		
		elif name == 'timecode':
			self.__dict__.update(self.__timecode_to_components())
			self.__dict__.update(self.__fix_components())
			self.__dict__.update(self.__components_to_total_seconds())
			self.__dict__.update(self.__components_to_total_frames())
			self.__dict__.update(self.__components_to_timecode())
		
		elif name in ('hours', 'minutes', 'seconds', 'frames') and None not in (self.hours, self.minutes, self.seconds, self.frames):
			self.__dict__.update(self.__fix_components())
			self.__dict__.update(self.__components_to_total_seconds())
			self.__dict__.update(self.__components_to_total_frames())
			self.__dict__.update(self.__components_to_timecode())
		
		elif name == 'total_seconds' and self.total_seconds is not None:
			self.__dict__.update(self.__total_seconds_to_total_frames())
			self.__dict__.update(self.__total_frames_to_components())
			self.__dict__.update(self.__fix_components())
			self.__dict__.update(self.__components_to_timecode())
		
		if name in ('is_drop_frame', 'frame_rate', 'total_frames') and None not in (self.is_drop_frame, self.frame_rate, self.total_frames):
			self.__dict__.update(self.__total_frames_to_components())
			self.__dict__.update(self.__fix_components())
			self.__dict__.update(self.__components_to_total_seconds())
			self.__dict__.update(self.__components_to_timecode())
	
	def __validate_inputs(self, name, value):
		if name in ('timecode', 'starting_timecode'):
			if all([not isinstance(value, valid_type) for valid_type in (Timecode, float, int, long, basestring)]):
				raise TypeError("Bad {name}: expected instance of Timecode, float, int, long, basestring, got {type}.".format(name=name, type=type(value)))
			
			elif isinstance(value, basestring) and not re.match(r'^.*?([0-9]{2,})[:;]?([0-5][0-9])[:;]?([0-5][0-9])[:;]?([0-9]{1,}).*?$', value):
				raise ValueError("Bad {name}: expected something in the form of NN:NN:NN:NN, got {value}".format(name=name, value=value))
		
		elif name in ('frame_rate', 'total_seconds') and all([not isinstance(value, valid_type) for valid_type in (float, int, long, Decimal)]):
			raise TypeError("Bad {name}: expected instance of float, int, long, Decimal, got {type}.".format(name=name, type=type(value)))
		
		elif name in ('hours', 'minutes', 'seconds', 'frames', 'total_frames') and int(value) != value:
			raise ValueError("Bad {name}: expected integer, got {value}".format(name=name, value=value))
		
		elif name == 'is_drop_frame' and value not in (True, False, None):
			raise ValueError("Bad {name}: expected True, False, None, got {value}".format(name=name, value=value))
	
	def __timecode_to_components(self):
		"""
		Attempts to extract timecode components out of a given string.
		
		"""
		
		match = re.match(r'^.*?([0-9]{2,})[:;]?([0-5][0-9])[:;]?([0-5][0-9])[:;]?([0-9]{1,}).*?$', self.timecode)
		
		if not match:
			raise ValueError('Bad timecode: expected something in the form of NN:NN:NN:NN, got {timecode}'.format(timecode=self.timecode))
		
		hours, minutes, seconds, frames = (int(n) for n in match.groups())
		
		seconds += frames / self._frame_rate_int
		minutes += seconds / 60
		hours += minutes / 60
		
		frames %= self._frame_rate_int
		seconds %= 60
		minutes %= 60
		
		if self.is_drop_frame and (minutes % 10):
			if self.frame_rate == 29.97 and frames < 2:
				frames += 2
			
			elif self.frame_rate == 59.94 and frames < 4:
				frames += 4
		
		return {'hours': hours, 'minutes': minutes, 'seconds': seconds, 'frames': frames}
	
	def __fix_components(self):
		"""
		Handles overflow and coercion of timecode components.
		
		"""
		
		frames = int(floor(self.frames))
		seconds = int(floor(self.seconds))
		minutes = int(floor(self.minutes))
		hours = int(floor(self.hours))
		
		seconds += frames // self._frame_rate_int
		minutes += seconds // 60
		hours += minutes // 60
		
		frames %= self._frame_rate_int
		seconds %= 60
		minutes %= 60
		hours %= 60
		
		return {'hours': hours, 'minutes': minutes, 'seconds': seconds, 'frames': frames}
	
	def __components_to_total_seconds(self):
		drop_fix = 0
		
		if self.is_drop_frame:
			drop_fix = 2 * (self.minutes % 10)
			
			if self.frame_rate == 59.94:
				drop_fix *= 2
		
		total_seconds = (self.hours * 3600) + (self.minutes * 60) + self.seconds + (Decimal(self.frames - drop_fix) / self._frame_rate_int)
		
		if self.starting_timecode:
			total_seconds -= self.starting_timecode.total_seconds
		
		return {'total_seconds': Decimal(total_seconds)}
	
	def __components_to_total_frames(self):
		total_frames = int(((self.hours * 3600) + (self.minutes * 60) + self.seconds) * self._frame_rate_int) + self.frames - self.dropped_frames
		
		if self.starting_timecode:
			total_frames -= self.starting_timecode.total_frames
		
		return {'total_frames': int(total_frames)}
	
	def __total_seconds_to_total_frames(self):
		total_frames = int(self.total_seconds * self._frame_rate_int) - self.__dropped_frames(using='total_seconds')
		
		return {'total_frames': int(total_frames)}
	
	def __total_frames_to_components(self):
		frames = self.total_frames + self.__dropped_frames(using='total_frames')
		
		if self.starting_timecode:
			frames += self.starting_timecode.total_frames
		
		hours = frames / (3600 * self._frame_rate_int)
		minutes = (frames % (3600 * self._frame_rate_int)) / (60 * self._frame_rate_int)
		seconds = ((frames % (3600 * self._frame_rate_int)) % (60 * self._frame_rate_int)) / self._frame_rate_int
		frames = ((frames % (3600 * self._frame_rate_int)) % (60 * self._frame_rate_int)) % self._frame_rate_int
		
		return {'hours': int(hours), 'minutes': int(minutes), 'seconds': int(seconds), 'frames': int(frames)}
	
	def __dropped_frames(self, using='components'):
		"""
		Calculates dropped frames for a timecode, using either components,
		total seconds, or total frames.
		
		"""
		
		if self.is_drop_frame:
			if self.frame_rate in (29.97, 59.94):
				if using == 'components':
					hours = self.hours
					minutes = self.minutes
				
				elif using == 'total_seconds':
					hours = int(self.total_seconds / 3600)
					minutes = int((self.total_seconds % 3600) / 60)
				
				elif using == 'total_frames':
					hours = int(self.total_frames / (3600 * self._frame_rate_int))
					minutes = int(self.total_frames % (3600 * self._frame_rate_int) / (60 * self._frame_rate_int))
				
				dropped = (hours * 108) + ((minutes / 10) * 18) + (minutes % 10 * 2) # "Drop" 2 frames every minute except every tenth.
				
				if self.frame_rate == 59.94: # Double for 59.94
					dropped *= 2
				
				return dropped
			
			else:
				raise Exception
		
		else:
			return 0
	
	def __components_to_timecode(self):
		return {'timecode': '%02d:%02d:%02d%s%02d' % (self.hours % 24, self.minutes, self.seconds, ';' if self.is_drop_frame else ':', self.frames)}
	
	@property
	def dropped_frames(self):
		return self.__dropped_frames()
	
	def convert_to(self, frame_rate=None, is_drop_frame=None, starting_timecode=None, preserving=None):
		"""
		Converts a timecode to another frame rate or starting timecode,
		preserving either seconds, frames, or the displayed timecode.
		
		"""
		
		if preserving not in ('seconds', 'frames', 'timecode'):
			preserving = 'seconds'
		
		if frame_rate is None:
			frame_rate = self.frame_rate
		
		if is_drop_frame is None:
			is_drop_frame = self.is_drop_frame
		
		if starting_timecode is None:
			starting_timecode = self.starting_timecode
		
		else:
			starting_timecode = Timecode(starting_timecode, frame_rate, is_drop_frame)
		
		if preserving == 'seconds':
			self.__init__(self.total_seconds, frame_rate, is_drop_frame, starting_timecode.convert_to(frame_rate, is_drop_frame, None, preserving) if starting_timecode else None)
		
		elif preserving == 'frames':
			self.__init__(self.total_frames, frame_rate, is_drop_frame, starting_timecode.convert_to(frame_rate, is_drop_frame, None, preserving) if starting_timecode else None)
		
		elif preserving == 'timecode':
			self.__init__(self.timecode, frame_rate, is_drop_frame, starting_timecode.convert_to(frame_rate, is_drop_frame, None, preserving) if starting_timecode else None)
		
		return self
	
	def __str__(self):
		return self.timecode
	
	def __repr__(self):
		return "Timecode(timecode='%s', frame_rate=%.2f, is_drop_frame=%s, starting_timecode=%s)" % (self.timecode, self.frame_rate, self.is_drop_frame, "'%s'" % self.starting_timecode.timecode if self.starting_timecode else 'None')
	
	def __op(self, op, other):
		if type(other) == Timecode:
			return Timecode(op(self.total_seconds, other.total_seconds), self.frame_rate, self.is_drop_frame, self.starting_timecode)
		
		elif type(other) in (float, Decimal):
			return Timecode(op(self.total_seconds, Decimal(other)), self.frame_rate, self.is_drop_frame, self.starting_timecode)
		
		elif type(other) in (int, long):
			return Timecode(op(self.total_frames, other), self.frame_rate, self.is_drop_frame, self.starting_timecode)
		
		elif isinstance(other, basestring):
			return Timecode(op(self.total_seconds, Timecode(other, self.frame_rate, self.is_drop_frame, self.starting_timecode).total_frames), self.frame_rate, self.is_drop_frame, self.starting_timecode)
		
		else:
			raise TypeError("unsupported operand type(s) for {op}: 'Timecode' and '{type}'".format(op=str(op)[19:-1], type=type(other)))
	
	def __add__(self, other):
		return self.__op(operator.add, other)
	
	def __sub__(self, other):
		return self.__op(operator.sub, other)
	
	def __mul__(self, other):
		return self.__op(operator.mul, other)
	
	def __div__(self, other):
		return self.__op(operator.div, other)
	
	def __rop(self, op, other):
		if type(other) == Timecode:
			return self.__op(op, other)
		
		elif type(other) in (float, Decimal):
			return self.__op(op, other).total_seconds
		
		elif type(other) in (int, long):
			return self.__op(op, other).total_frames
		
		elif isinstance(other, basestring):
			return self.__op(op, other).timecode
		
		else:
			raise TypeError("unsupported operand type(s) for {opp}: '{type}' and 'Timecode'".format(op=str(op)[19:-1], type=type(other)))
	
	def __radd__(self, other):
		return self.__rop(operator.add, other)
	
	def __rsub__(self, other):
		return self.__rop(operator.sub, other)
	
	def __rmul__(self, other):
		return self.__rop(operator.mul, other)
	
	def __rdiv__(self, other):
		return self.__rop(operator.div, other)
	
	def __eq__(self, other):
		if type(other) == Timecode:
			return self.total_seconds == other.total_seconds
		
		elif type(other) in (float, Decimal):
			return self.total_seconds == other
		
		elif type(other) in (int, long):
			return self.total_frames == other
		
		elif isinstance(other, basestring):
			return self.total_frames == Timecode(other, self.frame_rate, self.is_drop_frame, self.starting_timecode, self.starting_timecode).total_frames
		
		else:
			return False
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __gt__(self, other):
		if type(other) == Timecode:
			return self.total_seconds > other.total_seconds
		
		elif type(other) in (float, Decimal):
			return self.total_seconds > other
		
		elif type(other) in (int, long):
			return self.total_frames > other
		
		elif isinstance(other, basestring):
			return self.total_frames > Timecode(other, self.frame_rate, self.is_drop_frame, self.starting_timecode, self.starting_timecode).total_frames
		
		else:
			return False
	
	def __lt__(self, other):
		return not self.__gt__(other)
	
	def __ge__(self, other):
		return self.__gt__(other) or self.__eq__(other)
	
	def __le__(self, other):
		return self.__lt__(other) or self.__eq__(other)
