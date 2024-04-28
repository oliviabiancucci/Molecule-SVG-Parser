import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import MolDisplay
import io

class MyHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == "/":
			self.send_response( 200 ); #OK
			self.send_header( "Content-type", "text/html" )
			self.send_header( "Content-length", len(home_page) ) #length of the homepage
			self.end_headers()

			self.wfile.write( bytes( home_page, "utf-8" ) ) #send the homepage html

		else:
			self.send_response( 404 ) #ERROR
			self.end_headers()
			self.wfile.write( bytes( "404: not found", "utf-8" ) )

	def do_POST(self):
		if self.path == "/molecule":
			self.send_response( 200 )
			self.send_header( "Content-type", "image/svg+xml" )
			self.end_headers()

			length = int(self.headers["Content-Length"]) #find length of the uploaded file
			data = self.rfile.read(length) #save the file
   
			data = io.TextIOWrapper(io.BytesIO(data), encoding='utf-8')
			for i in range(4):
				data.readline()
    
			molecule = MolDisplay.Molecule() #create a new molecule
			molecule = molecule.parse(data) #parse the file
			molecule.sort() #sort the molecule
			svgMolecule = molecule.svg() #create the svg
			self.wfile.write(svgMolecule.encode()) #send the svg

		else:
			self.send_response( 404 )
			self.end_headers()
			self.wfile.write( bytes( "404: not found", "utf-8" ) )


home_page = """
<html>
	<head>
		<title> File Upload </title>
	</head>
	<body>
		<h1> File Upload </h1>
		<form action="molecule" enctype="multipart/form-data" method="post">
			<p>
				<input type="file" id="sdf_file" name="filename"/>
			</p>
			<p>
				<input type="submit" value="Upload"/>
			</p>
		</form>
	</body>
</html>
"""

httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler ) #create a server
httpd.serve_forever() #run the server
