/**
 * INF560 - TD2
 *
 * Part 3: Work Distribution
 * Static Work Distribution
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
    double t1, t2;
    t1 = MPI_Wtime();
    /* master process */
    int **tab = malloc(sizeof(int*) * m);
    int i, j;
    for(i=0; i<m; i++) {
      tab[i] = malloc(sizeof(int)*n);
      for(j=0; j<n; j++) {
	tab[i][j] = lrand48()%n;
      }
    }
    
    /* send the tasks */
    int task;
    int dest_rank;
    for(task=0; task <m; task++) {
      dest_rank = 1+(task%(size-1));
      MPI_Send(tab[task], n, MPI_INTEGER, dest_rank, 0, MPI_COMM_WORLD);
    }
    /* send a message that tell the workers to stop */
    for(dest_rank=1; dest_rank<size; dest_rank++) {
      int stop_value = -1;
      MPI_Send(&stop_value, 1, MPI_INTEGER, dest_rank, 0, MPI_COMM_WORLD);
    }

    /* recv the result */
    for(task=0; task <m; task++) {
      int max;
      dest_rank = 1+(task%(size-1));
      MPI_Recv(&max, 1, MPI_INTEGER, dest_rank, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      printf("max[%d] = %d\n", task, max);
    }

    t2 = MPI_Wtime();
    printf("computation took %f s\n", t2-t1);

  } else {
    /* slave process */
    int *local_tab = malloc(sizeof(int)*n);

    while(1) {
      /* receive a task */
      MPI_Recv(local_tab, n, MPI_INTEGER, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      if(local_tab[0] < 0) {
	/* no more task */
	break;
      }

      /* process the task */
      int i;
      int max=local_tab[0];
      for(i=0; i<n; i++) {
	if(local_tab[i] > max) {
	  max = local_tab[i];
	}
      }
      /* send the result */
      MPI_Send(&max, 1, MPI_INTEGER, 0, 0, MPI_COMM_WORLD);
    }
  }

  MPI_Finalize();
  return 0;
}
