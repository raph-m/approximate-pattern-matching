/**
 *  * APPROXIMATE PATTERN MATCHING
 *   *
 *    * INF560 X2016
 *     */
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/time.h>

#define APM_DEBUG 0

#define gpuErrchk(ans) { gpuAssert((ans), __FILE__, __LINE__); }
inline void gpuAssert(cudaError_t code, const char *file, int line, bool abort=true)
{
   if (code != cudaSuccess) 
   {
      fprintf(stderr,"GPUassert: %s %s %d\n", cudaGetErrorString(code), file, line);
      if (abort) exit(code);
   }
}

char *read_input_file(char * filename, int * size) {
    char * buf ;
    off_t fsize;
    int fd = 0 ;
    int n_bytes = 1 ;

    /* Open the text file */
    fd = open(filename, O_RDONLY);
    if (fd == -1) {
        fprintf(stderr, "Unable to open the text file <%s>\n", filename);
        return NULL;
    }

    /* Get the number of characters in the textfile */
    fsize = lseek(fd, 0, SEEK_END);
    lseek(fd, 0, SEEK_SET);

    /* TODO check return of lseek */

#if APM_DEBUG
    printf( "File length: %lld\n", fsize ) ;
#endif

    /* Allocate data to copy the target text */
    buf = (char *)malloc( fsize * sizeof ( char ) ) ;
    if (buf == NULL) {
        fprintf(stderr,
                "Unable to allocate %lld byte(s) for main array\n",
                fsize);
        return NULL;
    }

    n_bytes = read(fd, buf, fsize);
    if (n_bytes != fsize) {
        fprintf(stderr,
                "Unable to copy %lld byte(s) from text file (%d byte(s) copied)\n",
                fsize, n_bytes) ;
        return NULL ;
    }

#if APM_DEBUG
    printf( "Number of read bytes: %d\n", n_bytes ) ;
#endif

    *size = n_bytes ;

    close(fd);

    return buf;
}


#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)))

__global__
void cuda_levenshtein(char *s1, char *s2, int len, int * result, int n_max) {
    unsigned int x, y, lastdiag, olddiag;

    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i<n_max){
        int column[100];
        for (y = 1; y <= len; y++) {
            column[y] = y;
        }

        for (x = 1; x <= len; x++) {

            column[0] = x;
            lastdiag = x-1 ;

            for (y = 1; y <= len; y++) {
                olddiag = column[y];
                column[y] = MIN3(
                        column[y] + 1,
                        column[y-1] + 1,
                        lastdiag + (s1[y-1+i] == s2[x-1] ? 0 : 1)
                );
                lastdiag = olddiag;
            }
        }
        result[i] = column[len];
    }
}




int levenshtein(char *s1, char *s2, int len, int * column) {
    unsigned int x, y, lastdiag, olddiag;

    for (y = 1; y <= len; y++) {
        column[y] = y;
    }

    for (x = 1; x <= len; x++) {

        column[0] = x;
        lastdiag = x-1 ;

        for (y = 1; y <= len; y++) {
            olddiag = column[y];
            column[y] = MIN3(
                    column[y] + 1,
                    column[y-1] + 1,
                    lastdiag + (s1[y-1] == s2[x-1] ? 0 : 1)
            );
            lastdiag = olddiag;
        }
    }
    return(column[len]);
}


