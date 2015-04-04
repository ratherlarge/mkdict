# -*- coding: utf-8 -*-

class mkdict(object):
    """ A dictionary that allows multiple keys for one value """
    _init_dict = True
    
    class dict(object):
        """ Interface for mkdict.dict for dict-like behaviour """
        _init_mkdict = True

        def __init__(self, d={}, **kwargs):
            """ This is to avoid recursion when allowing:
            
            >>> d = mkdict.dict({'what': 'ever'})
            
            or...
            
            >>> d = mkdict({'what', 'ever'})
            """
            if self._init_mkdict:
                mkdict._init_dict = False
                self.mkdict = mkdict(d, **kwargs)
                mkdict._init_dict = True

                self.mkdict.dict = self

        def __str__(self):
            return str(self.mkdict._dict)

        def __repr__(self):
            return str(self)

        def __len__(self):
            return len(self.mkdict._dict)

        def __setitem__(self, key, value):
            """ Desired behaviour:
            
            >>> d = mkdict()
            >>> d['what', 'ever'] = 'testing'
            >>>
            >>> d
            >>> {'what': 'testing', 'ever': 'testing'}
            >>>
            >>> d.dict
            >>> {('what', 'ever'): 'testing'}
            >>>
            >>> d.dict['what'] = 'new value'
            >>>
            >>> d
            >>> {'what': 'new value', 'ever': 'testing'}
            >>>
            >>> d.dict
            >>> {'what': 'new value', 'ever': 'testing'}
            """
            if key not in self and key in self.mkdict:
                self.mkdict._key_already_set(key)

            self.mkdict[key] = value

        def __getitem__(self, key):
            return self.mkdict._dict[key]

        def __contains__(self, key):
            return key in self.mkdict._dict

        def __delitem__(self, key):
            if key not in self:
                raise KeyError(key)
            
            if isinstance(key, tuple):
                key = key[0]

            del self.mkdict[key]

        def __getattr__(self, attr):
            return getattr(self.mkdict._dict, attr)

        def clear(self):
            self.mkdict.clear()
    
    class _FullKeyPtr(object):
        """ Desired behaviour:
        
        full_key_ptr1 = _FullKeyPtr()
        mkdict._key_map -> {'key1', full_key_ptr1,
                            'key2', full_key_ptr1}
        
        >>> d = mkdict()
        >>> d['what', 'ever'] = 'testing'
        >>> d._key_map
        >>>
        >>> # d._key_map:
        >>> # {'what': full_key_ptr1, 'ever': full_key_ptr1}
        >>> d._key_map
        >>> {'what': ('what', 'ever'), 'ever': ('what', 'ever')}
        >>>
        >>> d['what']
        >>> 'testing'
        >>>
        >>> # full_key = _key_map['ever'].full_key
        >>> # i.e. full_key = ('what', 'ever')
        >>> # _dict[full_key] = 'test'
        >>> d['ever'] = 'test'
        >>>
        >>>
        >>> d['what']
        >>> 'test'
        """

        def __init__(self, full_key):
            self.full_key = full_key

        def __str__(self):
            return str(self.full_key)

        def __repr__(self):
            return str(self)
            
    def __init__(self, d={}, **kwargs):

        """ This is to avoid recursion when allowing:
            
        >>> d = mkdict({'what': 'ever'})
        
        or...
        
        >>> d = mkdict.dict({'what': 'ever'})
        """
        if self._init_dict:
            mkdict.dict._init_mkdict = False
            self.dict = mkdict.dict()
            mkdict.dict._init_mkdict = True

            self.dict.mkdict = self
        
        self._dict = dict()
        self._key_map = dict()
        self._dict_backup = None
        self._key_map_backup = None
        self.update(d, **kwargs)
        
    def __str__(self):
        return str(dict(self.items()))

    def __repr__(self):
        return str(self)
        
    def __len__(self):
        return len(self._key_map)

    def __iter__(self):
        return iter(self.keys())
        
    def __getitem__(self, key):
        full_key = self.full_key(key)
        return self.dict[full_key]
        
    def __setitem__(self, key, value):
        """ Desired behaviour:
            
        >>> d = mkdict()
        >>> d['what', 'ever'] = 'testing'
        >>>
        >>> d
        >>> {'what': 'testing', 'ever': 'testing'}
        >>>
        >>> d.dict
        >>> {('what', 'ever'): 'testing'}
        >>>
        >>> d['what'] = 'new value'
        >>> d
        >>> {'what': 'new value', 'ever': 'new value'}
        >>>
        >>> d.dict
        >>> {('what', 'ever'): 'new value'}
        """
        if key in self:
            key = self.full_key(key)

        if key not in self._dict:
            if isinstance(key, tuple):
                full_key_ptr = self._FullKeyPtr(key)
                for k in key:
                    if k in self:
                        self._key_already_set(k)
                    self._key_map[k] = full_key_ptr
            else:
                self._key_map[key] = self._FullKeyPtr(key)
                
        self._dict[key] = value
        
    def __delitem__(self, key):
        full_key = self.full_key(key)

        if isinstance(full_key, tuple):
            for k in full_key:
                del self._key_map[k]
        else:
            del self._key_map[full_key]

        del self._dict[full_key]
        
    def __contains__(self, key):
        return key in self._key_map
        
    def __getattr__(self, attr):
        return getattr(self._dict, attr)

    def items(self):
        return [(k, self[k]) for k, v in self._key_map.items()]

    def iteritems(self):
        return iter(self.items())
        
    def update(self, d={}, **kwargs):
        d.update(kwargs)
        for k, v in d.items():
            self[k] = v
    
    def clear(self):
        self._dict.clear()
        self._key_map.clear()

    def keys(self):
        return self._key_map.keys()
        
    def full_key(self, key):
        return self._key_map[key].full_key

    def has_key(self, key):
        return key in self
        
    def append(self, key, otherkey):
        pass
    
    def remove(self, key):
        full_key = self.full_key(key)

        if not isinstance(full_key, tuple):
            del self._dict[full_key]
            del self._key_map[full_key]
            return

        new_full_key = list(full_key)
        new_full_key.remove(key)
        
        if len(new_full_key) == 1:
            new_full_key = new_full_key[0]
        else:
            new_full_key = tuple(new_full_key)
            
        self._dict[new_full_key] = self.dict[full_key]
        del self._dict[full_key]
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
        pass
        
    def revert(self):
        pass
            
    def _key_already_set(self, key):
        self.remove(key)
        
