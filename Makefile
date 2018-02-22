all:
	$(CUDA_ROOT)/bin/nvcc -I. -o apm_cuda src/apm_cuda.cu