int main(int argc, char ** argv) {
    char ** pattern ;
    int * scounts;
    int * displs;
    int step;
    char * filename ;
    int approx_factor = 0 ;
    int nb_patterns = 0 ;
    int i, j ;
    char * buf ;
    struct timeval t1, t2;
    double duration ;
    int * n_matches ;
    int n_bytes ;
    int rank;
    int size;

    int max_pat;

    int chunk_size;

    /* Check number of arguments */
    if (argc < 4) {

        printf("Usage: %s approximation_factor "
                       "dna_database pattern1 pattern2 ...\n",
               argv[0]);
        return 1;
    }
    n_bytes=0;
    /* Get the distance factor */
    approx_factor = atoi(argv[1]);

    /* Grab the filename containing the target text */
    filename = argv[2];

    /* Get the number of patterns that the user wants to search for */
    nb_patterns = argc - 3;

    /* Fill the pattern array */
    pattern = (char **)malloc( nb_patterns * sizeof( char * ) ) ;

    if (pattern == NULL) {
        fprintf(
                stderr,
                "Unable to allocate array of pattern of size %d\n",
                nb_patterns
        );
        return 1 ;
    }

    /* Grab the patterns */
    for (i = 0 ; i < nb_patterns ; i++) {
        int l ;
        l = strlen(argv[i+3]) ;

        if (l <= 0) {
            fprintf( stderr, "Error while parsing argument %d\n", i+3 ) ;
            return 1 ;
        }

        pattern[i] = (char *)malloc( (l+1) * sizeof( char ) ) ;

        if (pattern[i] == NULL) {
            fprintf( stderr, "Unable to allocate string of size %d\n", l ) ;
            return 1 ;
        }

        strncpy( pattern[i], argv[i+3], (l+1) ) ;
    }
    printf( "Approximate Pattern Mathing: "
                    "looking for %d pattern(s) in file %s w/ distance of %d\n",
            nb_patterns, filename, approx_factor );

    buf = read_input_file( filename, &n_bytes ) ;
    if ( buf == NULL ) {
        return 1 ;
    }

    /* Allocate the array of matches */
    n_matches = (int *)malloc( nb_patterns * sizeof( int ) ) ;
    if (n_matches == NULL) {
        fprintf(
                stderr,
                "Error: unable to allocate memory for %ldB\n",
                nb_patterns * sizeof( int )
        );
        return 1 ;
    }
    /*****
   *    * BEGIN MAIN LOOP
   *       ******/

    /* Timer start */
    gettimeofday(&t1, NULL);
    max_pat=0;
    for(i=0; i<nb_patterns; i++){
        max_pat=max_pat>strlen(pattern[i]) ? max_pat : strlen(pattern[i]);
    }
	printf("hello %d\n", n_bytes);
    for ( i = 0 ; i < nb_patterns ; i++ ) {
        int size_pattern = strlen(pattern[i]) ;
		printf("hello\n");
        n_matches[i] = 0 ;

        char * d_rcv_buf;
        char * d_pattern;
        int * d_result;
        int n_max = (n_bytes-size_pattern + 1);
        int result[n_max];
		cudaMalloc((void **)&d_rcv_buf, n_bytes*sizeof(char));
        cudaMalloc((void **)&d_pattern, size_pattern*sizeof(char));
        cudaMalloc((void **)&d_result, n_max*sizeof(int));

        cudaMemcpy(d_rcv_buf, buf, n_bytes*sizeof(char), cudaMemcpyHostToDevice);
        cudaMemcpy(d_pattern, pattern[i], size_pattern*sizeof(char), cudaMemcpyHostToDevice);
        // à corriger
        cuda_levenshtein<<<1, 1024>>>(d_rcv_buf, d_pattern, size_pattern, d_result, n_max);
		gpuErrchk( cudaPeekAtLastError() );
		gpuErrchk( cudaDeviceSynchronize() );
        gpuErrchk(cudaMemcpy(result, d_result, n_max*sizeof(int), cudaMemcpyDeviceToHost));
		cudaFree(d_rcv_buf);
		cudaFree(d_pattern);
		cudaFree(d_result);
		printf("hello %d \n", result[0]);
		int * column;
	    column=(int *) malloc((size_pattern+1)*sizeof(int));
        for ( j = 0 ; j < n_bytes ; j++ ) {
            int distance = 0 ;
            int s ;

#if APM_DEBUG
            if ( j % 100 == 0 )
            {
            printf( "Procesing byte %d (out of %d)\n", j, n_bytes ) ;
            }
#endif
	    
            s = size_pattern ;
            if ( n_bytes - j < size_pattern )
            {
                s = n_bytes - j ;
                distance = levenshtein( pattern[i], &buf[j], s, column )+size_pattern-s;
            }
            else{
                distance = result[j];
            }

            if ( distance <= approx_factor ) {
                n_matches[i]++ ;
            }
        }
        printf("%d matches from %d\n", n_matches[0], rank);
        free( column );
    }

    /* Timer stop */
    gettimeofday(&t2, NULL);

    duration = (t2.tv_sec -t1.tv_sec)+((t2.tv_usec-t1.tv_usec)/1e6);

    printf( "APM done in %lf s\n", duration ) ;

    /*****
    *    * END MAIN LOOP
    *       ******/

    for ( i = 0 ; i < nb_patterns ; i++ )
    {
        printf( "Number of matches for pattern <%s>: %d\n",
                pattern[i], n_matches[i] ) ;
    }
    return 0 ;
}