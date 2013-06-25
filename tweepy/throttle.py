import sys
import time

class RateLimitInfo(object):
    def __init__(self, headers={}):
        self.from_headers(headers)

    def from_headers(self, d):
        self.reset = int(d.get('x-rate-limit-reset', sys.maxint))
        self.remaining = int(d.get('x-rate-limit-remaining', sys.maxint))
        self.limit = int(d.get('x-rate-limit-limit', sys.maxint))

    def seconds_till_reset(self, current_time=None):
        current_time = current_time or time.time()
        return self.reset - current_time

    def __repr__(self):
        state = ['%s=%s' % (k, repr(v)) for (k,v) in vars(self).items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(state))


class RateLimitStorage(object):
    def __init__(self):
        self.rateLimits = {}
        
    #Get a safe bet on the limit of a call that was never made yet.
    def get_default(self):
        default = RateLimitInfo()
        default.reset = int(time.time() + 900)
        default.remaining = 15
        default.limit = 15
        return default
        
    def _store(self, path, limit):
        self.rateLimits[path]=limit
        
    def update(self, path, response):
        headers = dict(response.getheaders())
        self._store(path, RateLimitInfo(headers=headers))
    
    def get_rate_limit(self, path):
        #If we stored a limit already, return it, if we haven't, that means that the app never called "path" yet
        #so we return a safe-to-assume default 15 calls limit in the next 15 mins.
        if path in self.rateLimits.keys():
            return self.rateLimits[path]
        else:
            return self.get_default()
        