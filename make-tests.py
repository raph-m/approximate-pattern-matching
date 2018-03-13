import subprocess

def compile_everything():
    commands = {
        "normal": "gcc -o apm src/apm.c",
        "mpi_only": "mpicc -o apm_par_seq src/apm_par_seq.c",
        "mpi and openMP": "mpicc -fopenmp -o apm_omp src/apm_omp.c",
        "cuda only": "/usr/local/cuda-9.0/bin/nvcc -o apm_cuda_only src/apm_cuda_only.cu"
    }

    for k, v in commands.items():
        ans = subprocess.check_output(v.split(" ")).decode()


a = subprocess.check_output(['git', 'status']).decode()
print(a)
compile_everything()
