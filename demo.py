import subprocess
import random
import numpy as np

MPI_ROOT = "/users/profs/2017/francois.trahay/soft/install/openmpi/"

my_file_0 = {
    "name": "dna/chr1_KI270710v1_random.fa",
    "size": 41,
    "nickname": "small"
}

my_file_1 = {
    "name": "dna/chr6_GL000250v2_alt.fa",
    "size": 4800,
    "nickname": "medium"
}

my_file_2 = {
    "name": "dna/chrY.fa",
    "size": 58400,
    "nickname": "big"
}

my_file_3 = {
    "name": "dna/chr6.fa",
    "size": 174200,
    "nickname": "huge"
}


my_files = [
    my_file_0,
    my_file_1,
    my_file_2,
    my_file_3
    ]

run_commands = {
    "normal": "",
    "mpi_only": "mpicc -o apm_par_seq src/apm_par_seq.c",
    "mpi_openmp": "mpicc -fopenmp -o apm_omp src/apm_omp.c",
    "cuda_only": "/usr/local/cuda-9.0/bin/nvcc -o apm_cuda_only src/apm_cuda_only.cu",
    "patterns": "mpicc -o apm_par src/apm_par.c",
}

one_pattern = ["ATGCATGC"]
four_patterns = [
    "ATGCATGC",
    "ATTTGAAA",
    "AXXTGATT",
    "AGGTGAAA",
]


def get_time(ans):
    look_for = "APM done in "
    n = len(look_for)
    time = ""
    for i in range(len(ans)):
        if ans[i:i+n] == look_for:
            j = i + n
            while True:
                if ans[j] == " ":
                    break
                time += ans[j]
                j += 1
    return float(time)


def get_result(ans, pattern):
    look_for = "<\"" + pattern + "\">: "
    n = len(look_for)
    n_matches = ""
    for i in range(len(ans)):
        if ans[i:i+n] == look_for:
            j = i + n
            while True:
                if ans[j] == "\n":
                    break
                n_matches += ans[j]
                j += 1
    return int(n_matches)


def compile_everything():
    commands = {
        "normal": "gcc -o apm src/apm.c",
        "mpi_only": "mpicc -o apm_par_seq src/apm_par_seq.c",
        "mpi_openmp": "mpicc -fopenmp -o apm_omp src/apm_omp.c",
        "cuda_only": "/usr/local/cuda-9.0/bin/nvcc -o apm_cuda_only src/apm_cuda_only.cu",
        "patterns": "mpicc -o apm_par src/apm_par.c",
        "mpi_cuda": "/usr/local/cuda-9.0/bin/nvcc -I" + MPI_ROOT + "/include -L" + MPI_ROOT + "/lib -lmpi -o apm_mpi_cuda src/apm_mpi_cuda.cu",
    }

    for k, v in commands.items():
        print("compiling " + k)
        ans = subprocess.check_output(v.split(" ")).decode()
        if ans == "":
            print("compiling went ok")
        else:
            print("compiling fucked up")


def args(file, patterns, approx):
    command = str(approx) + " " + file
    for p in patterns:
        command += " \"" + p + "\""

    return command


def get_results(script, file_, patterns, N=1, n=4, approx=3):

    command = ""
    if script == "normal":
        command = "./apm "
    if script == "mpi_only":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_par_seq "
    if script == "mpi_openmp":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_omp "
    if script == "cuda_only":
        command = "./apm_cuda_only "
    if script == "mpi_cuda":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_mpi_cuda "
    if script == "patterns":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_par "

    command += args(file_, patterns, approx)
    command = command.split(" ")

    ans = subprocess.check_output(command).decode()
    results = [get_result(ans, p) for p in patterns]
    time = get_time(ans)

    return time, results

def test_big_thing():
    N=30
    n=30
    approx=3
    patterns=["ATTTTGC", "ATGCATTGC", "ATGCCGTTGC", "ACCCGATGAC", "ATGACCCCC", "TTTGCAC", "TTTTGCCATGC", "TGCAGACTGC", "TTC", "GCAAT", "AAAGCTGCAG", "AAAAAGTGGCCTGGCAGCCGTGGC"]
    time2, _= get_results("mpi_cuda", my_file_3["name"], patterns, N, n, approx)
    print("duration for MPI+CUDA apm:"+str(time2))

    time1, _= get_results("mpi_openmp", my_file_3["name"], patterns, N, n, approx)
    print("duration for MPI+OMP apm:"+str(time1))

    time0, _= get_results("normal", my_file_3["name"], patterns, N, n, approx)
    print("duration for normal apm:"+str(time0))

compile_everything()

#  Here you can put the path to the file you want to test
my_file = {
    "name": "dna/chr6_GL000250v2_alt.fa",
}

print("testing on my file: " + my_file["name"])
#  this is how you should do to run and print the results on the different C methods on your file:
for meth in ["normal", "patterns" "mpi_only", "mpi_openmp", "mpi_cuda"]:
    # put the patterns you are looking for here:
    pat = [
        "ATTGCC",
        "GCCCAA"
    ]
    N_ = 4
    n_ = 4
    approx_ = 3
    t, r  = get_results(meth, my_file, N_, n_, approx_)
    print("method " + meth + "did the job in " + str(r))
    print("result is: ")
    print(r)
    print("")

print("launching test on very big file, this could take a few seconds: ")
#  this is the code we ran during the presentation:
test_big_thing()
