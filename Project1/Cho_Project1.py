import pandas

# instructions:
# download Cho_Project1.py and nba_2020-2021.csv locally to the same directory
# run Cho_Project1.py as a Python file
# nba_2020-2021.json file will be written to same folder as the other files
# console will print summary if run was successful

# data downloaded from https://www.kaggle.com/umutalpaydn/nba-20202021-season-player-stats

# benchmark 1: ingest a local file that was downloaded in a CSV format
f = pandas.read_csv("nba_2020-2021.csv", encoding="ISO-8859-1")

# benchmark 3: modify the number of columns
f.drop(['FG', 'FGA', '3P', '3PA', '2P', '2PA', 'FT', 'FTA', 'ORB', 'DRB'], axis=1, inplace=True)
f.replace(['PG'], 'Point Guard', inplace=True)
f.replace(['SG'], 'Shooting Guard', inplace=True)
f.replace(['SF'], 'Small Forward', inplace=True)
f.replace(['PF'], 'Power Forward', inplace=True)
f.replace(['C'], 'Center', inplace=True)
f.rename(columns={'Pos': 'Position', 'Tm': 'Team', 'eFG%': 'FG%'}, inplace=True)

# benchmark 2/4: convert CSV file to JSON file and save the converted file locally
f.to_json("nba_2020-2021.json", orient='split')

# benchmark 5: generate brief summary of the data including number of records and number of columns
# try/catch block for error handling
try:
    with open('nba_2020-2021.json', 'r'):
        print("Summary: \n Records:" + str(len(f.axes[0])) + "\n Columns:" + str(len(f.axes[1])))
except FileNotFoundError:
    print("File Not Found")

