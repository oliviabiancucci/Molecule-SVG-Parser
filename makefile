CC = clang
CFLAGS = -Wall -std=c99 -pedantic
LIBS = -lm

all: lib

lib: test.o libmol.so _molecule.so
	$(CC) test.o -L. $(LIBS) -lmol -lpython3.9 -o -lib

libmol.so: mol.o
	$(CC) -shared -o libmol.so mol.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) -shared -lmol -dynamiclib -L. -L /usr/lib/python3.9/config-3.9-x86_64-linux-gnu -lpython3.9 -o _molecule.so molecule_wrap.o

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -fpic -c mol.c -o mol.o

molecule_wrap.o: molecule_wrap.c 
	$(CC) $(CFLAGS) -c molecule_wrap.c -I/usr/include/python3.9 -fpic -o molecule_wrap.o

test.o: test.c mol.h
	$(CC) $(CFLAGS) -c test.c -o test.o
	
clean:
	rm -rf *.o *.so lib