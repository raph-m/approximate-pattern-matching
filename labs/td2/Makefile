EXE=hello \
	hello2 \
	hello3 \
	max1 \
	max2 \
	max3 \
	max4 \
	max5 

all: $(EXE)

% : %.c
	mpicc -o $@ $<

clean:
	rm -f $(EXE)
