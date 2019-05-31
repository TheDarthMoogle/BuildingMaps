#!/bin/sh
# Start of Script
# -----------------------------------------------------------------------
# Prepare the web server for the new files to be added to.
# Become Root
#sudo bash

# Remove the Old Files
rm /usr/local/building-maps/pages/ -R

# Recreate the blank directory structure
mkdir /usr/local/building-maps/pages/
mkdir /usr/local/building-maps/pages/cmi/
mkdir /usr/local/building-maps/pages/main/
mkdir /usr/local/building-maps/pages/spri/
mkdir /usr/local/building-maps/pages/atm/

# Remove the image directory
rm /usr/local/building-maps/images/ -R

# Recreate the image directory
mkdir /usr/local/building-maps/images/

# Leave Root
#exit
# ----------------------------------------------------------------------
# Create the new Files
# Run the Two Files to create the output
python /usr/local/building-maps/scripts/createSVG.py
python /usr/local/building-maps/scripts/createWeb.py
python /usr/local/building-maps/scripts/createIndex.py
# ----------------------------------------------------------------------
# Move the New Files to the webserver.
# Become Root
#sudo bash

# Remove Files from the Server
rm /var/www/html/buildingmaps/pages -R
rm /var/www/html/buildingmaps/images -R
rm /var/www/html/buildingmaps/index.html

# Might need to change the Origin Locstions of the files
# Move the created files to the correct locations
cp /usr/local/building-maps/pages/ /var/www/html/buildingmaps/ -R
cp /usr/local/building-maps/images/ /var/www/html/buildingmaps/ -R
cp /usr/local/building-maps/index.html /var/www/html/buildingmaps/


# Leave Root
#exit

# End of Script
# ----------------------------------------------------------------------
# ads81 - Shell Script to run the Python scripts.
#           - Remove the Populated Directory's and Create the blank directory,
#           - Populate the blank directory's,
