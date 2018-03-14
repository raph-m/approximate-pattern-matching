import subprocess
import matplotlib.pyplot as plt
import random
import numpy as np

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


def get_results(script, file, patterns, N, n, approx):

    command = ""
    if script == "normal":
        command = "./apm "
    if script == "mpi_only":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_par_seq "
    if script == "mpi_openmp":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_omp "
    if script == "cuda_only":
        command = "./apm_cuda_only "
    if script == "patterns":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_par "

    command += args(file, patterns, approx)
    command = command.split(" ")

    print("command:")
    print(command)

    ans = subprocess.check_output(command).decode()

    print("ans:")
    print(ans)

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


def pattern_parallelism(N=4, n=4, approx=3):
    alphabet = ['A', 'G', 'C', 'T']
    n_inf = 10
    patterns = []
    for i in range(n_inf):
        n = random.randint(5, 30)
        current = "".join(np.random.choice(alphabet, n, replace=True))
        patterns.append(current)

    # TODO: trier les patterns avant de les envoyer au C !
    speedups = []
    for i in range(n_inf):
        time0, _ = get_results("patterns", my_file_0["name"], patterns[:i], N, n, approx)
        time1, _ = get_results("normal", my_file_0["name"], patterns[:i], N, n, approx)
        speedups.append(time1/time0)

    plt.plot(range(n_inf), speedups)
    plt.plot(range(n_inf), np.ones(n_inf))
    plt.plot(range(n_inf), np.ones(n_inf)*n)
    plt.title("N = "+str(N)+", n = "+str(n))
    plt.xlabel("number of patterns")
    plt.ylabel("speedup")
    plt.show()


def test_patterns(N=4, n=4, approx=3):
    patterns = ["ATT", "AGCC"]
    time0, _ = get_results("patterns", my_file_0["name"], patterns, N, n, approx)
    time1, _ = get_results("normal", my_file_0["name"], patterns, N, n, approx)

compile_everything()
pattern_parallelism()

