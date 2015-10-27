/*
 * This program is intended to provide a pure-C "client" for interacting with
 * the camera, for use in debugging issues we've been having with running
 * long, high-speed acquisitions. It's basically a copy of the memhandler
 * code with some preambles and code to actually deal with the image data. 
 */

#include "atcore.h"
#include "memhandler.hh"

#include "stdio.h"
#include <fstream>
#include <iostream>
#include <list>
#include <boost/thread.hpp>
#include <windows.h>

/* Array of many images' worth of data. */
unsigned char* superBuffer = 0;
/* Number of bytes used by one image. */
unsigned int imageBytes = 0;
/* std::list of images waiting to be consumed. */
std::list<unsigned short*> imageList;
/* Mutex locking access to the above. */
boost::mutex listMutex;
/* Thread reading images out of the superBuffer */
boost::thread* readThread = NULL;
/* Boolean indicating if the reader thread should continue. */
int shouldReadImages = 0;


/* Clear the current array of memory and allocate a new one. Kill off the 
 * old image-retrieval thread. Empty the imageList. Spawn a new thread to 
 * replace the old one. We do this as the image size may have changed, which
 * makes the old readImages() function invalid.
 */
extern "C" {
int allocMemory(int handle, int numBuffers, int numElements) {
    int error;
    /* Halt any active read thread */
    if (readThread != NULL) {
        shouldReadImages = 0;
        /* Wait for the thread to exit. */
        readThread->join();
        free(readThread);
    }
    /* Wipe the list of images waiting to be read out. */
    listMutex.lock();
    imageList.clear();
    listMutex.unlock();
    
    /* Wipe the superBuffer, if it exists */
    if (superBuffer != 0) {
        /* The old buffer still exists; flush it. */
        error = AT_Flush(handle);
        free(superBuffer);
        if (error) {
            return error;
        }
    }
    /* Recreate the buffer */
    imageBytes = numElements;
    superBuffer = (unsigned char*) malloc(numBuffers * imageBytes * sizeof(unsigned char));

    /* Write zeros to each sub-buffer, and enqueue it. */
    for (int i = 0; i < numBuffers; ++i) {
        for (int j = 0; j < imageBytes; ++j) {
            superBuffer[i * imageBytes + j] = 0;
        }
        error = AT_QueueBuffer(handle, superBuffer + i * imageBytes, imageBytes);
        if (error) {
            return error;
        }
    }
    /* Start up a new reader thread. */
    shouldReadImages = 1;
    readThread = new boost::thread(&readImages, handle, imageBytes);
    return 0;
}
} // End extern "C"


/* Wraps around AT_WaitBuffer. Retrieve a buffer of image data from Andor,
 * then copy it to the provided buffer of shorts. The buffer from Andor
 * consists of either 11-bit or 16-bit pixels (in the 11-bit case, padded
 * to 12 bits with a 0). In the latter case we can just use memcpy and a
 * typecast, but in the former we have to do some annoying fiddling.
 * Once we've copied the data out to outputBuffer, we re-zero the buffer
 * that Andor wrote to, and then enqueue it so it can be re-used.
 */
int getUpdatedMemory(int handle, unsigned short* outputBuffer,
                     int timeout) {

    unsigned char* imageBuffer;
    int imageSize;
    int error = AT_WaitBuffer(handle, &imageBuffer, &imageSize, timeout);
    if (error) {
        return error;
    }

    int pixelEncoding;
    error = AT_GetEnumIndex(handle, L"PixelEncoding", &pixelEncoding);
    if (error) {
        return error;
    }

    if (pixelEncoding == 1) { // "Mono12Packed" encoding
        // Convert 12-bit pixels to 16-bit shorts. Actually, convert 11-bit
        // pixels that are stored in 12 bits. The packed "encoding" of
        // pixel data is really weird -- the byte that holds 4 bits each of
        // two different pixels always holds the *lowest* bits of pixel
        // data (i.e. you could extract every other byte and only introduce
        // error of up to 16 counts for each pixel).
        
        // top is the most significant 4 or 8 bits; bottom is the least
        // significant 8 or 4 bits.
        int i, curByte = 0, top, bottom;
        for (i = 0; curByte < imageBytes; ++i) {
            if (i % 2 == 0) {
                // Even offset, so our data is all of this byte and the
                // top half of the next byte.
                top = (imageBuffer[curByte]) << 4;
                bottom = (imageBuffer[curByte + 1]) >> 4;
                curByte += 1;
            }
            else {
                // Odd offset, so our data is the bottom half of this byte
                // and all of the next byte.
                bottom = imageBuffer[curByte] & 0x0f;
                top = (imageBuffer[curByte + 1]) << 4;
                curByte += 2;
            }
            // Truncate to 11 bits.
            top = top & 0x7ff;
            outputBuffer[i] = (short) (top + bottom);
        }
    }
    else {
        // Encoding is "Mono12" or "Mono16"; either way each pixel is
        // padded out to 2 bytes. We can just memcpy off each row.
        AT_64 stride, numPixels, numRows;
        error = AT_GetInt(handle, L"AOIStride", &stride);
        error = AT_GetInt(handle, L"AOIWidth", &numPixels);
        error = AT_GetInt(handle, L"AOIHeight", &numRows);
        for (int i = 0; i < numRows; ++i) {
            // outputBuffer is 16-bit shorts; imageBuffer is 8-bit chars
            memcpy(outputBuffer + i * numPixels, imageBuffer + i * stride,
                    numPixels * 2);
        }
    }

    // Re-zero the buffer we used, then enqueue it.
    for (int i = 0; i < imageBytes; ++i) {
        imageBuffer[i] = 0;
    }
    return AT_QueueBuffer(handle, imageBuffer, imageBytes);
}


// This function is intended to be created in a separate thread. It continually
// calls getUpdatedMemory and sticks the results (if any) into imageList.
void readImages(int handle, int imageBytes) {
    unsigned short* buffer = NULL;
    while (shouldReadImages) {
        if (buffer == NULL) {
            buffer = (unsigned short*) malloc(imageBytes);
        }
        if (!getUpdatedMemory(handle, buffer, 1)) {
            // We got a new image; store it.
            listMutex.lock();
            imageList.push_back(buffer);
            listMutex.unlock();
            buffer = NULL;
        }
        // Otherwise an error occurred; assume AT_WaitBuffer just timed out.
    }
}


/* This function consumes an image from imageList and returns it by
 * pointer. It blocks indefinitely, until an image is available.
 * It is assumed that the provided buffer is big enough to store
 * the image into. */
extern "C" {
int getImage(unsigned short* buffer, int imageBytes, double timeout) {
    int shouldStop = 0;
    int startTime = GetTickCount64(), curTime = 0;
    unsigned short* readoutBuffer;
    while (1) {
        if (!imageList.empty()) {
            // We have an image; retrieve it and process it.
            listMutex.lock();
            readoutBuffer = imageList.front();
            imageList.pop_front();
            listMutex.unlock();
            memcpy(buffer, readoutBuffer, imageBytes);
            free(readoutBuffer);
            return 0;
        }
        else {
            // Check for timeout.
            curTime = GetTickCount64();
            if (curTime - startTime > timeout) {
                // Timed out.
                return 123454321;
            }
            // No image available; sleep for a bit.
            Sleep(.001);
        }
    }
}
} // End extern "C"

