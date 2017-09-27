# -*- coding: utf-8 -*-


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

@singleton
class Settings(object):
    __instance = None

    display_off_active = True
    display_off_timeout = 90.0
    offlinemode = False

    def __init__(self, **kwargs):
        #print '\n\n\n Settings \n\n\n'
        pass
