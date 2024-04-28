#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct atom
{
	char element[3]; //null-terminated string representing the element name of the atom
	double x,y,z; //x,y, and z describe the position in Angstroms of the atom relative to a common origin for a molecule
} atom; //an atom and its position in 3-D space

typedef struct bond
{
	unsigned short a1, a2; //pointers to the two atoms in the co-valent bond, no need to free a1 or a2
	unsigned char epairs;  //number of electron pairs in the bond (eparis=2 is a double bond)
	atom *atoms;
	double x1, x2, y1, y2, z, len, dx, dy; 
	//x1 and y1 are the x and y coordinates of a1
	//z is the average z of a1 and a2
	//len is the distance from a1 to a2 (pythogorean)
	//dx and dy store the differences between x and y values of a2 and a1 divided by the len
} bond; //bond between two atoms

typedef struct molecule
{
	unsigned short atom_max, atom_no; 
	//atom_max is a non-negative integer that records the dimensionality of an array pointed to by atoms
	//atom_no is the number of atoms currently stored in the array atoms; never larger than atom_max
	atom *atoms, **atom_ptrs; 
	//allocate memory to the atoms pointer
	//atoms_ptrs is an array of atoms pointers (size is the same?) and is initialized to to corresponding structures
	//atoms_pts[0] points to atoms[0]
	unsigned short bond_max, bond_no;
	//bond_max is a non-negative integer that records the dimensionality of an array pointed to by bonds
	//bond_no is the number of bonds currently stored in the array bonds; must never be larger than bond_max
	bond *bonds, **bond_ptrs; 
	//allocate memory to the bonds pointer
	//bond_ptrs is an array of bonds pointers (size the same?) and is initialized to to corresponding structures
	//bond_pts[0] points to bonds[0]
} molecule; //consists of zero or more atoms, and zero or more bonds

typedef double xform_matrix[3][3]; //3-D transformation matrix

void atomset( atom *atom, char element[3], double *x, double *y, double *z );
void atomget( atom *atom, char element[3], double *x, double *y, double *z );
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs );
void compute_coords( bond *bond );
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max );
molecule *molcopy( molecule *src );
void molfree( molecule *ptr );
void molappend_atom( molecule *molecule, atom *atom );
void molappend_bond( molecule *molecule, bond *bond );
int atomCompare(const void *a, const void *b);
int bond_comp(const void *a, const void *b);
void molsort( molecule *molecule );
void xrotation( xform_matrix xform_matrix, unsigned short deg );
void yrotation( xform_matrix xform_matrix, unsigned short deg );
void zrotation( xform_matrix xform_matrix, unsigned short deg );
void mol_xform( molecule *molecule, xform_matrix matrix );
