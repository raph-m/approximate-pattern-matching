import subprocess
import matplotlib.pyplot as plt
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


def compare_cuda_normal():
    sizes = []
    time_normal = []
    time_cuda = []
    patterns = ["AAAAA", "GGGGG"]
    for file in my_files:
        sizes.append(file["size"])
        time, results_normal = get_results("normal", file["name"], patterns)
        time_normal.append(time)
        time, results_cuda = get_results("cuda", file["name"], patterns)
        time_cuda.append(time)
        assert results_cuda == results_normal

    plt.scatter(sizes, time_normal, label="normal")
    plt.scatter(sizes, time_cuda, label="cuda")
    plt.plot()
    plt.show()


def pattern_parallelism(N=1, n=4, approx=3):
    alphabet = ['A', 'G', 'C', 'T']
    n_inf = 25
    patterns = []
    for i in range(n_inf):
        x = random.randint(2, 7)
        current = "".join(np.random.choice(alphabet, x, replace=True))
        patterns.append(current)

    lens = [len(p) for p in patterns]
    indexes = np.argsort(lens)
    indexes = indexes[::-1]
    patterns2 = np.array(patterns)
    patterns2 = patterns2[indexes]

    speedups = []
    for i in range(1, n_inf):
        print("i:")
        print(i)
        print("current patterns:")
        print(patterns2[:i])
        time0, _ = get_results("patterns", my_file_1["name"], patterns2[:i], N, n, approx)
        time1, _ = get_results("normal", my_file_1["name"], patterns2[:i], N, n, approx)
        print("time0")
        print(time0)
        print("time1")
        print(time1)
        speedups.append(time1/time0)

    plt.plot(range(1, n_inf), speedups)
    plt.plot(range(1, n_inf), np.ones(n_inf-1))
    plt.plot(range(1, n_inf), np.ones(n_inf-1)*n)
    plt.title("N = "+str(N)+", n = "+str(n))
    plt.xlabel("number of patterns")
    plt.ylabel("speedup")
    plt.show()


def speedup_ideal_patterns():
    patterns = [
        "AAAAAAA",
        "TTTTTTT",
        "GGGGGGG",
        "CCCCCCC"
    ]
    N = 1
    n = 4
    approx = 3

    time0, _ = get_results("patterns", my_file_1["name"], patterns, N, n, approx)
    print("time0")
    print(time0)
    time1, _ = get_results("normal", my_file_1["name"], patterns, N, n, approx)
    print("time1")
    print(time1)


def test_mpi_only():
    N = 1
    n = 4
    approx = 3

    sizes = []
    speedup = []
    patterns = one_pattern
    print("computing for 1 pattern:")
    for f in my_files:
        print(f["name"])
        time0, r0 = get_results("normal", f["name"], patterns, N, n, approx)
        time1, r1 = get_results("mpi_only", f["name"], patterns, N, n, approx)
        print(r0==r1)
        print(time0)
        print(time1)
        speedup.append(time0/time1)
        sizes.append(f["size"])

    plt.scatter(sizes, speedup, label="with 1 pattern")
    plt.plot(sizes, np.ones(len(sizes))*n)


    sizes = []
    speedup = []
    patterns = four_patterns
    print("computing for 1 pattern:")
    for f in my_files:
        print(f["name"])
        time0, r0 = get_results("normal", f["name"], patterns, N, n, approx)
        time1, r1 = get_results("mpi_only", f["name"], patterns, N, n, approx)
        print(r0==r1)
        print(time0)
        print(time1)
        speedup.append(time0/time1)
        sizes.append(f["size"])

    plt.scatter(sizes, speedup, label="with 4 patterns")
    plt.plot(sizes, np.ones(len(sizes))*n)

    plt.legend()
    plt.title("N = "+str(N)+", n = "+str(n))
    plt.xlabel("size of file")
    plt.ylabel("speedup")
    plt.show()


def test_cuda_only():

    sizes = []
    speedup = []
    patterns = one_pattern
    print("computing for 1 pattern:")
    for f in my_files:
        print(f["name"])
        time0, r0 = get_results("normal", f["name"], patterns)
        time1, r1 = get_results("cuda_only", f["name"], patterns)
        print(r0==r1)
        print(time0)
        print(time1)
        speedup.append(time0/time1)
        sizes.append(f["size"])

    plt.scatter(sizes, speedup, label="with 4 patterns")

    plt.legend()
    plt.title("N = " + str(N) + ", n = " + str(n))
    plt.xlabel("size of file")
    plt.ylabel("speedup")
    plt.show()


def test_big_thing():
    N=30
    n=30
    approx=3
    patterns=["ATTTTGC", "ATGCATTGC", "ATGCCGTTGC", "ACCCGATGAC", "ATGACCCCC", "TTTGCAC", "TTTTGCCATGC", "TGCAGACTGC", "TTC", "GCAAT", "AAAGCTGCAG", "AAAAAGTGGCCTGGCAGCCGTGGC"]
    time0, _= get_results("normal", my_file_3["name"], patterns, N, n, approx)
    print("duration for normal apm:"+str(time0))
    time1, _= get_results("mpi_openmp", my_file_3["name"], patterns, N, n, approx)
    print("duration for MPI+OMP apm:"+str(time1))
    time2, _= get_results("mpi_cuda", my_file_3["name"], patterns, N, n, approx)
    print("duration for MPI+CUDA apm:"+str(time2))
    

def plot_theorique():
    sizes = []
    times = []
    patterns = one_pattern
    print("computing for different file sizes:")
    for f in my_files:
        time0, r0 = get_results("normal", f["name"], patterns, N, n, approx)
        times.append(time0)
        sizes.append(f["size"])

    print(times)
    print(sizes)

    print("computing for different pattern sizes:")
    alphabet = ['A', 'G', 'C', 'T']
    for i in range(3, 50, 4):
        current = "".join(np.random.choice(alphabet, i, replace=True))
        patterns = [current]
        time0, r0 = get_results("normal", my_file_1["name"], patterns, N, n, approx)
        times.append(time0)
        sizes.append(i)

    print(times)
    print(sizes)


compile_everything()
plot_theorique()