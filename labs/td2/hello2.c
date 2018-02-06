#include <mpi.h>
#include <stdio.h>

int main(int argc, char**argv) {
  int rank, size;
  int ready = 0;

  MPI_Init(&argc, &argv);

  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);


  if(rank>0) {
    MPI_Send(&ready, 1, MPI_INTEGER, 0, 0, MPI_COMM_WORLD);
  } else {
    MPI_Status status;
    int i;
    for(i=1; i<size; i++) {
      MPI_Recv(&ready, 1, MPI_INTEGER, i, 0, MPI_COMM_WORLD, &status);
    }
    fprintf(stderr, "Hello world with %d ready tasks\n", size);
  }

  MPI_Finalize();
  return 0;
}
