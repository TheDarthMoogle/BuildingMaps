#!/usr/bin/env python
# Script to create the Building Map svg Image for use in the website.

import svgwrite, psycopg2, sys	# svgwrite to draw the svg's,psycopg2 to handle the database connections and SQL and sys for sys.exit()

def main():
	createLog()
	# The script will collect array's of the building and floor ids from the database.
	floor_ids = getFloorId()
	building_ids = getBuildingID() 
	# The following section will iterate through each of the floors in each of the buildings as retrieved from the database
	for buildingID in building_ids:
		writeLog('-------------------## Building ' + str(buildingID) + ' ##-------------------\n')
		for floorID in floor_ids:
			writeLog('================## Floor ' + str(floorID) + ' ##================\n')
			# --------------
			record = pullRoom(floorID,buildingID) # This will call a function that will run SQL on the database for the current building/floor.
			if(len(record) == 0): # If the SQL returned no values then that will be noted in the log and the script will not run the rest of the script on the current floor.
				writeLog('No Rooms for the building_floor: ' + str(buildingID) + '_' + str(floorID) + '\n')
			else:
				# This is the processing if the floor contains some records.
				# ---------------------
				svgImg,bigGroup = createSVG(buildingID, floorID) # This creates the base svg file and stores it within svgImg (this will be the variable name used for storing the svg file throughout)
				svgImg = addOutline(buildingID, svgImg) # This will add the Building Outline to the svgImg
				# --------------------
				# Here will be the for loop to iterate through each room in the record array
				for room in record:
					roomID,roomName,coordinates,roomType = splitRecord(room) # This will split the values into the correct variables to be used by the scipt
					# -------------
					writeLog('## ---- ## Room ' + str(roomID) + ' ## ---- ##\n')
					fillColour = setFillColour(roomType,roomID) # Room ID is used for writing to the Log | function will set the correct fill colour based on Room Type.
					coordinates = rearrangeCoordinates(coordinates,roomName) # This will scale the coordinates, currently *8 ## Still want to change this to work from a variable rather than using a hardcoded value
					bigGroup = createObject(bigGroup,coordinates,fillColour,roomID,roomName,svgImg) # roomName is being passed so that it can be used by the createObject function to call the other searches to get the correct people and system image
					writeLog('The following room has been added to the Image: '+ roomName +'\n')
	
				svgImg.add(bigGroup)
				svgImg.save() # Save the Image at the end of the Script


# ----------------------------------------------------------------------------------------------------------------------
# SQL Queries
# This is where the SQL Queries functions are stored
def getBuildingID():
	dbconn = connectDatabase()
	dbcur = dbconn.cursor()
	try:
		dbcur.execute("""SELECT DISTINCT building_id FROM apps.building_maps_rooms_V1 WHERE building_id IS NOT NULL ORDER BY building_id ASC;""")
		#dbcur.execute('''SELECT building_id FROM building_hid;''')
		building_ids  = dbcur.fetchall()
	except:
		writeLog('ERROR: The script was not able to recover the building_id from the database so cannot iterate through, stopping script to stop error spamming\n')
		sys.exit()
	n = 0
	newArray = []
	for each in building_ids:
		current = int(building_ids[n][0])
		n = n + 1
		newArray.append(current)
	building_ids = newArray
	disconnectDatabase(dbconn)
	return building_ids

def getFloorId():
	dbconn = connectDatabase()
	dbcur = dbconn.cursor()
	try:
		dbcur.execute("""SELECT DISTINCT building_floor_id FROM apps.building_maps_rooms_V1 WHERE building_floor_id IS NOT NULL ORDER BY building_floor_id ASC;""")
		#dbcur.execute('''SELECT building_floor_id FROM building_floor_hid;''')
		floor_ids  = dbcur.fetchall()
	except:
		writeLog('ERROR: The script was not able to recover the building_floor_id from the database so cannot iterate through, stopping script to stop error spamming\n')
		sys.exit()
	n = 0
	newArray = []
	for each in floor_ids:
		current = int(floor_ids[n][0])
		n = n + 1
		newArray.append(current)
	floor_ids = newArray
	disconnectDatabase(dbconn)
	return floor_ids

def pullRoom(floorID,buildingID):
# Retrieve the data from an Open Database Connection
	dbconn = connectDatabase()
	dbcur = dbconn.cursor()
	try:
		dbcur.execute("""SELECT id,name,buildingmapscoordinates,room_type_id FROM apps.building_maps_rooms_V1 WHERE building_floor_id = %s AND building_id = %s AND buildingmapscoordinates IS NOT NULL;""",(floorID,buildingID))
		#dbcur.execute('''SELECT id,name,buildingmapscoordinates,room_type_id FROM room WHERE building_floor_id = %s AND building_id =%s AND buildingmapscoordinates IS NOT NULL;''' ,(floorID,buildingID))
		record = dbcur.fetchall()
		writeLog('SQL exected Correct to pull the infomation about the floor being searched\n') # When the SQL is written add in a brief desc of what the SQL did to the Log
		disconnectDatabase(dbconn)
		return record
	except:
		writeLog('ERROR: SQL command to retrieve the information from the Room Table failed to complete\n') # When it's written add a qualaifier so the write SQL can be debugged
		sys.exit()

