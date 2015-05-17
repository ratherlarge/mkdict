# -*- coding: utf-8 -*-

class mkdict(object):
    """ A dictionary that allows multiple keys for one value """


    class _Container(object):
        """ This is used to wrap an object to avoid infinite 
        recursion when calling my own methods from the inside.
        
        If a method sees this container, it assumes it has been
        called from the inside and not the user.
        """

        def __init__(self, _object):
            self.object = _object

    
    class dict(object):
        """ Interface for mkdict._dict for dict-like behaviour """

        def __init__(self, d={}, **kwargs):
            """ Using an mkdict._Container to avoid infinite
            recursion when allowing:
                
            >>> d = mkdict({'what': 'ever'})
            >>> d = mkdict.dict({'what': 'ever'})
            """
            if isinstance(d, mkdict._Container):
                self.mkdict = d.object
            else:
                self.mkdict = mkdict(mkdict._Container(self))
                self.update(d, **kwargs)

        def __str__(self):
            return str(self.mkdict._dict)

        def __repr__(self):
            return str(self)

        def __len__(self):
            return len(self.mkdict._dict)

        def __setitem__(self, key, value):
            """ Desired behaviour:
                
            >>> d = mkdict()
            >>>
            >>> d['what', 'ever'] = 'testing'
            >>> d
            {'what': 'testing', 'ever': 'testing'}
            >>> d.dict
            {('what', 'ever'): 'testing'}
            >>> d['what'] is d['ever']
            True
            >>>
            >>> d.dict['what'] = 'new value'
            >>> d
            {'what': 'new value', 'ever': 'testing'}
            >>> d.dict
            {'what': 'new value', 'ever': 'testing'}
            >>> d['what'] is d['ever']
            False
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

        def clear(self):
            self.mkdict.clear()

        def update(self, d, **kwargs):
            if isinstance(d, mkdict.dict):
                d = d.mkdict._dict
            elif isinstance(d, mkdict):
                d = d._dict

            d.update(kwargs)
            for k, v in d.items():
                self[k] = v

    
    class _FullKeyPtr(object):
        
        def __init__(self, full_key):
            self.full_key = full_key

        def __str__(self):
            return str(self.full_key)

        def __repr__(self):
            return str(self)
            

    def __init__(self, d={}, **kwargs):
        self._dict_backup = self._dict = dict()
        self._key_map_backup = self._key_map = dict()

        if isinstance(d, mkdict._Container):
            self.dict = d.object
        else:
            self.dict = mkdict.dict(mkdict._Container(self))
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
        >>> d
        {'what': 'testing', 'ever': 'testing'}
        >>> d.dict
        {('what', 'ever'): 'testing'}
        >>> d['what'] is d['ever']
        True
        >>>
        >>> d['what'] = 'hello'
        >>> d
        {'what': 'hello', 'ever': 'hello'}
        >>> d.dict
        {('what', 'ever'): 'hello'}
        >>> d['what'] is d['ever']
        True
        """
        if isinstance(key, list):
            key = tuple(key)

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

    def items(self):
        return [(k, self[k]) for k, v in self._key_map.items()]

    def iteritems(self):
        return iter(self.items())
        
    def update(self, d={}, **kwargs):
        if isinstance(d, mkdict.dict):
            d = d.mkdict._dict
        elif isinstance(d, mkdict):
            d = d._dict

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
        
    def alias(self, key, new_key):
        full_key = self.full_key(key)

        if isinstance(full_key, tuple):
            new_full_key = list(full_key)
        else:
            new_full_key = [full_key]

        new_full_key.append(new_key)
        new_full_key = tuple(new_full_key)

        self._dict[new_full_key] = self._dict[full_key]
        del self._dict[full_key]
        self._key_map[new_key] = self._key_map[key]
        self._key_map[new_key].full_key = new_full_key
    
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
        self._dict_backup = self._dict.copy()
        self._key_map_backup = self._key_map.copy()
        
    def revert(self):
        self._dict = self._dict_backup
        self._key_map = self._key_map_backup
            
    def _key_already_set(self, key):
        self.remove(key)
        
