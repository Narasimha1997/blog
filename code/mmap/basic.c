#include<stdio.h>
#include<stdlib.h>

int main(int argc, char** argv) {
    FILE *fp = fopen("data.txt", "r");
    if (fp != NULL) {
        char* data = (char*)malloc(512);
        fread(data, 1, 512, fp);
        printf("%s", data);
    }
}