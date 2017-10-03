# -*- coding: utf-8 -*-

from threading import Timer


def singleton(cls):
    # https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
    # 'Duck()'
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls



class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.function   = function
        self.interval   = interval
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        #self.ignore_next = True
        self.ignore_next = False
        self.to_be_stopped = False
        self.start()

    def _run(self):
        self.is_running = False
        #print 'self.to_be_stopped = %s' % self.to_be_stopped
        if ( self.to_be_stopped == False ):
            self.start()
        #print('RepeatedTimer._run() ignore_next = ', self.ignore_next)
        if ( self.ignore_next ):
            #print('ignore first display_off')
            self.ignore_next = False
        else:
            self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        #print 'RepeatedTimer.stop()'
        self._timer.cancel()
        self.is_running = False

    def restart(self):
        #print 'RepeatedTimer.restart()'
        self.stop()
        self.start()

    def finish(self):
        #print 'RepeatedTimer.finish()'
        self.to_be_stopped = True
        self.stop()

