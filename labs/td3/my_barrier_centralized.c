/**
 * INF560 - TD3
 *
 * Part 1: Collectives
 * Collective Implementation
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <mpi.h>

int MPI_My_barrier(MPI_Comm comm) {
  int my_rank;
  MPI_Comm_rank(comm, &my_rank);

  if(my_rank > 0) {
    int ready=1;
    MPI_Send(&ready, 1, MPI_INTEGER, 0, 0, comm);
    MPI_Recv(&ready, 1, MPI_INTEGER, 0, 0, comm, MPI_STATUS_IGNORE);
  } else {
    int i;
    int ready;
    int comm_size;
    MPI_Comm_size(comm, &comm_size);

    /* wait until all the process are ready */
    for(i=1; i<comm_size; i++) {
      MPI_Recv(&ready, 1, MPI_INTEGER, i, 0, comm, MPI_STATUS_IGNORE);
    }

    /* notify all the process */
    for(i=1; i<comm_size; i++) {
      MPI_Send(&ready, 1, MPI_INTEGER, i, 0, comm);
    }
  }

  return MPI_SUCCESS;
}

int main(int argc, char**argv) {
  MPI_Init(&argc, &argv);
  int my_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

  int i;
  for(i=0; i<10; i++) {
    MPI_My_barrier(MPI_COMM_WORLD);
    printf("[%d] barrier %d\n", my_rank, i);
    usleep(my_rank*100000);
  }

  MPI_Finalize();
  return EXIT_SUCCESS;
}
