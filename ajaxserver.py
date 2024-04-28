from http.server import HTTPServer, BaseHTTPRequestHandler

import sys      # to get command line argument for port
import urllib   # code to parse for data
import cgi
import io
import molsql
import MolDisplay
import sqlite3

# list of files that we allow the web-server to serve to clients
# (we don't want to serve any file that the client requests)
public_files = [ '/mol_icon.png', '/index.html', '/style.css', '/add.js', '/add.html', '/remove.js', '/remove.html', '/upload.js', '/upload.html', '/display.js', '/display.html', '/table.html',]

db = molsql.Database(reset=True)
db.create_tables()
cursor = db.conn.cursor()

class MyHandler( BaseHTTPRequestHandler ):
        # used to GET a file from the list ov public_files, above
    def do_GET(self):
        if self.path in public_files:
            if self.path == "/display.html": #get the table of molecules in the database
                molecule = MolDisplay.Molecule()
                names = db.__getMolNames__()
                name_list = [name[0] for name in names]
                
                html_table = ""
                html_table += "<table>"
                html_table += "<tr><th>Molecule Name</th><th>Number of Atoms</th><th>Number of Bonds</th></tr>"

                for name in name_list:
                    numAtoms = db.getNumAtoms(name) #get the number of atoms and bonds for each molecule
                    numBonds = db.getNumBonds(name)
                    html_table += "<tr>"
                    html_table += f"<td>{name}</td><td>{numAtoms}</td><td>{numBonds}</td>"
                    html_table += f"<td><button id = '{name}' onclick = 'sendPostRequest(this.id)'>View as an SVG</button></td>"
                    html_table += "</tr>"

                html_table += "</table>"
                with open('table.html', 'w') as f:
                    f.write(html_table) #write the table to a file

            self.send_response(200)
            if self.path.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif self.path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif self.path.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif self.path.endswith('.png'):
                self.send_header('Content-type', 'image/png')
            else:
                self.send_header('Content-type', 'text/plain')
            self.end_headers()

            if self.path.endswith('.html') or self.path.endswith('.css') or self.path.endswith('.js'): #send the file to the client
                fp = open(self.path[1:])
                page = fp.read()
                fp.close()
                self.wfile.write(bytes(page, 'utf-8'))
                
            elif self.path.endswith('.png'): #send the image to the client
                with open("mol_icon.png", "rb") as f:
                    imgData = f.read()
                self.wfile.write(imgData)

        else:
                self.send_response( 404 ) #if the file is not in the list of public files, send a 404 error
                self.end_headers()
                self.wfile.write( bytes( "404: not found", "utf-8" ) )


    def do_POST(self):
        if self.path == "/upload":
            length = int(self.headers["Content-Length"]) #find length of the uploaded file
            data = self.rfile.read(length) #save the file
            data = io.TextIOWrapper(io.BytesIO(data), encoding='utf-8')

            for i in range(4):
                data.readline()

            try:
                molname = self.headers.get('molname') #get the name of the molecule inputted
                db.add_molecule(molname, data) #add the molecule to the database
                self.send_response(200) #send a 200 response
            except:
                pass

        elif self.path == "/add":
            cgi.parse_header(self.headers["Content-Type"])
            form = cgi.FieldStorage( #get the data from the form
                fp=self.rfile,
                headers = self.headers,
                environ={'REQUEST_METHOD':'POST'}
            )

            #get the data from the form
            element = (form.getvalue("lnum"), form.getvalue("lcode"), form.getvalue("lname"), form.getvalue("colour1"), form.getvalue("colour2"), form.getvalue("colour3"), form.getvalue("radius"))

            try:
                db.__setitem__("Elements", element) #add the element to the database
                self.send_response(200)
            except:
                pass

        elif self.path == "/remove":
            cgi.parse_header(self.headers["Content-Type"])
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers = self.headers,
                environ={'REQUEST_METHOD':'POST'}
            )

            elementCode = form["removeel"].value

            try:
                db.__removeitem__("Elements", elementCode)
                self.send_response(200)
            except:
                pass

        elif self.path == "/display.html":
            MolDisplay.radius = db.radius() #get the radius of the atoms
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients() 

            molname = self.headers.get('molname')
            molecule = db.load_mol(molname) #load the molecule from the database using the selected name
            molecule.sort()
            with open(f"{molname}.svg", "w") as f: #write the molecule to a file as an svg
                f.write(molecule.svg())

            with open(f"{molname}.svg", "r") as f: 
                svgData = f.read().encode('utf-8')
            
            self.wfile.write(svgData) #send the svg to the client
            
            self.send_response(200)
            self.send_header("Content-type", "image/svg+xml")
            self.end_headers()
        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: not found", "utf-8" ) )

httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler ) #start the server
httpd.serve_forever() #run the server forever
