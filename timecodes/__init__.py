# -*- coding: utf-8 -*-

from __future__ import division, absolute_import, print_function, unicode_literals

import operator
import re
import sys
from decimal import Decimal
from math import floor


VERSION = (0, 0, 1)

__title__ = 'Timecodes'
__version__ = '.'.join((str(i) for i in VERSION)) # str for compatibility with setup.py in py3.
__author__ = 'Karan Lyons'
__contact__ = 'karan@karanlyons.com'
__homepage__ = 'https://github.com/karanlyons/timecodes'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 Karan Lyons'


if sys.version_info[0] >= 3: # pragma: no cover (version compatibility, unreachable in py2).
	long = int
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
	
	def __init__(self, timecode, frame_rate, is_drop_frame=None):
		self.__dict__.update({
			'timecode': None,
			'frame_rate': None,
			'_frame_rate_int': None,
			'is_drop_frame': None,
			'hours': None,
			'minutes': None,
			'seconds': None,
			'frames': None,
			'total_seconds': None,
			'total_frames': None,
		})
		
		self.frame_rate = frame_rate
		self.is_drop_frame = is_drop_frame
		
		if any([isinstance(timecode, seconds_type) for seconds_type in (float, Decimal)]):
			self.total_seconds = timecode
		
		elif any([isinstance(timecode, frames_type) for frames_type in (int, long)]):
			self.total_frames = timecode
		
		else:
			self.timecode = timecode
		
	def __setattr__(self, name, value):
		value = self._clean_input(name, value)
		
		if name == 'is_drop_frame' and value is None:
			value = True if self.frame_rate in (Decimal('29.97'), Decimal('59.94')) else False
		
		elif name == 'frame_rate':
			value = Decimal('23.976') if value == Decimal('23.976') else value
			self._frame_rate_int = int(round(value))
			
			if value not in (Decimal('29.97'), Decimal('59.94')):
				new_is_drop_frame = False
			
			elif value in (Decimal('29.97'), Decimal('59.94')) and self.frame_rate not in (Decimal('29.97'), Decimal('59.94')):
				new_is_drop_frame = None
			
			else:
				new_is_drop_frame = self.is_drop_frame
		
		if name in ('is_drop_frame', 'frame_rate') and None not in (self.frame_rate, self.is_drop_frame, self.total_frames, self.total_seconds):
			self.convert_to(**{name: value, 'preserving': 'frames'})
		
		else:
			super(Timecode, self).__setattr__(name, value)
		
		if name == 'frame_rate':
			self.is_drop_frame = new_is_drop_frame
		
		if name in ('timecode', 'total_seconds', 'total_frames', 'hours', 'minutes', 'seconds', 'frames'):
			if name == 'timecode':
				self.__dict__.update(self._timecode_to_components())
			
			elif name == 'total_seconds' and self.total_seconds is not None:
				self.__dict__.update(self._total_seconds_to_total_frames())
				self.__dict__.update(self._total_frames_to_components())
			
			elif name == 'total_frames' and self.total_frames is not None:
				self.__dict__.update(self._total_frames_to_components())
			
			if name in ('timecode', 'total_seconds', 'total_frames') or None not in (self.hours, self.minutes, self.seconds, self.frames):
				self.__dict__.update(self._fix_components())
				self.__dict__.update(self._components_to_total_seconds())
				self.__dict__.update(self._components_to_total_frames())
				self.__dict__.update(self._components_to_timecode())
	
	def _clean_input(self, name, value):
		if name == 'timecode':
			if all([not isinstance(value, valid_type) for valid_type in (Timecode, basestring)]):
				raise TypeError("Bad {name}: expected instance of Timecode, basestring, got {type}.".format(name=name, type=type(value)))
			
			elif isinstance(value, basestring) and not re.match(r'^.*?([0-9]{2,})[:;]?([0-5][0-9])[:;]?([0-5][0-9])[:;]?([0-9]{1,}).*?$', value):
				raise ValueError("Bad {name}: expected something in the form of NN:NN:NN:NN, got {value}".format(name=name, value=value))
		
		elif name in ('frame_rate', 'total_seconds') and all([not isinstance(value, valid_type) for valid_type in (Timecode, float, int, long, Decimal)]):
			raise TypeError("Bad {name}: expected instance of Timecode, float, int, long, Decimal, got {type}.".format(name=name, type=type(value)))
		
		elif name in ('total_frames', '_frame_rate_int') and all([not isinstance(value, valid_type) for valid_type in (Timecode, int, long)]):
			raise TypeError("Bad {name}: expected instance of Timecode, int, long got {type}.".format(name=name, type=type(value)))
		
		elif name == 'is_drop_frame' and value not in (Timecode, True, False, None):
			raise ValueError("Bad {name}: expected instance of Timecode, True, False, None, got {value}".format(name=name, value=value))
		
		if isinstance(value, Timecode):
			value = getattr(value, name)
		
		elif isinstance(value, float):
			value = Decimal(str(value))
		
		return value
	
	def _timecode_to_components(self):
		"""
		Attempts to extract timecode components out of a given string.
		
		"""
		
		hours, minutes, seconds, frames = (int(n) for n in re.match(r'^.*?([0-9]{2,})[:;]?([0-5][0-9])[:;]?([0-5][0-9])[:;]?([0-9]{1,}).*?$', self.timecode).groups())
		
		seconds += frames // self._frame_rate_int
		minutes += seconds // 60
		hours += minutes // 60
		
		frames %= self._frame_rate_int
		seconds %= 60
		minutes %= 60
		
		if self.is_drop_frame and (minutes % 10):
			if self.frame_rate == Decimal('29.97') and frames < 2:
				frames += 2
			
			elif self.frame_rate == Decimal('59.94') and frames < 4:
				frames += 4
		
		return {'hours': hours, 'minutes': minutes, 'seconds': seconds, 'frames': frames}
	
	def _fix_components(self):
		"""
		Handles overflow and coercion of timecode components.
		
		"""
		
		hours = self.hours
		minutes = self.minutes + (60 * (hours % 1))
		seconds = self.seconds + (60 * (minutes % 1))
		frames = self.frames + (self._frame_rate_int * (seconds % 1))
		
		hours = int(floor(hours))
		minutes = int(floor(minutes))
		seconds = int(floor(seconds))
		frames = int(floor(frames))
		
		seconds += frames // self._frame_rate_int
		minutes += seconds // 60
		hours += minutes // 60
		
		frames %= self._frame_rate_int
		seconds %= 60
		minutes %= 60
		hours %= 60
		
		return {'hours': hours, 'minutes': minutes, 'seconds': seconds, 'frames': frames}
	
	def _components_to_total_seconds(self):
		drop_fix = 0
		
		if self.is_drop_frame:
			drop_fix = 2 * (self.minutes % 10)
			
			if self.frame_rate == Decimal('59.94'):
				drop_fix *= 2
		
		total_seconds = (self.hours * 3600) + (self.minutes * 60) + self.seconds + (Decimal(self.frames - drop_fix) / self._frame_rate_int)
		
		return {'total_seconds': Decimal(total_seconds)}
	
	def _components_to_total_frames(self):
		total_frames = int(((self.hours * 3600) + (self.minutes * 60) + self.seconds) * self._frame_rate_int) + self.frames - self.dropped_frames
		
		return {'total_frames': int(total_frames)}
	
	def _total_seconds_to_total_frames(self):
		total_frames = int(self.total_seconds * self._frame_rate_int) - self._dropped_frames(using='total_seconds')
		
		return {'total_frames': int(total_frames)}
	
	def _total_frames_to_components(self):
		frames = self.total_frames + self._dropped_frames(using='total_frames')
		
		hours = frames // (3600 * self._frame_rate_int)
		minutes = (frames % (3600 * self._frame_rate_int)) // (60 * self._frame_rate_int)
		seconds = ((frames % (3600 * self._frame_rate_int)) % (60 * self._frame_rate_int)) // self._frame_rate_int
		frames = ((frames % (3600 * self._frame_rate_int)) % (60 * self._frame_rate_int)) % self._frame_rate_int
		
		return {'hours': int(hours), 'minutes': int(minutes), 'seconds': int(seconds), 'frames': int(frames)}
	
	def _dropped_frames(self, using='components'):
		"""
		Calculates dropped frames for a timecode, using either components,
		total seconds, or total frames.
		
		"""
		
		if self.is_drop_frame:
			if self.frame_rate in (Decimal('29.97'), Decimal('59.94')):
				if using == 'components':
					hours = self.hours
					minutes = self.minutes
					
				elif using == 'total_seconds':
					hours = int(self.total_seconds // 3600)
					minutes = int((self.total_seconds % 3600) // 60)
					
				elif using == 'total_frames':
					hours = int(self.total_frames // (3600 * self._frame_rate_int))
					minutes = int(self.total_frames % (3600 * self._frame_rate_int) // (60 * self._frame_rate_int))
				
				else:
					raise ValueError('bad using: expected components, total_seconds, total_frames, got {value}'.format(value=using))
				
				dropped = (hours * 108) + ((minutes // 10) * 18) + (minutes % 10 * 2) # "Drop" 2 frames every minute except every tenth.
				
				if self.frame_rate == Decimal('59.94'): # Double for 59.94
					dropped *= 2
				
				return int(dropped)
			
			else:
				raise RuntimeError('is_drop_frame is True, but frame_rate is not in (29.97, 59.94). This should never happen.')
		
		else:
			return 0
	
	def _components_to_timecode(self):
		return {'timecode': '%02d:%02d:%02d%s%02d' % (self.hours % 24, self.minutes, self.seconds, ';' if self.is_drop_frame else ':', self.frames)}
	
	@property
	def dropped_frames(self):
		return self._dropped_frames()
	
	def convert_to(self, frame_rate=None, is_drop_frame=None, preserving=None):
		"""
		Converts a timecode to another frame rate or starting timecode,
		preserving either seconds, frames, or the displayed timecode.
		
		"""
		
		if preserving not in ('seconds', 'frames', 'timecode'):
			raise ValueError('bad preserving: expected seconds, frames, timecode, got {preserving}'.format(preserving=preserving))
		
		if is_drop_frame is None:
			is_drop_frame = self.is_drop_frame
		
		if frame_rate is None:
			frame_rate = self.frame_rate
		
		if preserving == 'seconds':
			self.__init__(self.total_seconds, frame_rate, is_drop_frame)
		
		elif preserving == 'frames':
			self.__init__(self.total_frames, frame_rate, is_drop_frame)
		
		elif preserving == 'timecode':
			self.__init__(self.timecode, frame_rate, is_drop_frame)
	
	def __str__(self):
		return self.timecode
	
	def __repr__(self):
		return "Timecode(timecode='%s', frame_rate=%.2f, is_drop_frame=%s)" % (self.timecode, self.frame_rate, self.is_drop_frame)
	
	def _op(self, op, other):
		if type(other) == Timecode:
			return Timecode(op(self.total_seconds, other.total_seconds), self.frame_rate, self.is_drop_frame)
		
		elif type(other) in (float, Decimal):
			return Timecode(op(self.total_seconds, Decimal(str(other))), self.frame_rate, self.is_drop_frame)
		
		elif type(other) in (int, long):
			return Timecode(op(self.total_frames, other), self.frame_rate, self.is_drop_frame)
		
		elif isinstance(other, basestring):
			return Timecode(op(self.total_seconds, Timecode(other, self.frame_rate, self.is_drop_frame).total_seconds), self.frame_rate, self.is_drop_frame)
		
		else:
			raise TypeError("unsupported operand type(s) for {op}: 'Timecode' and '{type}'".format(op=str(op)[19:-1], type=type(other)))
	
	def __add__(self, other):
		return self._op(operator.add, other)
	
	def __sub__(self, other):
		return self._op(operator.sub, other)
	
	def __mul__(self, other):
		return self._op(operator.mul, other)
	
	def __div__(self, other):
		return self._op(operator.div, other)
	
	def _rop(self, op, other):
		if type(other) == Timecode:
			return self._op(op, other)
		
		elif type(other) in (float, Decimal):
			return self._op(op, Decimal(str(other))).total_seconds
		
		elif type(other) in (int, long):
			return self._op(op, other).total_frames
		
		elif isinstance(other, basestring):
			return self._op(op, other).timecode
		
		else:
			raise TypeError("unsupported operand type(s) for {opp}: '{type}' and 'Timecode'".format(op=str(op)[19:-1], type=type(other)))
	
	def __radd__(self, other):
		return self._rop(operator.add, other)
	
	def __rsub__(self, other):
		return self._rop(operator.sub, other)
	
	def __rmul__(self, other):
		return self._rop(operator.mul, other)
	
	def __rdiv__(self, other):
		return self._rop(operator.div, other)
	
	def __eq__(self, other):
		if type(other) == Timecode:
			return self.total_seconds == other.total_seconds
		
		elif type(other) in (float, Decimal):
			return self.total_seconds == Decimal(str(other))
		
		elif type(other) in (int, long):
			return self.total_frames == other
		
		elif isinstance(other, basestring):
			return self.total_frames == Timecode(other, self.frame_rate, self.is_drop_frame).total_frames
		
		else:
			return False
	
	def __ne__(self, other):
		return not self.__eq__(other)
	
	def __gt__(self, other):
		if type(other) == Timecode:
			return self.total_seconds > other.total_seconds
		
		elif type(other) in (float, Decimal):
			return self.total_seconds > Decimal(str(other))
		
		elif type(other) in (int, long):
			return self.total_frames > other
		
		elif isinstance(other, basestring):
			return self.total_frames > Timecode(other, self.frame_rate, self.is_drop_frame).total_frames
		
		else:
			return False
	
	def __lt__(self, other):
		return not self.__gt__(other)
	
	def __ge__(self, other):
		return self.__gt__(other) or self.__eq__(other)
	
	def __le__(self, other):
		return self.__lt__(other) or self.__eq__(other)
