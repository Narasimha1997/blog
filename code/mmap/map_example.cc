#include <stdio.h>
#include <sys/mman.h>
#include <fcntl.h>

int main(int argc, char **argv) {
    int fd = open("data.txt", 0);
    // we only map first 512 bytes
    const char* file_ptr = (const char*)mmap(NULL, 1000, PROT_READ, MAP_PRIVATE, fd, 0);
    if (file_ptr != NULL) {
        printf("%s\n", file_ptr);
    }
}