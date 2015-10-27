// This is a SWIG interface file for a custom C library designed to
// make wrapping certain troublesome functions in the Andor SDK3
// library easier.

%include typemaps.i

%{
#define SWIG_FILE_WITH_INIT
%}
%include numpy.i
%init %{
import_array();
%}

%module memhandler
%{
#include "memhandler.hh"
%}

#define ERR_NO_MEMORY_ALLOCATED 1000
#define ERR_BUFFER_NOT_FOUND 1001

%apply (unsigned short* ARGOUT_ARRAY1, int DIM1) {(unsigned short* outputBuffer, int numElements)};

int allocMemory(int handle, int numBuffers, int numElements);
int getUpdatedMemory(int handle, unsigned short* outputBuffer,
                     int numElements, int timeout);
