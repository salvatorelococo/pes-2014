# CSV Mappers

All scripts inside this folder generate CSV files.

Filename | Content of generated CSV 
---------|-------------
all_in_one_mapper.py | All info contained in all other scripts inside this folder (multiple CSVs).
champions_league_mapper.py | `ID`, `team name abbr.`, `team name`, `group`, `bytes sequence` for all of the teams included in the Champions League.
names_mapper.py | `team name abbr.`, `team name`, `byte positions (team name abbr., team name, end of sequence)`.
players_mapper.py | `ID`, `name`, `bytes sequence`.
teams_mapper.py | `ID`, `team name abbr.`, `team name`, `group`, `bytes sequence`.