def searchPeople(dbconn,roomID):
# Would be used to Dynamically Search the People table so that I can add People to Room Objects as I go.
	peopleCur = dbconn.cursor()
	try:
		# This will either be retrieved as an array or a string, need to set the value to be a array, this will allow for uniform seperation later.
		peopleCur.execute("""SELECT id FROM apps.building_maps_people_V1 WHERE room_id = %s;""",(str(roomID),))
		#peopleCur.execute('''SELECT person_id FROM mm_person_room WHERE room_id = %s;''' ,(str(roomID),))
		personCrsid = peopleCur.fetchall()
		#print(personCrsid)
		writeLog('The list of peoples ids for Room: ' + str(roomID) + ' has been retrieved\n') # Is this write strictly required
		n = 0
		newArray = []
		for person in personCrsid:
			currentCrsid = int(personCrsid[n][0])
			n = n + 1
			newArray.append(currentCrsid)
		personCrsid = newArray
		personCrsid = changeIdToCrsid(personCrsid,dbconn) # This is currently doing a complete list including Users who have already left. # ERROR IN HERE SOMEWHERE
		#print(personCrsid)
		crsids = arrayAsString(personCrsid) 
	except:
		roomID = str(roomID)
		writeLog('ERROR: The SQL to retrieve CRSIDs failed, the id of the room being searchd was: '+ str(roomID) + '\n')
	
	return crsids
		
def searchSystemImage(dbconn,roomID):
# Would be used to Dynamically search the System Image All table so that i can add People to Room Objects as I go
		systemImageCur = dbconn.cursor()
		try:
			# This will either be retrieved as an array or a string, need to se the value to be an array, this will allow for uniform seperation later.
			systemImageCur.execute("""SELECT name FROM apps.building_maps_hardware_V1 WHERE room_id = %s;""",(roomID,))
			#systemImageCur.execute('''SELECT name FROM hardware WHERE room_id = %s AND (hardware_type_id = 1 OR hardware_type_id = 2 OR hardware_type_id = 3 OR hardware_type_id = 4 OR hardware_type_id = 5);''' ,(roomID,))
			systemImageName = systemImageCur.fetchall()
			#print(systemImageName)
			# Going to need to place a for loop in here to convert to the array of tuples into an array of string
			n = 0
			newArray = []
			for hardware in systemImageName:
				if systemImageName[n][0] is None:
					writeLog('No Hardware Name in Database')
				else:
					currentHardwareObject = systemImageName[n][0]
					n = n + 1
					newArray.append(currentHardwareObject)
			writeLog('The list of Hardware Names has been sucessfully recovered for the following room: ' + str(roomID) +'\n') # Is this write stictly worth it??
			systemImage = arrayAsString(newArray) # This will force the script into a loop will will allow for the Hardware names to be seperated and added to the SVG before returning to this point.
		except:
			roomID = str(roomID) # This should be moved into it's own subroutine at some point, yes it will be a short sub routine :)
			writeLog('ERROR: The SQL to retrieve the HardwareNames failed, the id of the room being searchd was: '+ roomID + '\n')
		
		return systemImage

def arrayAsString(array):
	string = ', '.join(array)
	return string

# ----------------------------------------------------------------------------------------------------------------------
# THE SVG FILE
# This is where functions relating to the SVG file are being kept.
def addOutline(buildingID, svgImg):
	scale = 8
	if(buildingID == 1):
		# Main Building Outline
		outline = [(34*scale,-105*scale+800),(33*scale,-73*scale+800),(1*scale,-70*scale+800),(2*scale,-57*scale+800),(39*scale,-60*scale+800),(52*scale,-60*scale+800),(58*scale,-59*scale+800),(56*scale,-4*scale+800),(153*scale,-4*scale+800),(153*scale,-30*scale+800),(157*scale,-64*scale+800),(67*scale,-76*scale+800),(67*scale,-74*scale+800),(60*scale,-75*scale+800),(59*scale,-72*scale+800),(52*scale,-100*scale+800),(54*scale,-100*scale+800),(54*scale,-105*scale+800),(34*scale,-105*scale+800)]
	elif(buildingID == 2):
		# Unileaver Building Outline
		outline = [(0,0),(0,1),(1,1),(1,0)]
	elif(buildingID == 3):
		# 14 Union Rd Outline (Not Done)
		outline = [(0,0),(0,1),(1,1),(1,0)]
	elif(buildingID == 4):
		# SPRI
		outline = [(0,0),(0,1),(1,1),(1,0)]
	elif(buildingID == 5):
		# Engineering Outline (This will defiently not be used.)
		outline = [(0,0),(0,1),(1,1),(1,0)]
	elif(buildingID == 6):
		# West Cambridge Data Center (Unsure)
		outline = [(0,0),(0,1),(1,1),(1,0)]
	else:
		writeLog('Error: The ID for the building you are currently trying to outline does not exist. The ID that failed is: ' + buildingID + '\n')
		sys.exit()
	# End of make do switch section..
	outlinePath = svgImg.polyline(points=outline,stroke='black',stroke_width=3.5,fill='white')
	svgImg.add(outlinePath)
	
	return svgImg

