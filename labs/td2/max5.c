/**
 * INF560 - TD2
 *
 * Part 3: Work Distribution
 * Dynamic Work Distribution
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

  if( rank==0 ) {
    /* master process */
    int **tab = malloc(sizeof(int*) * m);
    int *max_values = malloc(sizeof(int)*n);
    MPI_Request *req = malloc(sizeof(MPI_Request)*n);
    int i, j;
    for(i=0; i<m; i++) {
      tab[i] = malloc(sizeof(int)*n);
      for(j=0; j<n; j++) {
	tab[i][j] = lrand48()%n;
      }
    }

    double t1, t2;
    t1 = MPI_Wtime();
    
    /* send the tasks */
    int task;
    int dest_rank;

    for(task=0; task <m; task++) {
      int ready;
      MPI_Recv(&ready, 1, MPI_INTEGER, MPI_ANY_SOURCE, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      dest_rank = ready;
      MPI_Irecv(&max_values[task], 1, MPI_INTEGER, dest_rank, 0, MPI_COMM_WORLD, &req[task]);
#if DEBUG
      fprintf(stderr, "Sending task %d to %d\n", task, dest_rank);
#endif
      MPI_Send(tab[task], n, MPI_INTEGER, dest_rank, 0, MPI_COMM_WORLD);
    }

    /* send a message that tell the workers to stop */
    for(dest_rank=1; dest_rank<size; dest_rank++) {
      int ready;
      MPI_Recv(&ready, 1, MPI_INTEGER, dest_rank, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

      int stop_value = -1;
      MPI_Send(&stop_value, 1, MPI_INTEGER, dest_rank, 0, MPI_COMM_WORLD);
    }

    /* wait until all the results are received */
    MPI_Waitall(m, req, MPI_STATUSES_IGNORE);

    t2 = MPI_Wtime();
    printf("computation took %f s\n", t2-t1);

  } else {
    /* slave process */
    int *local_tab = malloc(sizeof(int)*n);

    while(1) {
      MPI_Send(&rank, 1, MPI_INTEGER, 0, 1, MPI_COMM_WORLD);
      MPI_Recv(local_tab, n, MPI_INTEGER, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      if(local_tab[0] < 0) {
	fprintf(stderr, "End of rank %d\n", rank);
	break;
      }

      int i;
      int max=local_tab[0];
      for(i=0; i<n; i++) {
	if(local_tab[i] > max) {
	  max = local_tab[i];
	}
      }

      MPI_Send(&max, 1, MPI_INTEGER, 0, 0, MPI_COMM_WORLD);
    }
  }

  MPI_Finalize();
  return 0;
}
