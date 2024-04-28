#include "mol.h"

/*
* Only malloc as much memory as required in the function descriptions
* All malloc return values must be checked before accessing memory
* If a malloc returns a NULL, the return value of the calling function should also be NULL
*/

void atomset( atom *atom, char element[3], double *x, double *y, double *z ){
//copy the values pointed to by element x,y,z into the atom stored at atom
//all pointer addresses have sufficient memory allocated to them
	strcpy(atom->element, element);
	atom->x = *x;
	atom->y = *y;
	atom->z = *z;
}

void atomget( atom *atom, char element[3], double *x, double *y, double *z ){
//copy the values in the atom stored at atom to the locations pointed to by element x,y, and z
//all pointer addresses have sufficient memory allocated to them
	strcpy(element, atom->element);
	*x = atom->x;
	*y = atom->y;
	*z = atom->z;
}

void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
//copy the values a1, a2, atoms and epairs into the corresponding structure attributes in bond	
//all pointer addresses have sufficient memory allocated to them
//you are NOT copying atom structures, only the ADDRESSES of the atom structures
//call compute_coords function on the bond
	bond->a1 = *a1;
	bond->a2 = *a2;
	for (int i = 0; i < 2; i++) {
		bond->atoms[i] = *atoms[i];
	}
	bond->epairs = *epairs;
	compute_coords(bond);
}

void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
//copy the structure attributes in bond to their corresponding arguments: a1, a2, atoms and epairs
//all pointer addresses have sufficient memory allocated to them
//you are NOT copying atom structures, only the ADDRESSES of the atom structures
	*a1 = bond->a1;
	*a2 = bond->a2;
	*atoms = bond->atoms;
	*epairs = bond->epairs;
}

void compute_coords( bond *bond){
//compute the z, x1, y1, x2, y2, len, dx and dy values and set them in appropriate structure member variables
	atom *a1 = &(bond->atoms[bond->a1]); //get the address of the first atom
	atom *a2 = &(bond->atoms[bond->a2]);

	bond->z = (a1->z + a2->z) / 2;
	bond->x1 = a1->x;
	bond->y1 = a1->y;
	bond->x2 = a2->x;
	bond->y2 = a2->y;
	bond->len = sqrt(pow((bond->x2 - bond->x1),2) + pow((bond->y2 - bond->y1),2));
	bond->dx = (bond->x2 - bond->x1) / bond->len;
	bond->dy = (bond->y2 - bond->y1) / bond->len;
}

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ){
//return the address of a malloced area of memory, large enough to hold a molecule
//copy atom_max value into structure
//atom_no in the structure should be set to zero
//the arrays atoms and atom_ptrs should be malloced to have enough memory to hold atom_max and pointers
//copy bond_max value into structure
//bond_no in the structure should be set to zero
//bonds and bond_ptrs malloced to have enough memory to hold bond_max bonds and pointers
	molecule *aMolecule = malloc(sizeof(molecule)); //check size
	if(aMolecule == NULL){
		return NULL;
	}
	aMolecule->atom_max = atom_max;
	aMolecule->atom_no = 0;

	if(aMolecule->atom_max == 0){
		aMolecule->atoms = malloc(sizeof(struct atom));
		aMolecule->atom_ptrs = malloc(sizeof(struct atom*));
	} //if the max is 0, allocate space for 1 atom/atom ptr
	else{
		aMolecule->atoms = malloc(aMolecule->atom_max * (sizeof(struct atom)));
		aMolecule->atom_ptrs = malloc(aMolecule->atom_max * (sizeof(struct atom*)));
	} //if the atom max > 0, allocate space for the max number of atoms/atom ptrs

	if((aMolecule->atoms) == NULL || (aMolecule->atom_ptrs) == NULL){
		return NULL;
	}

	aMolecule->bond_max = bond_max;
	aMolecule->bond_no = 0;

	if(aMolecule->bond_max == 0){
		aMolecule->bonds = malloc(sizeof(struct bond));
		aMolecule->bond_ptrs = malloc(sizeof(struct bond*));
	}
	else{
		aMolecule->bonds = malloc(aMolecule->bond_max * (sizeof(struct bond))); 
		aMolecule->bond_ptrs = malloc(aMolecule->bond_max * sizeof(struct bond*));
	}

	if((aMolecule->bonds) == NULL || (aMolecule->bond_ptrs) == NULL){
		return NULL;
	}

	return aMolecule;
}

molecule *molcopy( molecule *src ){
//return the address of a malloced area of memory, large enough to hold a molecule
//atom_max, atom_no, bond_max, and bond_no should be copied from src into the new structure
//atoms, atom_ptrs, bonds, and bond_ptrs must be allocated to match the size of the ones in src
//reuse (call) the molmalloc function in this function
//use molappend atom and bond to add the atoms from src to the new molecule

	molecule *copiedMol = molmalloc(src->atom_max, src->bond_max);

	for(int i = 0; i < src->atom_no; i++){
		molappend_atom(copiedMol, &src->atoms[i]);
	} //copy the atoms from src to the new molecule

	for(int i = 0; i < src->bond_no; i++){
		molappend_bond(copiedMol, &src->bonds[i]);
	}

	return copiedMol;
}

