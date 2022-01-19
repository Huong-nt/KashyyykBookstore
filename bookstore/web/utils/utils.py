# -*- coding: utf-8 -*-

class Utils:
    def __init__(self):
        pass

    def remove_none_params(self, params):
        return {key: value for (key, value) in params.items() if value is not None}
    
    def gen_otp(self):
        return str(self._random_with_n_digits(6))