def createObject(bigGroup,coordinates,fillColour,roomID,roomName,svgImg):
# Write a New object to the svg file
# Will need to use Polygon objects from svgwrite as this is the object type that is defined by a list of points
	
	#Create the Group Object to enclose the room object/information
	try:
		groupObject = svgImg.g(id=str(roomID) + '_room')
		roomObject = svgImg.polygon(points=coordinates,fill=fillColour,stroke='black',stroke_width=1)
		groupObject.add(roomObject)
		# ----------------------------------------------------------
		# This section will add the text objects	
		dbconn = connectDatabase()
		line1 = svgImg.text(text = roomName,opacity=0,insert=(0,0),style="font-family:'Dejavu Sans';font-size:14;")
		groupObject.add(line1)
		line2 = svgImg.text(text = (roomName + ' Hardware'),opacity=0,insert=(0,16),style="font-family:'Dejavu Sans';font-size:14;")
		groupObject.add(line2)
		#try:
		systemImageText = searchSystemImage(dbconn,roomID)
		#except:
			#systemImagetext = 'Unable to Retrieve'
		systemImageObject = svgImg.text(text=systemImageText,opacity=0,insert=(0,32),style="font-family:'Dejavu Sans';font-size=14:")
		groupObject.add(systemImageObject)
		line4 = svgImg.text(text = (roomName + ' People'),opacity=0,insert=(0,48),style="font-family:'Dejavu Sans';font-size=14:")
		groupObject.add(line4)
		#try:
		peopleText = searchPeople(dbconn,roomID)
		#except:
		#	peopleText = 'Unable to Retrieve'
		peopleObject = svgImg.text(text=peopleText,opacity=0,insert=(0,64),style="font-family:'Dejavu Sans';font-size:14;")
		groupObject.add(peopleObject)
		mid = findCenter(coordinates)
		roomName = svgImg.text(text=roomName,opacity=1,insert=mid,fill="rgb(178,76,63)",font_size="8px",style="font-family:'Dejavu Sans';")
		groupObject.add(roomName)
		
		# Add the Group to the svgImg object
		bigGroup.add(groupObject)
	
		disconnectDatabase(dbconn)
	except:
		writeLog('ERROR: The following Room did not add correctly: ' + roomName + '\n')
		
	return bigGroup # The function will be called by svgImg = createObject(....) This will be the append the object and keep the svgImg up to date.

def createSVG(buildingID,floorID):
# create the svg file
	floor = '/usr/local/building-maps/images/' + str(buildingID) + '_' + str(floorID) + '.svg'
	print(floor)
	svgImg = svgwrite.Drawing(filename = floor, size = ("1500px","1300px"))
	bigGroup = svgImg.g(id='floor_n')
	writeLog('The Base Image has been created for floor: ' + floor + '\n')
	
	return svgImg,bigGroup
	
def setFillColour(type, roomID):
# Sets the fill colour depending on the Room Type
	if (type == 21): # 21 is the ID for stairs
		fillColour = 'rgb(128,128,128)' # Set Fill Colour to Grey
	elif (type == 16): # 16 is the ID for Corridor
		fillColour = 'rgb(128,128,128)' # Set Fill Colour to Grey
	else: # For any other roomType
		fillColour = 'rgb(119,151,159)'	
		
	return fillColour	
	
# ----------------------------------------------------------------------------------------------------------------------
# THE DATABASE
# The following Functions Relate to Connecting and General Admin of the Database
# This doesn't include the SQL functions.
def connectDatabase():
# Open the database Connection
	try:
		dbconn = psycopg2.connect(host="database.ch.private.cam.ac.uk",database="chemistry",user="buildingmaps",password="bmbjtkynstaihiwtg")
		writeLog('Connected to the Database\n')
		return dbconn
	except:
		writeLog('ERROR: Failed to Connect to the Database, check connection and credentials\n')
		sys.exit()
	
def disconnectDatabase(dbconn):
# Close the Database Connection
	writeLog('Disconnected From Database\n')
	dbconn.close()

