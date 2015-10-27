// This module is for converting AT_WC arrays to/from Python.

#include "atcore.h"

// Convert a Python string input to a AT_WC array alone.
%typemap(in) AT_WC* InputString {
    int len = PyString_Size($input);
    $1 = (AT_WC*) malloc((len + 1) * sizeof(AT_WC));
    mbstowcs($1, PyString_AsString($input), len);
    $1[len] = '\0';
}

// Convert a Python string input to a AT_WC array and an integer length.
%typemap(in) (AT_WC* InputFixedString, int InputLength) {
    $2 = PyString_Size($input);
    $1 = (AT_WC*) malloc(($2 + 1) * sizeof(AT_WC));
    mbstowcs($1, PyString_AsString($input), $2);
    $1[$2] = '\0';
}


// Create a buffer to hold a result string in.
%typemap(in, numinputs = 0) AT_WC* OutputString {
    $1 = (AT_WC*) malloc(128 * sizeof(AT_WC));
}
// Automatically generate a "size of result buffer" input. According
// to Andor reps strings should never be more than 32 characters
// long, but memory is cheap. This should match the size in the
// OutputString typemap above.
%typemap(default) int OutputStringLength {
    $1 = 128;
}

// Convert a result AT_WC array into a Python string.
%typemap(argout) AT_WC* OutputString {
    // Get number of bytes we have to write; wcslen just gives us the number
    // of characters, which is different.
    int len = wcstombs(NULL, $1, 0);
    // Unconvertable characters are indicated by wcstombs returning -1
    if (len == (size_t) -1) {
        PyErr_SetString(PyExc_ValueError, "Invalid character returned; couldn't convert to Python string");
        return NULL;
    }

    len++; // Make room for the terminator
    char* cBuffer = (char*) malloc(len * sizeof(char));
    wcstombs(cBuffer, $1, len);
    %append_output(PyString_FromString(cBuffer));
    free(cBuffer);
    free($1);
}


