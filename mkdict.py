

class mkdict(object):

	class _FullKeyPtr(object):
		def __init__(self, full_key):
			self.full_key = full_key

	def __init__(self, d={}, **kwargs):
		self._dict = dict()
		self._key_map = dict()
		self._dict_backup = None
		self._key_map_backup = None
		self.update(d, **kwargs)

	def __str__(self):
		return str(self._dict)

	def __len__(self):
		return len(self._dict)

	def __getitem__(self, key):
		if key in self._key_map:
			key = self.full_key(key)
		return self._dict[key]

	def __setitem__(self, key, value):
		if key in self._key_map:
			key = self.full_key(key)

		if key not in self._dict:
			if isinstance(key, tuple):
				key = tuple(set(key))
				full_key_ptr = self._FullKeyPtr(key)
				for k in key:
					if k in self:
						self._key_already_set(k)
					self._key_map[k] = full_key_ptr
			else:
				self._key_map[key] = self._FullKeyPtr(key)

		self._dict[key] = value

	def __delitem__(self, key):
		self.remove(key)

	def __contains__(self, key):
		return key in self._key_map or key in self._dict

	def __iter__(self):
		return iter(self._dict)	

	def update(self, d={}, **kwargs):
		d.update(kwargs)
		for k, v in d.items():
			self[k] = v

	def items(self):
		return self._dict.items()

	def keys(self):
		return self._dict.keys()

	def pop(self):
		pass

	def clear(self):
		self._dict.clear()
		self._key_map.clear()

	@property
	def dict(self):
		return self._dict.copy()

	def full_key(self, key):
		return self._key_map[key].full_key

	def append(self, key, other_key):
		pass

	def remove(self, key, return_value=False):
		if key in self._dict:
			if isinstance(key, tuple):
				for k in key:
					del self._key_map[k]
			else:
				del self._key_map[key]
			del self._dict[key]
			return

		current_full_key = self.full_key(key)
		new_full_key = list(current_full_key)
		new_full_key.remove(key)

		if len(new_full_key) == 1:
			new_full_key = new_full_key[0]
		else:
			new_full_key = tuple(new_full_key)

		self._dict[new_full_key] = self._dict[current_full_key]
		del self._dict[current_full_key]
		self._key_map[key].full_key = new_full_key
		del self._key_map[key]

	def aliases(self, key):
		full_key = self.full_key(key)
		if isinstance(full_key, tuple):
			aliases = list(full_key)
			aliases.remove(key)
			return aliases
		return list()
	
	def backup(self):
		self._dict_backup = self.dict
		self._key_map_backup = self._key_map.copy()

	def revert(self):
		if None not in (self._dict_backup, self._key_map_backup):
			self._dict = self._dict_backup
			self._key_map = self._key_map_backup
			
	def _key_already_set(self, key):
		del self[key]

