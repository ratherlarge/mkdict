
class mkdict(object):
    
    class dict(object):

        def __init__(self, mkdict):
            self._dict = dict()
            self.mkdict = mkdict

        def __str__(self):
            return str(self._dict)

        def __repr__(self):
            return str(self)

        def __len__(self):
            return len(self._dict)

        def __setitem__(self, key, value):
            if key not in self:
                if key in self.mkdict._key_map:
                    self.mkdict.remove(key)
            self.mkdict[key] = value

        def __getitem__(self, key):
            return self._dict[key]

        def __contains__(self, key):
            return key in self._dict

        def __delitem__(self, key):
            if key not in self:
                raise KeyError(key)
            del self.mkdict[key]

        def __getattr__(self, attr):
            return getattr(self._dict, attr)

        def clear(self):
            self._dict.clear()
            self.mkdict._key_map.clear()
    
    class _FullKeyPtr(object):

        def __init__(self, full_key):
            self.full_key = full_key

        def __str__(self):
            return str(self.full_key)

        def __repr__(self):
            return str(self)
            
    def __init__(self, d={}, **kwargs):
        self.dict = mkdict.dict(self)
        self._key_map = dict()
        self._dict_backup = None
        self._key_map_backup = None
        self.update(d, **kwargs)
        
    def __str__(self):
        return str(self.items())

    def __repr__(self):
        return str(self)
        
    def __len__(self):
        return len(self._key_map)

    def __iter__(self):
        return iter(self.keys())
        
    def __getitem__(self, key):
        if key in self._key_map:
            key = self.full_key(key)
        return self.dict[key]
        
    def __setitem__(self, key, value):
        if key in self._key_map:
            key = self.full_key(key)
            
        if key not in self.dict:
            if isinstance(key, tuple):
                #key = tuple(set(key))
                full_key_ptr = self._FullKeyPtr(key)
                for k in key:
                    if k in self:
                        self._key_already_set(k)
                    self._key_map[k] = full_key_ptr
            else:
                self._key_map[key] = self._FullKeyPtr(key)
                
        self.dict._dict[key] = value
        
    def __delitem__(self, key):
        if key in self._key_map:
            key = self.full_key(key)
        
        if isinstance(key, tuple):
            for k in key:
                del self._key_map[k]
        else:
            del self._key_map[key]
            
        del self.dict._dict[key]
        
    def __contains__(self, key):
        return key in self._key_map or key in self.dict
        
    def __getattr__(self, attr):
        return getattr(self.dict, attr)

    def items(self):
        pass

    def iteritems(self):
        pass
        
    def update(self, d={}, **kwargs):
        d.update(kwargs)
        for k, v in d.items():
            self[k] = v
    
    def clear(self):
        self.dict._dict.clear()
        self._key_map.clear()

    def keys(self):
        return self._key_map.keys()
        
    def full_key(self, key):
        return self._key_map[key].full_key

    def has_key(self, key):
        return key in self
        
    def append(self, key, otherkey):
        pass
    
    def remove(self, key, return_value=False):
        if key in self.dict:
            del self[key]
            return
        
        current_full_key = self.full_key(key)
        new_full_key = list(current_full_key)
        new_full_key.remove(key)
        
        if len(new_full_key) == 1:
            new_full_key = new_full_key[0]
        else:
            new_full_key = tuple(new_full_key)
            
        self.dict._dict[new_full_key] = self.dict[current_full_key]
        del self.dict._dict[current_full_key]
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
        self._dict_backup = self.dict.copy()
        self._key_map_backup = self._key_map.copy()
        
    def revert(self):
        if None not in (self._dict_backup, self._key_map_backup):
            self.dict = self._dict_backup
            self._key_map = self._key_map_backup
            
    def _key_already_set(self, key):
        self.remove(key)
        
