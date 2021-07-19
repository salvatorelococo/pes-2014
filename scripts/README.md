# Scripts folder

Here you will find the **code**.

filename            | description
--------------------|-------------
multi_unzlib.py     | Tool to extract uncompressed content from all zlib files in a folder. Adapted for PES headers.
names_scraper.py    | Inspects the ID00015 file and generate a .csv file with team names, team abbreviations and their position.
names_structure.py  | Contains info about the structure of ID00015.
names_updater.py    | Using an edited version of a .csv generated with names_scraper.py this script updates the ID00015 file. 
teams_scraper.py    | Inspects the ID00015 file and generates two .csv files: one containing info about nationalities and another one containing info about teams.
