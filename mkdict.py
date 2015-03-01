
class mkdict(object):
    
    class dict(object):
        def __init__(self, mkdict):
            self.mkdict = mkdict
        def __del__(self):
            pass
		def remove(self):
			pass
    
    class _FullKeyPtr(object):
        def __init__(self, fullkey):
            self.fullkey = fullkey
            
    def __init__(self, d={}, **kwargs):
        self.dict = mkdict.dict(self)
        self._keymap = dict()
        self._dict_backup = None
        self._keymap_backup
        self.update(d, **kwargs)
        
    def __str__(self):
        return str(self.dict)
        
    def __len__(self):
        return len(self.dict)
        
    def __getitem__(self, key):
        if key in self._keymap:
            key = self.fullkey(key)
        return self.dict[key]
        
    def __setitem__(self, key, value):
        if key in self._keymap:
            key = self.fullkey(key)
            
        if key not in self.dict:
            if isinstance(key, tuple):
                key = tuple(set(key))
                fullkey_ptr = self._FullKeyPtr(key)
                for k in key:
                    if k in self:
                        self._key_already_set(k)
                    self._keymap[k] = fullkey_ptr
            else:
                self._keymap[key] = self._FullKeyPtr(key)
                
        self.dict[key] = value
        
    def __delitem__(self, key):
        fullkey = self.fullkey(key)
        
        if isinstance(fullkey, tuple):
            for k in fullkey:
                del self._keymap[k]
        else:
            del self._keymap[fullkey]
            
        del self.dict[fullkey]
        
    def __contains__(self, key):
        return key in self._keymap or key in self.dict
        
    def __iter__(self):
        return iter(self.dict)
        
    def __getattr__(self, attr):
        return getattr(self.dict, attr)
        
    def update(self, d={}, **kwargs):
        d.update(kwargs)
        for k, v in d.items():
            self[k] = v
    
    def clear(self):
        self.dict.clear()
        self._keymap.clear()
        
    def fullkey(self, key):
        return self._keymap[key].fullkey
        
    def append(self, key, otherkey):
        pass
    
    def remove(self, key, return_value=False):
        if key in self.dict:
            del self[key]
            return
        
        current_fullkey = self.fullkey(key)
        new_fullkey = list(current_fullkey)
        new_fullkey.remove(key)
        
        if len(new_fullkey) == 1:
            new_fullkey = new_fullkey[0]
        else:
            new_fullkey = tuple(new_fullkey)
            
        self.dict[new_fullkey] = self.dict[current_fullkey]
        del self.dict[current_fullkey]
        self._keymap[key].fullkey = new_fullkey
        del self._keymap[key]
        
    def aliases(self, key):
        fullkey = self.fullkey(key)
        if isinstance(fullkey, tuple):
            aliases = list(fullkey)
            aliases.remove(key)
            return aliases
        return list()
        
    def backup(self):
        self._dict_backup = self.dict.copy()
        self._keymap_backup = self._keymap.copy()
        
    def revert(self):
        if None not in (self._dict_backup, self._keymap_backup):
            self.dict = self._dict_backup
            self._keymap = self._keymap_backup
            
    def _key_already_set(self, key):
        self.remove(key)
        
