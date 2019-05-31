import psycopg2
# Script for the building maps project to dynamically create the webpages for the website. 

def main():
	buildings = getbuildinginfo() # Generate the Buildings data from the database
	listOfBuildings = getListOfBuildings(buildings) # change the Building data to a list of buildings
	for building in buildings:
		# Loop through the List of Buildings
		floors = getfloorinfo(int(building[2]))
		building,buildingname = getThisBuildingInfo(building)
		for floor in floors:
			# Loop through the list of floors for the current building.
			floor = getThisFloorInfo(floor)
			fileName = createFileName(buildingname,floor)
			scriptName = createScriptName(buildingname,floor)
			#print('-----------------------------')
			print(fileName)
			imageName = getImageName(building,floor)
			createBlankFile(fileName)
			createHead(fileName)
			createNav(fileName,listOfBuildings,buildings)
			createBody(building,fileName,floor,scriptName,imageName)
			createFooter(fileName)
	
def createFileName(buildingname, floor):
	# Create the filename for the webpage
	fileName = '/usr/local/building-maps/pages/' + buildingname + '/' + buildingname + '_' + floor.replace(" ","") + '.html'
	return fileName
	
def createScriptName(buildingname, floor):
	# Create the name of the script that is on the webserver to import the image
	fileName = '../../script/' + buildingname + '_' + floor.replace(" ","") + '.js'
	return fileName
	
def createBlankFile(fileName):
	# Creates the Blank File with the DOCTYPE set.
	page = open(fileName,'w')
	page.write('<!DOCTYPE html>\n')
	page.close()

def createHead(fileName):
	# Create the HTML head object and adds to the html file that has been created.
	page = open(fileName,'a')
	page.write('	<head>\n')
	page.write('		<meta charset="UTF-8">\n')
	page.write('		<title>Building Maps</title>\n')
	page.write('		<link rel="stylesheet" href="../../css/maps.css">\n')
	page.write('		<link rel="stylesheet" href="../../css/pageFormat.css">\n')
	page.write('		<link rel="stylesheet" href="../../css/dropdown.css">\n') # leaving sepearte from pageFormat because it's function is to create the  
	page.write('	</head>\n')
	page.close()
	
def createNav(fileName,listOfBuildings,buildings):
	# Create the HTML nav object and add to the html file that has been created. 
	page = open(fileName,'a')
	page.write('	<nav>\n')
	page.write('		<h1 id="h01">Nav Bar</h1>\n')
	page.write('		<p>Please use the following links to navigate to other pages</p>\n')
	page.write('		<a id="home" href="../../index.html">Home</a>\n')
	for currentBuilding in buildings:
		page.write('		<div class="dropdown">\n')
		page.write('			<p class="dropp">'+ currentBuilding[0] +'</p>\n')
		page.write('			<div class="dropdown-content">\n')
		floors = getfloorinfo(int(currentBuilding[2]))
		newListOfFloors = getListOfFloors(floors)
		for floor in newListOfFloors:
			page.write('				<a href="../' + currentBuilding[1] + '/' + currentBuilding[1] + '_' + floor.replace(" ","")  +'.html">'+ floor + '</a>\n')
		page.write('			</div>\n')
		page.write('		</div>\n')
	page.write('	</nav>\n')
	page.close()
	
def getbuildinginfo():
	# Collect the building data from the database
	dbconn = connectDatabase()
	dbcur = dbconn.cursor()
	dbcur.execute("""SELECT DISTINCT building_hid,email_abbreviation,building_id FROM apps.building_maps_rooms_V1 WHERE buildingmapscoordinates IS NOT NULL ORDER BY building_id ASC;""")
	record = dbcur.fetchall()
	buildings = record
	dbconn.close()
	return buildings
	
def getfloorinfo(building_id):
	# Collect the floor data from the database
	dbconn = connectDatabase()
	dbcur = dbconn.cursor()
	dbcur.execute("""SELECT DISTINCT building_floor_hid FROM apps.building_maps_rooms_V1 WHERE buildingmapscoordinates IS NOT NULL AND building_id = %s ORDER BY building_floor_hid ASC;""",(building_id,))
	record = dbcur.fetchall()
	floors = record
	dbconn.close()
	return floors

def createBody(building,fileName,floor,scriptName,imageName):
	page = open(fileName,'a')
	page.write('	<body>\n')
	page.write('		<h1 id="h_main">'+  building + ': ' + floor + ', Floor Plan</h1>\n')
	page.write('		<p>Please use the following floor plan to discover who and which hardware is located in which rooms on this floor</p>\n')
	page.write('		<div id="image">The Image has failed to Load, please inform support@ch.cam.ac.uk</div>\n')
	page.write('		<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js"></script>\n')
	page.write('		<script>$("#image").load("'+imageName+'");</script>\n')
	#page.write('		<script src="'+ scriptName +'"></script>\n') # This will need to link to the correct .js fie to load the image into the #div object. 
	page.write('	</body>\n')
	page.close()

def createFooter(fileName):
	page = open(fileName,'a')
	page.write('	<footer>\n')
	page.write('		<p>Chemistry Department Building Maps</p>\n')
	page.write('	</footer>\n')
	page.close()	

def connectDatabase():
	dbconn = psycopg2.connect(host='database.ch.private.cam.ac.uk', database="chemistry", user="buildingmaps", password='bmbjtkynstaihiwtg')
	return dbconn

def getThisBuildingInfo(buildings):
	building = buildings[0]
	buildingname = buildings[1]
	return building,buildingname

def getThisFloorInfo(floors):
	print(floors)
	floor = floors[0]
	return floor
	
def getListOfBuildings(buildings):
	listOfBuildings = []
	for building in buildings:
		buildingName = ''.join(building[0])
		listOfBuildings.append(buildingName)
	return listOfBuildings

def getListOfFloors(floors):
	listOfFloors = []
	for floor in floors:
		floorName = ''.join(floor[0])
		listOfFloors.append(floorName)
	return listOfFloors

def getImageName(building,floor):
	dbconn = connectDatabase()
	dbcur = dbconn.cursor()
	dbcur.execute("""SELECT DISTINCT building_id FROM apps.building_maps_rooms_V1 WHERE building_hid = %s;""",(building,))
	buildingID = dbcur.fetchall()
	buildingID = str(buildingID[0][0])
	dbconn.close()
	
	dbconn = connectDatabase()
	dbcur = dbconn.cursor()
	dbcur.execute("""SELECT DISTINCT building_floor_id FROM apps.building_maps_rooms_V1 WHERE building_floor_hid = %s;""",(floor,))
	floorID = dbcur.fetchall()
	floorID = str(floorID[0][0])
	dbconn.close()
	# Create the name of the script that is on the webserver to import the image
	imageName = '../../images/'+buildingID + '_' + floorID + '.svg'
	print(imageName)
	return imageName	
	
	
main()
