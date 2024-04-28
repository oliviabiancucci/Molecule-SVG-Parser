import molecule

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""

offsetx = 500
offsety = 500

class Atom():
	def __init__(self, atom): #atom is the C struct atom
		self.atom = atom
		self.z = atom.z
    
	def __str__(self): #return the atom as a string
		return f"Atom: element={self.atom.element}, x={self.atom.x}, y={self.atom.y}, z={self.atom.z}"
    
	def svg(self): #return the atom as an svg circle
		self.atom.x *= 100
		self.atom.x += offsetx
		self.atom.y *= 100
		self.atom.y += offsety
		try:
			self.atom.z = radius[self.atom.element]
		except KeyError:
			self.atom.z = 25
   
		try:
			self.atom.color = element_name[self.atom.element]
		except KeyError:
			self.atom.color = "000000"
		
		return f'  <circle cx="{self.atom.x:.2f}" cy="{self.atom.y:.2f}" r="{self.atom.z}" fill="#{self.atom.color}"/>\n'

class Bond():
	def __init__(self, bond): #bond is the C struct bond
		self.bond = bond
		self.z = bond.z
	
	def __str__(self): #return the bond as a string
		return f"Bond: atom1={self.bond.a1}, atom2={self.bond.a2}, z={self.bond.z}, x1={self.bond.x1}, y1={self.bond.y1}, x2={self.bond.x2}, y2={self.bond.y2}"
	
	def svg(self): #return the bond as an svg line
		cx1 = ((self.bond.x1 * 100) + offsetx) - (self.bond.dy * 10)
		cy1 = ((self.bond.y1 * 100) + offsety) + (self.bond.dx * 10)
		cx2 = ((self.bond.x1 * 100) + offsetx) + (self.bond.dy * 10)
		cy2 = ((self.bond.y1 * 100) + offsety) - (self.bond.dx * 10)
		cx3 = ((self.bond.x2 * 100) + offsetx) + (self.bond.dy * 10)
		cy3 = ((self.bond.y2 * 100) + offsety) - (self.bond.dx * 10)
		cx4 = ((self.bond.x2 * 100) + offsetx) - (self.bond.dy * 10)
		cy4 = ((self.bond.y2 * 100) + offsety) + (self.bond.dx * 10)

		return f'  <polygon points="{cx1:.2f},{cy1:.2f} {cx2:.2f},{cy2:.2f} {cx3:.2f},{cy3:.2f} {cx4:.2f},{cy4:.2f}" fill="green"/>\n'

class Molecule(molecule.molecule):
			
	def __str__(self):
		display = []
		for atom in range(self.atom_no): #append atoms to a list
			display.append(Atom(self.get_atom(atom)))

		for bond in range(self.bond_no): #append bonds to a list
			display.append(Bond(self.get_bond(bond)))

		return "".join([str(d) for d in display]) #return the list as a string
	
	def svg(self):
		a1 = []
		b1 = []
		svgList = []
		
		for atom in range(self.atom_no): #append atoms to a list
			a1.append(Atom(self.get_atom(atom)))

		for bond in range(self.bond_no): #append bonds to a list
			b1.append(Bond(self.get_bond(bond)))

		while a1 and b1: #sort the lists
			if a1[0].z < b1[0].z:
				svgList.append(a1[0].svg())
				a1.pop(0) #remove the first element from the list
			else:
				svgList.append(b1[0].svg())
				b1.pop(0)

		svgList.extend([a.svg() for a in a1]) #add the remaining elements to the list
		svgList.extend([b.svg() for b in b1])

		return header + "".join(svgList) + footer #return the list as a string with the header and footer

	def parse(self, fileObj): #parses the file
		lines = fileObj.readlines() #reads the file
		num_atoms, num_bonds = map(int, lines[3].split()[:2]) #gets the number of atoms and bonds

		for i in range(num_atoms): #appends the atoms to the molecule
			x = float(lines[i+4].split()[0]) #first number in the current line is the x coordinate
			y = float(lines[i+4].split()[1])
			z = float(lines[i+4].split()[2])
			element = lines[i+4].split()[3]
			self.append_atom(element, x, y, z)

		for i in range(num_bonds): #appends the bonds to the molecule
			a1 = int(lines[i+4+num_atoms].split()[0])
			a2 = int(lines[i+4+num_atoms].split()[1])
			epairs = int(lines[i+4+num_atoms].split()[2])
			self.append_bond(a1-1, a2-1, epairs) 
		#return molecule
