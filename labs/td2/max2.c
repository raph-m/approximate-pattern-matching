/**
 * INF560 - TD2
 *
 * Part 2: Work Decomposition
 * Parallel Max
 */
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char**argv) {
  int rank, size;
  int s, n ;
  int * tab ;
  int i;
  double t1, t2;
  int max ;
  int chunk_size ;
  int lower_bound ;
  int upper_bound ;

  /* MPI Initialization */
  MPI_Init(&argc, &argv);

  /* Get the rank of the current task and the number
   * of MPI processe
   */
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  /* Check the input arguments */
  if(argc <3) {
    printf("usage: %s S N\n", argv[0]);
    return 0;
  }

  s = atoi(argv[1]);
  n = atoi(argv[2]);
  srand48(s);

  /* Allocate the array */
  tab = (int *)malloc(sizeof(int) * n);
  if ( tab == NULL ) { 
	  fprintf( stderr, "Unable to allocate %d elements\n", n ) ;
	  return 1 ; 
  }

  /* Initialize the array */
  for(i=0; i<n; i++) {
    tab[i] = lrand48()%n;
  }

  /* start the measurement */
  t1=MPI_Wtime();

  /* Compute the number of elements to traverse per task */
  chunk_size = n/size;
  if ( n % size != 0 ) chunk_size++ ;

  /* Deduce the indices inside the global array */
  lower_bound = chunk_size*rank;
  upper_bound = chunk_size*(rank+1);
  if(upper_bound>n) {
    upper_bound = n;
  }

#if DEBUG
  printf("%d: from %d to %d (cs=%d)\n", 
		  rank, lower_bound, upper_bound, chunk_size );
#endif	/* DEBUG */

  max = tab[0] ;
  for(i=lower_bound; i<upper_bound; i++) {
    if(tab[i] > max) {
      max = tab[i];
    }
  }

#if DEBUG
  printf("the array contains:\n");
  for(i=0; i<n; i++) {
    printf("%d  ", tab[i]);
  }
  printf("\n");
#endif

  if(rank > 0) {
    /* send the local max to rank 0 */
    MPI_Send(&max, 1, MPI_INTEGER, 0, 0, MPI_COMM_WORLD);
  } else {
    /* rank 0 */
    int max_remote;
#if DEBUG
    printf("0: my max=%d\n", max);
#endif
    /* receive the max value from all the ranks */
    for(i=1; i<size; i++) {
      MPI_Recv(&max_remote, 1, MPI_INTEGER, i, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      if(max_remote>max) {
#if DEBUG
	printf("New max (%d) found by %d\n", max_remote, i);
#endif
	max = max_remote;
      }
    }
  }

  /* stop the measurement */
  t2=MPI_Wtime();

  printf("(Rank %d) Computation time: %f s\n", rank, t2-t1);
  if ( rank == 0 ) {
	  printf("\nFinal Max value: %d\n", max);
  }

  MPI_Finalize();
  return 0;
}
