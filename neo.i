// SWIG interface file for the Andor SDK3.

%include cstring.i
%include exception.i
%include pythonWideChar.i
//%include windows.i
%include typemaps.i

%{
#define SWIG_FILE_WITH_INIT
%}
%include numpy.i
%init %{
import_array();
%}

%module neo
%{
#include "atcore.h"
%}

#define AT_HANDLE_SYSTEM 1

#define AT_ERR_NOTINITIALISED 1
#define AT_ERR_NOTIMPLEMENTED 2
#define AT_ERR_READONLY 3
#define AT_ERR_NOTREADABLE 4
#define AT_ERR_NOTWRITABLE 5
#define AT_ERR_OUTOFRANGE 6
#define AT_ERR_INDEXNOTAVAILABLE 7
#define AT_ERR_INDEXNOTIMPLEMENTED 8
#define AT_ERR_EXCEEDEDMAXSTRINGLENGTH 9
#define AT_ERR_CONNECTION 10
#define AT_ERR_NODATA 11
#define AT_ERR_INVALIDHANDLE 12
#define AT_ERR_TIMEDOUT 13
#define AT_ERR_BUFFERFULL 14
#define AT_ERR_INVALIDSIZE 15
#define AT_ERR_INVALIDALIGNMENT 16
#define AT_ERR_COMM 17
#define AT_ERR_STRINGNOTAVAILABLE 18
#define AT_ERR_STRINGNOTIMPLEMENTED 19

#define AT_ERR_NULL_FEATURE 20
#define AT_ERR_NULL_HANDLE 21
#define AT_ERR_NULL_IMPLEMENTED_VAR 22
#define AT_ERR_NULL_READABLE_VAR 23
#define AT_ERR_NULL_READONLY_VAR 24
#define AT_ERR_NULL_WRITABLE_VAR 25
#define AT_ERR_NULL_MINVALUE 26
#define AT_ERR_NULL_MAXVALUE 27
#define AT_ERR_NULL_VALUE 28
#define AT_ERR_NULL_STRING 29
#define AT_ERR_NULL_COUNT_VAR 30
#define AT_ERR_NULL_ISAVAILABLE_VAR 31
#define AT_ERR_NULL_MAXSTRINGLENGTH 32
#define AT_ERR_NULL_EVCALLBACK 33
#define AT_ERR_NULL_QUEUE_PTR 34
#define AT_ERR_NULL_WAIT_PTR 35
#define AT_ERR_NULL_PTRSIZE 36
#define AT_ERR_NOMEMORY 37

#define AT_ERR_HARDWARE_OVERFLOW 100


%apply int* OUTPUT {AT_BOOL* OUTPUT};
%apply int* OUTPUT {AT_H* OUTPUT};
%apply int {AT_H, AT_BOOL};
%apply unsigned char {AT_U8};
%apply wchar_t {AT_WC};
%apply wchar_t* {AT_WC*};
%apply unsigned char* {AT_U8*};

%apply (unsigned char* IN_ARRAY1, int DIM1) {(unsigned char* InputArray, int ArraySize)};
%apply (unsigned char* ARGOUT_ARRAY1, int DIM1) {(unsigned char* OutputArray, int OutputArraySize)};

int AT_InitialiseLibrary(); 
int AT_FinaliseLibrary(); 
 
int AT_Open(int DeviceIndex, AT_H* OUTPUT); 
int AT_Close(AT_H Hndl); 
 
int AT_IsImplemented(AT_H Hndl, AT_WC* InputString, AT_BOOL* OUTPUT); 
int AT_IsReadOnly(AT_H Hndl, AT_WC* InputString, AT_BOOL* OUTPUT); 
int AT_IsReadable(AT_H Hndl, AT_WC* InputString, AT_BOOL* OUTPUT); 
int AT_IsWritable(AT_H Hndl, AT_WC* InputString, AT_BOOL* OUTPUT); 
 
int AT_SetInt(AT_H Hndl, AT_WC* InputString, long long Value); 
int AT_GetInt(AT_H Hndl, AT_WC* InputString, long long* OUTPUT); 
int AT_GetIntMax(AT_H Hndl, AT_WC* InputString, long long* OUTPUT); 
int AT_GetIntMin(AT_H Hndl, AT_WC* InputString, long long* OUTPUT); 
 
int AT_SetFloat(AT_H Hndl, AT_WC* InputString, double Value); 
int AT_GetFloat(AT_H Hndl, AT_WC* InputString, double* OUTPUT); 
int AT_GetFloatMax(AT_H Hndl, AT_WC* InputString, double* OUTPUT); 
int AT_GetFloatMin(AT_H Hndl, AT_WC* InputString, double* OUTPUT); 
 
int AT_SetBool(AT_H Hndl, AT_WC* InputString, AT_BOOL Value); 
int AT_GetBool(AT_H Hndl, AT_WC* InputString, AT_BOOL* OUTPUT); 
 
int AT_SetEnumIndex(AT_H Hndl, AT_WC* InputString, int Value); 
int AT_SetEnumString(AT_H Hndl, AT_WC* InputString, AT_WC* InputString); 
int AT_GetEnumIndex(AT_H Hndl, AT_WC* InputString, int* OUTPUT); 
int AT_GetEnumCount(AT_H Hndl, AT_WC* InputString, int* OUTPUT); 
int AT_IsEnumIndexAvailable(AT_H Hndl, AT_WC* InputString, int Index, AT_BOOL* OUTPUT); 
int AT_IsEnumIndexImplemented(AT_H Hndl, AT_WC* InputString, int Index, AT_BOOL* OUTPUT);


int AT_GetEnumStringByIndex(AT_H Hndl, AT_WC* InputString, int Index, AT_WC* OutputString, int OutputStringLength); 
 
int AT_Command(AT_H Hndl, AT_WC* InputString); 
 
int AT_SetString(AT_H Hndl, AT_WC* InputString, AT_WC* InputString);
int AT_GetString(AT_H Hndl, AT_WC* InputString, AT_WC* OutputString, int OutputStringLength); 

int AT_GetStringMaxLength(AT_H Hndl, AT_WC* InputString, int* OUTPUT); 
 
int AT_QueueBuffer(AT_H Hndl, unsigned char* InputArray, int ArraySize); 
int AT_WaitBuffer(AT_H Hndl, AT_U8** OutputArray, int* ArraySize, unsigned int Timeout); 
int AT_Flush(AT_H Hndl); 

