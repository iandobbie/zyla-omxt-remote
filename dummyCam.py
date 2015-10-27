import memhandler
import neo

import numpy

import threading
import time
import traceback


## Because all functions in the neo module a) accept a camera handle as a
# first argument, and b) return an error code as the primary return value,
# we make this wrapper around the entire library to make interacting with
# it cleaner. It initializes the library, connects to the camera, and
# wraps every API function to handle error conditions.
class WrappedNeo:
    def __init__(self):
        self.errorCodes = dict()
        allItems = neo.__dict__.items() + memhandler.__dict__.items()
        for key, value in allItems:
            if callable(value):
                self.__dict__[key] = self.wrapFunction(value)
            # Also capture the error codes at this time so we can
            # provide their names instead of bare numbers.
            elif 'AT_ERR' == key[:6] or 'ERR_' == key[:4]:
                self.errorCodes[value] = key

        startTime = time.time()
        print "Initializing Andor library...",
        error = neo.AT_InitialiseLibrary()
        if error:
            raise RuntimeException("Failed to initialize Andor library: %s" % self.errorCodes[error])
        print "done in %.2f seconds" % (time.time() - startTime)
        error, self.handle = neo.AT_Open(0)
        if error:
            raise RuntimeError("Failed to connect to camera: %s" % self.errorCodes[error])
        elif self.handle == -1:
            raise RuntimeError("Got an invalid handle from the camera")
        else:
            print "Connected to camera with handle",self.handle


    ## Clean up after ourselves.
    def __del__(self):
        print "Close:",neo.AT_Close(self.handle)
        print "Finalize:",neo.AT_FinaliseLibrary()


    ## Manual decorator function -- call the passed-in function with our
    # handle, and raise an exception if an error occurs.
    def wrapFunction(self, func):
        def wrappedFunction(*args, **kwargs):
            if func.__name__ != 'getUpdatedMemory':
                print "Calling",func.__name__,"with args",args
            result = func(self.handle, *args, **kwargs)
            # result may be a single value, a length-2 list, or a
            # length-3+ list. We return None, the second value, or
            # a tuple in those respective cases.
            errorCode = result
            returnVal = None
            if type(result) in [tuple, list]: # Type paranoia
                errorCode = result[0]
                if len(result) == 2:
                    returnVal = result[1]
                else:
                    returnVal = tuple(result[1:])
            if errorCode:
                errorString = "unknown error %s" % errorCode
                if errorCode in self.errorCodes:
                    errorString = "error %s" % self.errorCodes[errorCode]
                raise RuntimeError("An %s occurred calling function %s with args %s and %s" % (errorString, func, args, kwargs))
            return returnVal
        return wrappedFunction



wrappedNeo = WrappedNeo()

width = wrappedNeo.AT_GetInt('SensorWidth')
height = wrappedNeo.AT_GetInt('SensorHeight')
wrappedNeo.AT_SetEnumString("FanSpeed", "Off")
wrappedNeo.AT_SetBool("SensorCooling", True)
wrappedNeo.AT_SetFloat("TargetSensorTemperature", -50)
wrappedNeo.AT_SetEnumIndex("PreAmpGainControl", 0)

#wrappedNeo.AT_SetEnumIndex('PixelEncoding', 1)
wrappedNeo.AT_SetEnumString('TriggerMode', 'External')
wrappedNeo.AT_SetEnumString('CycleMode', 'Continuous')
wrappedNeo.AT_SetEnumString('PixelReadoutRate', '200 MHz')
wrappedNeo.AT_SetFloat('ExposureTime', .015)
imageBytes = wrappedNeo.AT_GetInt('ImageSizeBytes')
for i in xrange(10):
    wrappedNeo.allocMemory(imageBytes)
wrappedNeo.AT_Command('AcquisitionStart')
print "Acquisition started"
raw_input()
for i in xrange(10):
    print ("Getting image %d..." % i),
    attempts = 0
    while attempts < 5:
        try:
            val = wrappedNeo.getUpdatedMemory(imageBytes, 1000)
            print "got image with bytes", val[:10]
            break
        except Exception, e:
            attempts += 1
    if attempts == 5:
        print "Failed"
    wrappedNeo.allocMemory(imageBytes)

raw_input()
