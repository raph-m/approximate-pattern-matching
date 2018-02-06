/**
 * INF560 - TD2
 *
 * Part 3: Work Distribution
 * Max on Multiple Arrays
 */
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char**argv) {

  MPI_Init(&argc, &argv);

  int rank, size;
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  if(argc < 4) {
    printf("usage: %s S N m\n", argv[0]);
    return 0;
  }

  int s = atoi(argv[1]);
  int n = atoi(argv[2]);
  int m = atoi(argv[3]);
  srand48(s);

  /* allocate an array of array and initialize it */
  int **tab = malloc(sizeof(int*) * m);
  int i, j;
  for(i=0; i<m; i++) {
    tab[i] = malloc(sizeof(int)*n);
    for(j=0; j<n; j++) {
      tab[i][j] = lrand48()%n;
    }
  }

  int chunk_size = n/size;
  if ( n % size != 0 ) chunk_size++ ;
  int lower_bound = chunk_size*rank;
  int upper_bound = chunk_size*(rank+1);
  if(upper_bound>n) {
    upper_bound = n;
  }

  double t1, t2;
  /* start measurement */
  t1 = MPI_Wtime();

  int task;
  for(task=0; task <m; task++) {
    int max=tab[task][0];

    for(i=lower_bound; i<upper_bound; i++) {
      if(tab[task][i] > max) {
	max = tab[task][i];
      }
    }
 
    if(rank>0) {
    /* send the local max to rank 0 */
      MPI_Send(&max, 1, MPI_INTEGER, 0, 0, MPI_COMM_WORLD);
    } else {
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
#if DEBUG
      printf("\nmax[%d]=%d\n", task, max);
#endif
    }
  }
  /* stop the measurement */
  t2 = MPI_Wtime();

  printf("(Rank %d) Computation time: %f s\n", rank, t2-t1);

  MPI_Finalize();
  return 0;
}
