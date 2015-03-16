
class mkdict(object):
    
    class dict(object):

        def __init__(self, mkdict):
            self._dict = dict()
            self.mkdict = mkdict

        def __str__(self):
            return str(self._dict)

        def __repr__(self):
            return str(self)

        def __setitem__(self, key, value):
            if key not in self:
                if key in self.mkdict._keymap:
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
    
    class _FullKeyPtr(object):

        def __init__(self, fullkey):
            self.fullkey = fullkey

        def __str__(self):
            return str(self.fullkey)

        def __repr__(self):
            return str(self)
            
    def __init__(self, d={}, **kwargs):
        self.dict = mkdict.dict(self)
        self._keymap = dict()
        self._dict_backup = None
        self._keymap_backup = None
        self.update(d, **kwargs)
        
    def __str__(self):
        return str(self.items())

    def __repr__(self):
        return str(self)
        
    def __len__(self):
        return len(self.dict)

    def __iter__(self):
        return iter(self.keys())
        
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
                
        self.dict._dict[key] = value
        
    def __delitem__(self, key):
        if key in self._keymap:
            key = self.fullkey(key)
        
        if isinstance(key, tuple):
            for k in key:
                del self._keymap[k]
        else:
            del self._keymap[key]
            
        del self.dict._dict[key]
        
    def __contains__(self, key):
        return key in self._keymap or key in self.dict
        
    def __getattr__(self, attr):
        return getattr(self.dict, attr)

    def items(self):
        return {k: self[v.fullkey] for k, v in self._keymap.items()}

    def iteritems(self):
        return {k: self[v.fullkey]
                for k, v in self._keymap.iteritems()}.iteritems()
        
    def update(self, d={}, **kwargs):
        d.update(kwargs)
        for k, v in d.items():
            self[k] = v
    
    def clear(self):
        self.dict.clear()
        self._keymap.clear()

    def keys(self):
        return self._keymap.keys()
        
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
            
        self.dict._dict[new_fullkey] = self.dict[current_fullkey]
        del self.dict._dict[current_fullkey]
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
        
