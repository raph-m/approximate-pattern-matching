/**
 * INF560 - TD3
 *
 * Part 1: Collectives
 * All-to-One and All-to-All
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

int MPI_My_allreduce(const void *sendbuf, void *recvbuf, int count,
		     MPI_Datatype datatype, MPI_Op op, MPI_Comm comm) {

  /* rank 0 performs the reduction */
  int err = MPI_Reduce(sendbuf, recvbuf, count, datatype, op, 0, comm);
  if(err != MPI_SUCCESS)
    return err;

  /* broadcast the result */
  err = MPI_Bcast(recvbuf, count, datatype, 0, comm );
  return err;
}

int main(int argc, char**argv) {
  MPI_Init(&argc, &argv);
  int my_rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

  int result;
  MPI_My_allreduce(&my_rank, &result, 1, MPI_INTEGER, MPI_MIN, MPI_COMM_WORLD);

  printf("[%d] result = %d\n", my_rank, result);
  MPI_Finalize();
  return EXIT_SUCCESS;
}
