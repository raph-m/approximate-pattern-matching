/**
 * INF560 - TD3
 *
 * Part 1: Collectives
 * One-to-All
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <mpi.h>

void print_buffer(int* buffer, int size) {
  int i;
  int rank ;

  MPI_Comm_rank( MPI_COMM_WORLD, &rank ) ;

  printf( "R%.2d: ", rank ) ;
  for(i=0; i<size; i++) {
    printf("%d ", buffer[i]);
  }
  printf("\n");
}

int MPI_my_bcast( void *buffer,
	       int count,
	       MPI_Datatype datatype,
	       int root,
               MPI_Comm comm ) {

  int type_size ;
  int buffer_size ;
  void* array ;
  int nb_procs;
  int my_rank;
  int round_size ;
  int remaining_bytes ;
  int i ;

  /* Get the size of the input data type */
  MPI_Type_size(datatype, &type_size);

  /* Compute the size (in bytes) of the input buffer */
  buffer_size = count*type_size ;

  /* Allocate a new buffer with twice the previous size */
  array = malloc(2*buffer_size);

  /* Copy the input buffer into this new array (twice in a row) */
  memcpy(array, buffer, buffer_size);
  memcpy(&((uint8_t*)array)[buffer_size], buffer, buffer_size);

  /* Get the total number of MPI tasks and the corresponding rank */
  MPI_Comm_size(comm, &nb_procs);
  MPI_Comm_rank(comm, &my_rank);

  for ( i = 0 ; i < count ; i++ )
  {
	  int index_root ;
	  int index ;

	  index_root = i * type_size ;
	  index = ( (i + my_rank)%count ) * type_size ;

	  MPI_Scatter( &(((uint8_t *)array)[index_root]), 1, datatype,
			  &(((uint8_t *)buffer)[index]), 1, datatype,
			  root, comm ) ;

  }

  return MPI_SUCCESS ;
}

int main(int argc, char**argv) {
  int my_rank;
  int comm_size;
  int buffer_size ;
  int * buffer ;
  int i ;
  int seed ;
  int root ;

  /* Initialization of MPI */
  MPI_Init(&argc, &argv);

  if ( argc < 4 ) 
  {
	  printf( "Usage: %s seed size_array root\n",
			  argv[0] ) ;
	  MPI_Abort( MPI_COMM_WORLD, 1 ) ;
  }

  /* Parse input arguments */
  seed = atoi(argv[1]);
  buffer_size = atoi(argv[2]);
  root = atoi( argv[3] ) ;

  /* Initialize seed */
  srand48(seed);

  /* Get the rank and size of main communicator */
  MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
  MPI_Comm_size(MPI_COMM_WORLD, &comm_size);


  /* Check the root value */
  if ( root < 0 || root >= comm_size ) 
  {
	  printf( "Error: Unable to have root %d\n", root ) ;
	  MPI_Abort( MPI_COMM_WORLD, 1 ) ;
  }

  /* Allocate the buffer */
  buffer = (int *)malloc( buffer_size * sizeof( int ) ) ;
  if ( buffer == NULL ) {
	  fprintf( stderr, "Unable to allocate buffer of %d element(s) on rank %d\n",
			  buffer_size, my_rank ) ;
	  MPI_Abort( MPI_COMM_WORLD, 1 ) ;
  }

  /* Fill the buffer for the root (random) and others (0) */
  if(my_rank==root) {
    for(i=0; i<buffer_size; i++) {
      buffer[i] = lrand48() % 100;
    }

	printf( "Running my_bast on %d element(s) with seed %d\n", buffer_size, seed ) ;
  } else
  {
	  for(i=0; i<buffer_size; i++) {
		  buffer[i] = 0 ;
	  }
  }

  MPI_my_bcast(buffer, buffer_size, MPI_INTEGER, root, MPI_COMM_WORLD);

  /* Debugging part to print the buffer 
   * on each rank with synchronization between
   * printing
   */
  for(i=0; i<comm_size; i++) {
    MPI_Barrier(MPI_COMM_WORLD);
    if(my_rank == i ){
      print_buffer(buffer, buffer_size);
      fflush(stdout);
    }
  }

  MPI_Finalize();

  return EXIT_SUCCESS;
}