# ----------------------------------------------------------------------------------------------------------------------
# LOG FILE
# Functions relating to the Log File are stored in this Section. These include Create the Log and Write to the Log			
def writeLog(logMessage):
# Write a Messages to the Log File
	log = open('/usr/local/building-maps/building_map_log.txt','a') # When Move the Script to the UNIX webserver add the path to /var/log/
	log.write(logMessage)
	log.close()
	
def createLog():
	log = open('/usr/local/building-maps/building_map_log.txt','w')
	log.write('This is the Log for Building Maps Create Script\n')
	log.close()

# -----------------------------------------------------------------------------------------------------------------------
# GENERAL
# This is where the functions that don't really belong anywhere else are stored.
def splitRecord(record):
# Split the Record into it's seperate Components
	roomID = record[0]
	roomName = record[1]
	roomCoordinates = record[2]
	roomType = record[3]
	
	return roomID, roomName,roomCoordinates,roomType
	
def rearrangeCoordinates(coordinates,roomName):
	import retrieveCoord
	numCoords = len(coordinates) / 2
	if  numCoords == 4:
		coordinates = retrieveCoord.coords4(coordinates)
	elif numCoords == 5:
		coordinates = retrieveCoord.coords5(coordinates)
	elif numCoords == 6:
		coordinates = retrieveCoord.coords6(coordinates)
	elif numCoords == 7:
		coordinates = retrieveCoord.coords7(coordinates)
	elif numCoords == 8:
		coordinates = retrieveCoord.coords8(coordinates)
	elif numCoords == 9:
		coordinates = retrieveCoord.coords9(coordinates)
	elif numCoords == 10:
		coordinates = retrieveCoord.coords10(coordinates)
	elif numCoords == 11:
		coordinates = retrieveCoord.coords11(coordinates)
	elif numCoords == 12:
		coordinates = retrieveCoord.coords12(coordinates)
	elif numCoords == 13:
		coordinates = retrieveCoord.coords13(coordinates)
	elif numCoords == 14:
		coordinates = retrieveCoord.coords14(coordinates)
	elif numCoords == 15:
		coordinates = retrieveCoord.coords15(coordinates)
	else:
		writeLog('ERROR: Was not able to rearrange coordinats of the following room: ' + roomName + '\n')
	
	return coordinates
	
def changeIdToCrsid(idList, dbconn):
# This will take the list of person id's retrieved from the database and turn them into a list of crsid's
	nameList = []
	for id in idList:
		nameCur = dbconn.cursor()
		nameCur.execute("""SELECT DISTINCT first_names, surname FROM apps.building_maps_people_V1 WHERE id = %s;""" ,(id,))
		#nameCur.execute("""SELECT first_names, surname FROM person WHERE id = %s;""" ,(id,))
		names = nameCur.fetchall()
		#print(names)
		statusCur = dbconn.cursor()
		statusCur.execute("""SELECT DISTINCT status_id FROM apps.building_maps_people_V1 WHERE id = %s;""",(id,))
		#statusCur.execute("""SELECT status_id FROM _physical_status_v3 WHERE person_id = %s;""" ,(id,))
		status = statusCur.fetchall()
		status = status[0][0]
		#print(status) # THIS BIT DOESN'T WORK ANYMORE
		if (status == 'Current'): # THIS BIT DOESN'T WORK MORE
			nameList.append(names)
	newArray = []
	n = 0
	for name in nameList:
		name = name[0]
		currentName = ' '.join(name)
		newArray.append(currentName)
	writeLog('All the Names of the Active Members has been collated\n')
	finalList = newArray
	return finalList

def setRoomID_Name(roomID,roomType):
	# Change the type of the ID and Type Values
	roomID = int(roomID)
	roomType = int(roomType)
	return roomID,roomType
	
# ---------------------------------------------------------------	
def findTopLeft(points):
	left = 2000
	height = 2000
	for coord in points:
		if coord[0] < left:
			left = coord[0]
		
		if coord[1] < height:
			height = coord[1]
		
	topLeft = (left,height)
	return topLeft
	
def findBottomRight(points):
	right = 0
	height = 0
	for coord in points:
		if coord[0] > right:
			right = coord[0]
		
		if coord[1] > height:
			height = coord[1]
	bottomRight = (right,height)
	return bottomRight
	
def findCenter(coordinates):
	topLeft = findTopLeft(coordinates)
	bottomRight = findBottomRight(coordinates)
	x1, x2, y1, y2 = topLeft[0], bottomRight[0], topLeft[1], bottomRight[1]
	cx, cy = (x2 + x1)/2, (y2+y1)/2
	mid = ((cx-8),cy)
	return mid
	
# -----------------------------------------------------------------------------------------------------------------------

main()
