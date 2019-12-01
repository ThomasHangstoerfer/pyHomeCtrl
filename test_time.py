import time


class T:

    def __init__(self, h, m):
        self.tm_hour = h
        self.tm_min = m


t = T(10, 36)


def is_earlier(h, m):
    #        10        10          40    20
    return (t.tm_hour == h and t.tm_min > m) or t.tm_hour > h


def is_later(h, m):
    #        23        23          00    01
    return (t.tm_hour == h and t.tm_min < m) or t.tm_hour < h


if __name__ == '__main__':
    t.tm_hour, t.tm_min = 10, 40
    h, m = 10, 20
    print('%02i:%02i is %searlier than %02i:%02i ' % (h, m, '' if is_earlier(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 10, 40
    h, m = 9, 20
    print('%02i:%02i is %searlier than %02i:%02i ' % (h, m, '' if is_earlier(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 10, 40
    h, m = 9, 50
    print('%02i:%02i is %searlier than %02i:%02i ' % (h, m, '' if is_earlier(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 11, 00
    h, m = 10, 59
    print('%02i:%02i is %searlier than %02i:%02i ' % (h, m, '' if is_earlier(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 11, 00
    h, m = 11, 00
    print('%02i:%02i is %searlier than %02i:%02i ' % (h, m, '' if is_earlier(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 11, 00
    h, m = 11, 1
    print('%02i:%02i is %searlier than %02i:%02i ' % (h, m, '' if is_earlier(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 23, 00
    h, m = 6, 1
    print('%02i:%02i is %searlier than %02i:%02i ' % (h, m, '' if is_earlier(h, m) else 'not ', t.tm_hour, t.tm_min))
    print('')
    t.tm_hour, t.tm_min = 23, 00
    h, m = 6, 1
    print('%02i:%02i is %slater than %02i:%02i ' % (h, m, '' if is_later(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 23, 00
    h, m = 23, 00
    print('%02i:%02i is %slater than %02i:%02i ' % (h, m, '' if is_later(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 23, 00
    h, m = 23, 1
    print('%02i:%02i is %slater than %02i:%02i ' % (h, m, '' if is_later(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 10, 40
    h, m = 10, 41
    print('%02i:%02i is %slater than %02i:%02i ' % (h, m, '' if is_later(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 10, 40
    h, m = 10, 39
    print('%02i:%02i is %slater than %02i:%02i ' % (h, m, '' if is_later(h, m) else 'not ', t.tm_hour, t.tm_min))
    t.tm_hour, t.tm_min = 11, 29
    h, m = 11, 31
    print('%02i:%02i is %slater than %02i:%02i ' % (h, m, '' if is_later(h, m) else 'not ', t.tm_hour, t.tm_min))
