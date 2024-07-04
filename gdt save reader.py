#Function 
def releaseWeekToYear(releaseWeek):
    year = releaseWeek / 52

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    month = months[int(year % 1 *12)]

    return "{month}, {year}".format(month = month, year = 1980+int(year))

#Set locale for currency printing later
import locale
locale.setlocale(locale.LC_ALL, 'en_GB')



import sys
try:
    droppedFile = sys.argv[1] 
except IndexError:
    raise FileNotFoundError("No file inputted")



#Get data from sqlite file (sql database)
import sqlite3

sqlFilePath = droppedFile   

con = sqlite3.connect(sqlFilePath)
cur = con.cursor()
cur.execute("select cast(value as char) from ItemTable where key='slot_auto'")


jsonString = cur.fetchone()[0]

con.close()


#Get json data from the string from the sql database
import json

jsonData = json.loads(jsonString)

dataList = []

#Loop through the json data to get the best stuff outta there 
for game in jsonData['company']['gameLog']:
    dataListEntry = {}
    print(game["title"])
    dataListEntry["Title"] = game["title"]
    #sequelTo
    if "sequelTo" in game:
        sequelId = game["sequelTo"]
        for potentialSequel in jsonData['company']['gameLog']:
            if potentialSequel['id'] == sequelId:
                print("Sequel to: {}".format(potentialSequel['title']))
                dataListEntry["Sequel To"] = potentialSequel['title']
                break
    else:
        dataListEntry["Sequel To"] = ""
        

    print("Release time: {}".format(releaseWeekToYear(game["releaseWeek"])))
    dataListEntry["Release Date"] = releaseWeekToYear(game["releaseWeek"])

    print("A {topic} {genre} game".format(topic = game['topic'], genre = game['genre']))
    dataListEntry["Topic"] = game["topic"]
    dataListEntry["Genre"] = game["genre"]

    print("Platforms: {}".format(", ".join([x['id'] for x in game["platforms"]])))
    dataListEntry["Platform(s)"] = ", ".join([x['id'] for x in game["platforms"]])

    print("Size: {}".format(game["gameSize"]))
    dataListEntry["Size"] = game["gameSize"].capitalize()
    print("Audience: {}".format(game["targetAudience"]))
    dataListEntry["Audience"] = game["targetAudience"].capitalize()
    
    print("Review Score: {0:.1f}".format(game["score"]))
    dataListEntry["Review Score"] = game["score"]

    
    print("Cost: {}".format(locale.currency(game["costs"], grouping=True)))
    print("Revenue: {}".format(locale.currency(game["revenue"], grouping=True)))
    print("Profit: {}".format(locale.currency(game["revenue"] - game["costs"], grouping=True)))
    dataListEntry["Profit"] = game["revenue"] - game["costs"]
    dataListEntry["Cost"] = game["costs"]
    dataListEntry["Revenue"] = game["revenue"]

    print(" ")
    dataList.append(dataListEntry)


import pandas as pd
dataframe = pd.DataFrame(dataList)

import panel
formatters = {
    "Profit": {'type': 'money', 'symbol':'£'},
    "Cost": {'type': 'money', 'symbol':'£'},
    "Revenue": {'type': 'money', 'symbol':'£'},
    "Review Score": {'type': 'money', 'symbol':'/10', 'symbolAfter':True, 'precision':1},
}
pt = panel.widgets.Tabulator(dataframe, formatters = formatters, text_align={"Review Score":'center'})
pt.sortable = {"Release Date": False}
pt.hidden_columns = ["Revenue", "Cost"] 

pt.show_index = False
pt.disabled = True

pt.save("gdt save table.html")