void molfree( molecule *ptr ){
//free molecule pointed to by ptr (includes the arrays atoms, atom_ptrs, bonds, bond_ptrs)
	free(ptr->atom_ptrs);
	free(ptr->atoms);
	free(ptr->bond_ptrs);
	free(ptr->bonds);
	free(ptr);
}

void molappend_atom( molecule *molecule, atom *atom ){
//copy the data pointed to by atom to the first "empty" atom in atoms in the molecule pointed to by molecule
//set the first "empty" pointer in atom_ptrs to the same atom in the atoms array, incrementing the value of atom_no
//use realloc for atoms and atom_ptrs so that a larger amount of memory is allocated and existing data is copied to the new location

	if(molecule->atom_no == molecule->atom_max){ 
		if(molecule->atom_max == 0){ //if the atom number and the atom max are both 0
			(molecule->atom_max)++;

			molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * (molecule->atom_max));
			//increment the max and allocate space for an atom

			if (molecule->atoms == NULL){
				fprintf(stderr, "realloc failed1\n");
				exit(-1);
			} //print error message and exit if malloc fails

			molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * (molecule->atom_max));

			if (molecule->atom_ptrs == NULL){
				fprintf(stderr, "realloc failed2\n");
				exit(-1);
			}

			for(int i = 0; i < molecule->atom_no; i++){
				(molecule->atom_ptrs)[i] = &((molecule->atoms)[i]);
			} //recalculate the pointers in case they got moved to another place in memory
		}
		else{
			(molecule->atom_max) *= 2;

			molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * (molecule->atom_max));

			if (molecule->atoms == NULL){
				fprintf(stderr, "realloc failed3\n");
				exit(-1);
			}

			molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * (molecule->atom_max));

        	if (molecule->atom_ptrs == NULL){
				fprintf(stderr, "realloc failed4\n");
				exit(-1);
			}

			for(int i = 0; i < molecule->atom_no; i++){
				(molecule->atom_ptrs)[i] = &((molecule->atoms)[i]);
			}
		}
	}
	else if(molecule->atom_max == 0){
			(molecule->atom_max)++;
			
			molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * (molecule->atom_max));

			if (molecule->atoms == NULL){
				fprintf(stderr, "realloc failed5\n");
				exit(-1);
			}

			molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * (molecule->atom_max));

        	if (molecule->atom_ptrs == NULL){
				fprintf(stderr, "realloc failed6\n");
				exit(-1);
			}
			for(int i = 0; i < molecule->atom_no; i++){
				(molecule->atom_ptrs)[i] = &((molecule->atoms)[i]);
			}
	}

	(molecule->atoms)[molecule->atom_no] = *atom; //append the atom to the empty space in the array
	(molecule->atom_ptrs)[molecule->atom_no] = &((molecule->atoms)[molecule->atom_no]); //sets the next space in the pointer array to the appended atom
	(molecule->atom_no)++;
}

void molappend_bond( molecule *molecule, bond *bond ){
//same as molappend_atom but for bonds
		if(molecule->bond_no == molecule->bond_max){
		if(molecule->bond_max == 0){
			(molecule->bond_max)++;

			molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * (molecule->bond_max));

			if (molecule->bonds == NULL){
				fprintf(stderr, "realloc failed\n");
				exit(-1);
			}

			molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * (molecule->bond_max));

			if (molecule->bond_ptrs == NULL){
				fprintf(stderr, "realloc failed\n");
				exit(-1);
			}

			for(int i = 0; i < molecule->bond_no; i++){
				(molecule->bond_ptrs)[i] = &((molecule->bonds)[i]);
			}
		}
		else{
			(molecule->bond_max) *= 2;

			molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * (molecule->bond_max));

			if (molecule->bonds == NULL){
				fprintf(stderr, "realloc failed\n");
				exit(-1);
			}

			molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * (molecule->bond_max));

        	if (molecule->bond_ptrs == NULL){
				fprintf(stderr, "realloc failed\n");
				exit(-1);
			}

			for(int i = 0; i < molecule->bond_no; i++){
				(molecule->bond_ptrs)[i] = &((molecule->bonds)[i]);
			}
		}
	}
	else if(molecule->bond_max == 0){
			(molecule->bond_max)++;
			
			molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * (molecule->bond_max));

			if (molecule->bonds == NULL){
				fprintf(stderr, "realloc failed\n");
				exit(-1);
			}

			molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * (molecule->bond_max));

        	if (molecule->bond_ptrs == NULL){
				fprintf(stderr, "realloc failed\n");
				exit(-1);
			}
			for(int i = 0; i < molecule->bond_no; i++){
				(molecule->bond_ptrs)[i] = &((molecule->bonds)[i]);
			}
	}

	(molecule->bonds)[molecule->bond_no] = *bond;
	(molecule->bond_ptrs)[molecule->bond_no] = &((molecule->bonds)[molecule->bond_no]);
	(molecule->bond_no)++;
}

