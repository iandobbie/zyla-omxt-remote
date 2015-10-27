import memhandler
import neo

import numpy
import time

## Save an array as an image. Copied from 
# http://stackoverflow.com/questions/902761/saving-a-numpy-array-as-an-image
def imsave(filename, array, vmin=None, vmax=None, cmap=None,
           format=None, origin=None):
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure

    fig = Figure(figsize=array.shape[::-1], dpi=1, frameon=False)
    canvas = FigureCanvas(fig)
    fig.figimage(array, cmap=cmap, vmin=vmin, vmax=vmax, origin=origin)
    fig.savefig(filename, dpi=1, format=format)


## Because all functions in the neo module a) accept a camera handle as a
# first argument, and b) return an error code as a second argument, we make
# this wrapper around the entire library to make interacting with it cleaner.
# It initializes the library, connects to the camera, and wraps every API
# function to handle error conditions.
class WrappedNeo:
    def __init__(self):
        self.errorCodes = dict()
        for key, value in neo.__dict__.iteritems():
            if callable(value):
                self.__dict__[key] = self.wrapFunction(value)
            # Also capture the error codes at this time so we can
            # look up their descriptions.
            elif 'AT_ERR' == key[:6]:
                self.errorCodes[value] = key
        for key, value in memhandler.__dict__.iteritems():
            if callable(value):
                self.__dict__[key] = self.wrapFunction(value)

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

        self.AT_SetEnumString("FanSpeed", "On")
        self.AT_SetBool("SensorCooling", True)
        self.AT_SetFloat("TargetSensorTemperature", -15)
        # 11 bits per pixel
        self.AT_SetEnumIndex("PreAmpGainControl", 0)


    ## Manual decorator function -- call the passed-in function with our
    # handle, and raise an exception if an error occurs.
    def wrapFunction(self, func):
        def wrappedFunction(*args, **kwargs):
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
                raise RuntimeError("An error %s occurred calling function %s with args %s and %s" % (self.errorCodes[errorCode], func, args, kwargs))
            return returnVal
        return wrappedFunction


    ## Clean up after ourselves.
    def __del__(self):
        print "Close:",neo.AT_Close(self.handle)
        print "Finalize:",neo.AT_FinaliseLibrary()


wrappedNeo = WrappedNeo()    

class Camera:
    def __init__(self):

        wrappedNeo.AT_SetFloat('ExposureTime', .1)
        imageBytes = wrappedNeo.AT_GetInt('ImageSizeBytes')
        height = wrappedNeo.AT_GetInt('SensorHeight')
        width = wrappedNeo.AT_GetInt('SensorWidth')

        wrappedNeo.allocMemory(imageBytes)

        print "CCD sensor shape:",width,height
        print "Bit depth:",wrappedNeo.AT_GetEnumIndex('BitDepth')
        print "Fan speed:",wrappedNeo.AT_GetEnumIndex('FanSpeed')
        print "Sensor cooling:",wrappedNeo.AT_GetBool('SensorCooling')
        print "Temp status:",wrappedNeo.AT_GetEnumIndex('TemperatureStatus')
        print "Sensor temperature",wrappedNeo.AT_GetFloat('SensorTemperature')

        wrappedNeo.AT_Command("AcquisitionStart")
        image = wrappedNeo.getUpdatedMemory(width * height, 5000)
        wrappedNeo.AT_Command("AcquisitionStop")

        print "Received image with min/max %d/%d" % (image.min(), image.max())        
        image.shape = height, width
        imsave('out.png', image)

try:
    cam = Camera()
except Exception, e:
    print "Exception occurred:",e
    import traceback
    traceback.print_stack()

del wrappedNeo # Clean up after ourselves.

