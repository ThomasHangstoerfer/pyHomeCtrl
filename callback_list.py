# -*- coding: utf-8 -*-


class CallbackList(list):
     def fire(self, *args, **kwargs):
         for listener in self:
             listener(*args, **kwargs)