#include <mpi.h>
#include <stdio.h>

int main(int argc, char**argv) {
  int rank, size;
  char hostname[1024];

  MPI_Init(&argc, &argv);

  /* Grab the rank of the current MPI task */
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);

  /* Grab the total number of MPI tasks */
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  /* Get the hostname */
  gethostname(hostname, 1024);

  printf("Hello World from task %d out of %d on %s\n", rank, size, hostname);

  MPI_Finalize();
  return 0;
}
