#ifndef MEMHANDLER_H
#define MEMHANDLER_H

extern "C" {
__declspec(dllexport) int allocMemory(int handle, int numBuffers, int numElements);
__declspec(dllexport) int getImage(unsigned short* buffer, int imageBytes, double timeout);
}

int getUpdatedMemory(int handle, unsigned short* outputBuffer,
        int timeout);
void readImages(int handle, int imageBytes);

#endif