int atomCompare(const void *a, const void *b){

	atom **aPtr, **bPtr;

	aPtr = (struct atom **)a; //copy the pointer to a temporary pointer to be evaluated
	bPtr = (struct atom **)b;
	
	if((*aPtr)->z < (*bPtr)->z){ //if the z value of the first atom is < the z value of the second atom
		return -1;
	}
	else if ((*aPtr)->z == (*bPtr)->z){ //if the z values are equal
		return 0;
	}
	return 1; //if the z value of the first atom is > the z value of the second atom

}
int bond_comp(const void *a, const void *b){ //change
	//same as atomCompare except that each bond has 2 atoms and they need to be added before comparing
	bond **aPtr, **bPtr;

	aPtr = (struct bond **)a;
	bPtr = (struct bond **)b;

	if((*aPtr)->z < (*bPtr)->z){
		return -1;
	}
	else if ((*aPtr)->z == (*bPtr)->z){
		return 0;
	}
	return 1;
}

void molsort( molecule *molecule ){
//sort atom_ptrs and bond_ptrs arrays in order of increasing z value
//atom_ptrs[0] should point to the atom that contains the lowest z value
//atom_ptrs[atom_no-1] should contain the highest z value
//bond z values are the average z value of their 2 atoms
//**HINT USE qsort** bond_ptrs[0] should point to the bond that has the lowest z value and bond_ptrs[atom_no-1] should contain the highest z value

	qsort(&molecule->atom_ptrs[0], molecule->atom_no, sizeof(atom*), atomCompare);
	qsort(&molecule->bond_ptrs[0], molecule->bond_no, sizeof(bond*), bond_comp); //CHECK

}

void xrotation( xform_matrix xform_matrix, unsigned short deg ){
//return an affine transformation matrix corresponding to a rotation of deg degrees around the x-axis	
	double rad = deg * (M_PI / 180.0); //convert the degrees to radians
	
	xform_matrix [0][0] = 1; xform_matrix [0][1] = 0; xform_matrix [0][2] = 0;
	xform_matrix [1][0] = 0; xform_matrix [1][1] = cos(rad); xform_matrix [1][2] = sin(rad) * -1;
	xform_matrix [2][0] = 0; xform_matrix [2][1] = sin(rad); xform_matrix [2][2] = cos(rad);
	//perform the rotation matrix using the inputted radians
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ){
//return an affine transformation matrix corresponding to a rotation of deg degrees around the y-axis	
	double rad = deg * (M_PI / 180.0);

	xform_matrix [0][0] = cos(rad); xform_matrix [0][1] = 0; xform_matrix [0][2] = sin(rad);
	xform_matrix [1][0] = 0; xform_matrix [1][1] = 1; xform_matrix [1][2] = 0;
	xform_matrix [2][0] = sin(rad) * -1; xform_matrix [2][1] = 0; xform_matrix [2][2] = cos(rad);
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ){
//return an affine transformation matrix corresponding to a rotation of deg degrees around the z-axis	
	double rad = deg * (M_PI / 180.0);

	xform_matrix [0][0] = cos(rad); xform_matrix [0][1] = sin(rad) * -1; xform_matrix [0][2] = 0;
	xform_matrix [1][0] = sin(rad); xform_matrix [1][1] = cos(rad); xform_matrix [1][2] = 0;
	xform_matrix [2][0] = 0; xform_matrix [2][1] = 0; xform_matrix [2][2] = 1;
}

void mol_xform( molecule *molecule, xform_matrix matrix ){
//apply the transformation matrix to all the atoms of molecule by performing a vector matrix multiplication on the x,y,z coordinates
//apply compute_coords to each bond in the molecule
	double xTemp, yTemp, zTemp = 0.0; //create temporary variables to hold the values during multiple - avoids error in multiplying

	for(int i = 0; i < molecule->atom_no; i++){ //perform the transformation on all of the atoms
		xTemp = (molecule->atoms[i].x * matrix[0][0]) + (molecule->atoms[i].y * matrix[0][1]) + (molecule->atoms[i].z * matrix[0][2]);
		yTemp = (molecule->atoms[i].x * matrix[1][0]) + (molecule->atoms[i].y * matrix[1][1]) + (molecule->atoms[i].z * matrix[1][2]); 
		zTemp = (molecule->atoms[i].x * matrix[2][0]) + (molecule->atoms[i].y * matrix[2][1]) + (molecule->atoms[i].z * matrix[2][2]);
		//vector multiplication on the matrix
		molecule->atoms[i].x = xTemp;
		molecule->atoms[i].y = yTemp;
		molecule->atoms[i].z = zTemp;
		//set the atoms values to the multiplied variables
	}
	for(int i = 0; i < molecule->bond_no; i++){ //perform the transformation on all of the bonds
		compute_coords(&molecule->bonds[i]);
	}
}
