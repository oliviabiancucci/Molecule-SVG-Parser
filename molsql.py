import os
import sqlite3
import MolDisplay

class Database():
    def __init__(self, reset=False):
        #if reset is set to True, the molecules.db will be deleted
        if reset:
            try: #remove the database if it exists
                os.remove('molecules.db')
            except FileNotFoundError:
                pass

        self.conn = sqlite3.connect('molecules.db')
    
    def create_tables(self): 
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements(
                    ELEMENT_NO INTEGER NOT NULL,
                    ELEMENT_CODE VARCHAR(3) NOT NULL,
                    ELEMENT_NAME VARCHAR(32) NOT NULL,
                    COLOUR1 CHAR(6) NOT NULL,
                    COLOUR2 CHAR(6) NOT NULL,
                    COLOUR3 CHAR(6) NOT NULL,
                    RADIUS DECIMAL(3) NOT NULL,
                    PRIMARY KEY (ELEMENT_CODE));""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms(
                        ATOM_ID INTEGER NOT NULL,
                        ELEMENT_CODE VARCHAR(3) NOT NULL,
                        X DECIMAL(7,4) NOT NULL,
                        Y DECIMAL(7,4) NOT NULL,
                        Z DECIMAL(7,4) NOT NULL,
                        PRIMARY KEY (ATOM_ID),
                        FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements
                        );""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds(
                        BOND_ID INTEGER NOT NULL,
                        A1 INTEGER NOT NULL,
                        A2 INTEGER NOT NULL,
                        EPAIRS INTEGER NOT NULL,
                        PRIMARY KEY (BOND_ID)
                        );""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules(
                        MOLECULE_ID INTEGER NOT NULL,
                        NAME TEXT NOT NULL UNIQUE,
                        PRIMARY KEY (MOLECULE_ID)
                        );""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom(
                        MOLECULE_ID INTEGER NOT NULL,
                        ATOM_ID INTEGER NOT NULL,
                        PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                        FOREIGN KEY (ATOM_ID) REFERENCES Atoms
                        );""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond(
                        MOLECULE_ID INTEGER NOT NULL,
                        BOND_ID INTEGER NOT NULL,
                        PRIMARY KEY (MOLECULE_ID, BOND_ID),
                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                        FOREIGN KEY (BOND_ID) REFERENCES Bonds
                        );""")
        self.conn.commit() #commits the changes to the database
        
    def __setitem__( self, table, values ): #inserts a row into the table passed in
        cursor = self.conn.cursor()
        inputRow = f"INSERT INTO {table} VALUES ({','.join(['?']*len(values))})"
        cursor.execute(inputRow, values)
        self.conn.commit()
    
    def __removeitem__(self, table, values):
        cursor = self.conn.cursor()
        inputRow = f"DELETE FROM {table} WHERE ELEMENT_CODE = '{values}'"
        cursor.execute(inputRow)
        self.conn.commit()
    
    def __getMolNames__(self):
        cursor = self.conn.cursor()
        action = f"SELECT NAME FROM Molecules"
        cursor.execute(action)
        return cursor.fetchall()
    
    def getNumAtoms(self, molname):
        cursor = self.conn.cursor()
        action = f"SELECT COUNT(ATOM_ID) FROM MoleculeAtom WHERE MOLECULE_ID = (SELECT MOLECULE_ID FROM Molecules WHERE NAME = '{molname}')"
        cursor.execute(action)
        return cursor.fetchone()[0]
    
    def getNumBonds(self, molname):
        cursor = self.conn.cursor()
        action = f"SELECT COUNT(BOND_ID) FROM MoleculeBond WHERE MOLECULE_ID = (SELECT MOLECULE_ID FROM Molecules WHERE NAME = '{molname}')"
        cursor.execute(action)
        return cursor.fetchone()[0]
        
    
    def add_atom( self, molname, atom ):
        cursor = self.conn.cursor()
        inputAtom = """INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z)
                VALUES (?, ?, ?, ?)""" 
        cursor.execute(inputAtom, (atom.element, atom.x, atom.y, atom.z)) #inserts the atom into the Atoms table
        
        atom_id = cursor.lastrowid #gets the atom_id of the atom just inserted
        inputAtom = """INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID)
                VALUES ((SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?), ?)"""
        cursor.execute(inputAtom, (molname, atom_id)) #inserts the atom into the MoleculeAtom table with the atom_id
        
        self.conn.commit()
        
    def add_bond(self, molname, bond):
        self.conn.execute("""INSERT INTO Bonds (BOND_ID, A1, A2, EPAIRS) VALUES (?, ?, ?, ?)""", (None, bond.a1, bond.a2, bond.epairs))
        
        bondID = self.conn.execute("""SELECT BOND_ID FROM Bonds ORDER BY BOND_ID DESC LIMIT 1;""").fetchone()[0]
        molID = self.conn.execute("""SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?;""", (molname,)).fetchone()[0]
        
        self.__setitem__("MoleculeBond", (molID, bondID))
        
        self.conn.commit()
        
    def add_molecule( self, name, fp ):
        try:
            mol = MolDisplay.Molecule() #creates a new molecule
            mol.parse(fp) #parses the molecule from the file

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO Molecules (NAME) VALUES (?)", (name,))
        
            for atom in range(mol.atom_no): #adds the atoms to the database
                self.add_atom(name, mol.get_atom(atom))

            for bond in range(mol.bond_no):
                self.add_bond(name, mol.get_bond(bond))
        except:
            print("Invalid file.")
            pass

        self.conn.commit()
        
    def load_mol( self, name ):
        mol = MolDisplay.Molecule()

        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT Atoms.ATOM_ID, ELEMENT_CODE, X, Y, Z FROM Atoms NATURAL JOIN MoleculeAtom NATURAL JOIN Molecules WHERE NAME = ?", (name,))
        atoms = cursor.fetchall() #gets all the atoms in the molecule from the database

        for atom in atoms: #adds the atoms to the molecule
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])
            
        cursor.execute("SELECT DISTINCT Bonds.BOND_ID, A1, A2, EPAIRS FROM Bonds NATURAL JOIN MoleculeBond NATURAL JOIN Molecules WHERE NAME = ?", (name,))
        bonds = cursor.fetchall() 
        
        for bond in bonds:
            mol.append_bond(bond[1], bond[2], bond[3])
            
        return mol #returns the molecule object with the atoms and bonds appended
        
    def radius ( self ):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements")
        return dict(cursor.fetchall()) #returns a dictionary mapping the ELEMENT_CODE values to the RADIUS values based on the Elements table
    
    def element_name( self ):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements")
        return dict(cursor.fetchall())
    
    def radial_gradients(self):
        cursor = self.conn.cursor()
        radialGradientSVG = """<radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
            <stop offset="0%%" stop-color="#%s"/>
            <stop offset="50%%" stop-color="#%s"/>
            <stop offset="100%%" stop-color="#%s"/>
        </radialGradient>""" #creates a radial gradient string that will be used for the database elements
        
        cursor.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements") #gets the element names and colours from the database
        elements = cursor.fetchall()

        finalSVGs = []
        for element in elements: #for each element, make a radial gradient
            finalSVGs.append(radialGradientSVG % (element[0], element[1], element[2], element[3]))

        return ''.join(finalSVGs) #returns the radial gradients concatenated as a string

if __name__ == "__main__":
    db = Database(reset=False); # or use default
    MolDisplay.radius = db.radius();
    MolDisplay.element_name = db.element_name();
    MolDisplay.header += db.radial_gradients();
    for molecule in [ 'Water', 'Caffeine', 'Isopentanol' ]:
        mol = db.load_mol( molecule );
        mol.sort();
        fp = open( molecule + ".svg", "w" );
        fp.write( mol.svg() );
        fp.close();