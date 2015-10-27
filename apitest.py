#class Writer:
#    def __init__(self, filename):
#        self.handle = open(filename, 'w')
#    def write(self, content):
#        self.handle.write(content)
#
#foo = Writer('out.txt')
#import sys
#sys.stdout = foo

import neo
neo.AT_InitialiseLibrary()
error, handle = neo.AT_Open(0)
print "Connect:",error,handle
print "Number of devices",neo.AT_GetInt(neo.AT_HANDLE_SYSTEM, "DeviceCount")
print "Number of devices",neo.AT_GetInt(neo.AT_HANDLE_SYSTEM, "DeviceCount")
print "Max size:",neo.AT_GetStringMaxLength(neo.AT_HANDLE_SYSTEM, "SoftwareVersion")
print neo.AT_GetString(neo.AT_HANDLE_SYSTEM, "SoftwareVersion")

print neo.AT_GetInt(handle, 'ImageSizeBytes')

for feature, featType in [('FrameCount', neo.AT_GetInt),
                          ('FrameRate', neo.AT_GetFloat),
                          ('ImageSizeBytes', neo.AT_GetInt),
                          ('ExposureTime', neo.AT_GetFloat)]:
    print feature
    print "Implemented:",neo.AT_IsImplemented(handle, feature)
    print "Readable:",neo.AT_IsReadable(handle, feature)
    print "Writable:",neo.AT_IsWritable(handle, feature)
    print "Read-only:",neo.AT_IsReadOnly(handle, feature)
    print "Value:",featType(handle, feature)

print "\n"

for feature in ['BitDepth', 'CycleMode', 'FanSpeed', 'PixelCorrection']:
    print feature
    print "Index:", neo.AT_GetEnumIndex(handle, feature)
    error, count = neo.AT_GetEnumCount(handle, feature)
    print "Count:", [error, count]
    if not error:
        for i in xrange(count):
            s = "  %d of %d (%s)" % (i, count, feature)
            print s,'available:',neo.AT_IsEnumIndexAvailable(handle, feature, i)
            print s,'implemented:',neo.AT_IsEnumIndexImplemented(handle, feature, i)
            print s,'set by index:', neo.AT_SetEnumIndex(handle, feature, i)
        print "Available:", [neo.AT_IsEnumIndexAvailable(handle, feature, i) for i in xrange(count)]
        print "Implemented:", [neo.AT_IsEnumIndexImplemented(handle, feature, i) for i in xrange(count)]
        print "Set by index:", [neo.AT_SetEnumIndex(handle, feature, i) for i in xrange(count)]
    
print "Close:",neo.AT_Close(handle)
print "Finalize:",neo.AT_FinaliseLibrary()

#foo.handle.close()
