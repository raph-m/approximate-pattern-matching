import subprocess
import matplotlib.pyplot as plt

my_file_0 = {
    "name": "chr1_KI270710v1_random.fa",
    "size": 41,
    "nickname": "small"
}

my_file_1 = {
    "name": "chr6_GL000250v2_alt.fa",
    "size": 4800,
    "nickname": "medium"
}

my_file_2 = {
    "name": "chrY.fa",
    "size": 58400,
    "nickname": "big"
}

my_file_3 = {
    "name": "chr6.fa",
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
    "cuda_only": "/usr/local/cuda-9.0/bin/nvcc -o apm_cuda_only src/apm_cuda_only.cu"
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
    look_for = "<" + pattern + ">: "
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
        "cuda_only": "/usr/local/cuda-9.0/bin/nvcc -o apm_cuda_only src/apm_cuda_only.cu"
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


def get_results(script, file, patterns, approx=3, N=1, n=1):

    command = ""
    if script == "normal":
        command = "./apm "
    if script == "mpi_only":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_par_seq "
    if script == "mpi_openmp":
        command = "salloc -N " + str(N) + " -n " + str(n) + " mpirun ./apm_omp "
    if script == "cuda_only":
        command = "./apm_cuda_only "

    command += args(file, patterns, approx)
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

    plt.scatter(sizes, results_normal, label="normal")
    plt.scatter(sizes, results_cuda, label="cuda")
    plt.plot()
    plt.show()



