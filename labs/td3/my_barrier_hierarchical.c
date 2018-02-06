#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <mpi.h>

int MPI_My_barrier(MPI_Comm comm) {
  int my_rank;
  MPI_Comm_rank(comm, &my_rank);
  int comm_size;
  MPI_Comm_size(comm, &comm_size);

  int offset;
  int round;
  int ready;
  int nb_round=0;
  for(nb_round=0; (1<<nb_round)<comm_size; nb_round++) { }

  /* notify rank 0 */
  for(round=nb_round; round >= 0; round--) {
    int offset = 1<<round;
    if(my_rank+1 >> round == 1) {
      if(my_rank+offset < comm_size)
	MPI_Recv(&ready, 1, MPI_INTEGER, my_rank+offset, 0, comm, MPI_STATUS_IGNORE);
      if(my_rank+(2*offset) < comm_size)
	MPI_Recv(&ready, 1, MPI_INTEGER, my_rank+(2*offset), 0, comm, MPI_STATUS_IGNORE);
    } else if(my_rank+1 >> (round+1) == 1) {
      if(((my_rank+1) & (1<<round))==0) {
	MPI_Send(&ready, 1, MPI_INTEGER, my_rank-offset, 0, comm);
      } else {
	MPI_Send(&ready, 1, MPI_INTEGER, my_rank-(2*offset), 0, comm);
      }
    }
  }

  /* everyone is ready */

  /* notify all the processes */
  for(round=0;(1<<round)< comm_size; round++) {
    int offset = 1<<round;
    if(my_rank+1 >> round == 1) {
      if(my_rank+offset < comm_size)
	MPI_Send(&ready, 1, MPI_INTEGER, my_rank+offset, 0, comm);
      if(my_rank+(2*offset) < comm_size)
	MPI_Send(&ready, 1, MPI_INTEGER, my_rank+(2*offset), 0, comm);
    } else if(my_rank+1 >> (round+1) == 1) {
      if(((my_rank+1) & (1<<round))==0) {
	MPI_Recv(&ready, 1, MPI_INTEGER, my_rank-offset, 0, comm, MPI_STATUS_IGNORE);
      } else {
	MPI_Recv(&ready, 1, MPI_INTEGER, my_rank-(2*offset), 0, comm, MPI_STATUS_IGNORE);
      }
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
    fflush(stdout);
    usleep(my_rank*1000000);
  }

  MPI_Finalize();
  return EXIT_SUCCESS;
}
