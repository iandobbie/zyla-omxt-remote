import threading
import time
import numpy

import Pyro4

remote = Pyro4.Proxy('PYRO:serve@192.168.137.1:1234')

data = numpy.zeros((540, 512), dtype = numpy.uint16)
for i in xrange(1000000):
    remote.serve(data)
