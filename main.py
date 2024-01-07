#Football Web Scraping
#Using mostly per 90 stats

from unidecode import unidecode
import requests
from bs4 import BeautifulSoup
import time
import operator


def getTeamUrls():
    Ligue1 = "https://fbref.com/en/comps/13/Ligue-1-Stats"
    SerieA = "https://fbref.com/en/comps/11/Serie-A-Stats"
    LaLiga = "https://fbref.com/en/comps/12/La-Liga-Stats"
    Bundesliga = "https://fbref.com/en/comps/20/Bundesliga-Stats"
    Championship = "https://fbref.com/en/comps/10/Championship-Stats"
    Eredivisie = "https://fbref.com/en/comps/23/Eredivisie-Stats"

    leaguesList = [Ligue1]
    leaguesCount = len(leaguesList) #number of leagues to be used
    combinedLeaguesURLS = [] #urls of teams

   
    for x in range (leaguesCount): #Adds all the teams' URL
        data = requests.get(leaguesList[x])
        soup = BeautifulSoup(data.text, features = "html.parser")

        standings_table = soup.select('table', class_='stats_table')[0]

        
        links = standings_table.find_all('a')

        links = [l.get("href") for l in links]

        #print(links)

        links = [l for l in links if '/squads/' in l]

        #print(links)

        teamURLS = [f"https://fbref.com{l}" for l in links]
        combinedLeaguesURLS += teamURLS

    return combinedLeaguesURLS

def createPlayerObjectNonGK(name, position, footed, birthdate, nationality,
                            club, stat1, stat2, stat3, stat4, stat5, stat6, stat7,
                              stat9, stat10, stat11, stat12, stat14,
                              stat15, stat17, stat18, stat19, stat20, stat21):
    new_player = {
        "name": name,
        "position": position,
        "footed": footed,
        "birthdate": birthdate,
        "nationality": nationality,
        "club" : club,
        "Non-Penalty Goals": stat1,
        "Non-Penalty xG(npxG)": stat2,
        "Shots Total": stat3,
        "Assists": stat4,
        "Expected Assisted Goals(xAG)": stat5,
        "npxG + xAG": stat6,
        "Shot-Creating Actions": stat7,
        "Passes Attempted": stat9,
        "Pass Completion %": stat10,
        "Progessive Passes": stat11,
        "Progessive Carries": stat12,
        "Successful Take-Ons": stat14,
        "Touches(Att Pen)": stat15,
        "Tackles": stat17,
        "Interceptions": stat18,
        "Blocks": stat19,
        "Clearances": stat20,
        "Aerials Won": stat21
    }
    return new_player

def createPlayerObjectGK(name, position, footed, birthdate, nationality, club, stat1, stat2, stat3, stat4, stat5,
                         stat6, stat8, stat9, stat10, stat11, stat13, stat14, stat15):
    new_player = {
        "name": name,
        "position": position,
        "footed": footed,
        "birthdate": birthdate,
        "nationality": nationality,
        "club": club,
        "Post-Shot Expected Goals minus Goals Allowed": stat1,
        "Goals Against": stat2,
        "Save Percentage": stat3,
        "Post-Shot Expected Goals per Shot on Target": stat4,
        "Saves% (Penality Kicks)": stat5,
        "Clean Sheet Percentage": stat6,
        "Touches": stat8,
        "Launch %": stat9,
        "Goal Kicks": stat10,
        "Average length of Goal Kicks": stat11,
        "Crosses Stopped %": stat13,
        "Defensive Actions Outside Penalty Area": stat14,
        "Average Distance of Defense Actions": stat15
    }
    return new_player


def normalizeName(name): #remove accents from names
    name = name.replace("-"," ")
    return unidecode(name)

def retrievePlayerStats(teamLinks):
    playersNonGK = []
    playersGKs = []
    for x in range(len(teamLinks)):
        data = requests.get(teamLinks[x])
        soup = BeautifulSoup(data.text, features = "html.parser")

        stats_table = soup.select('table.stats_table')[0]

        links = stats_table.find_all('a')
        links = [l.get("href") for l in links]

        links = [l for l in links if "/players/" in l and "/matchlogs/" not in l]
        #print(links)

        playerURLS = [f"https://fbref.com{l}" for l in links] #urls of players
        #print(playerURLS)

        for x in range((len(playerURLS)) - 24): #Choosing number of players
            parts = playerURLS[x].split("/")
            name = parts[-1]
            nameURL = name.replace("-", " ")
            #print(nameURL)

            data = requests.get(playerURLS[x])
            soup = BeautifulSoup(data.text, features = "html.parser")

            Name = soup.find_all("span")
            end = True
            counter = 0

            while (end):
                if nameURL in normalizeName(Name[counter].text):
                    Name = Name[counter].text
                    end = False
                else:
                    counter += 1

            #print(Name, end = " ")
            shortInfo = soup.find_all("p")
            end = True
            counter = 0

            while (end):
                if "Position" in shortInfo[counter].text:
                    shortInfo = shortInfo[counter].text
                    end = False
                else:
                    counter += 1

           
                    
            parts = shortInfo.split("▪ ")
            Position = parts[0].split(":")[1].strip()
            try:
                Footed = parts[1].split(":")[1].strip()
            except IndexError:
                Footed = None

            #print(Position, end = " ")
            # if (Footed == None):
            #     pass
            # else:
            #     print(Footed)
                
            Birthdate = soup.find_all("span", id = "necro-birth")
            Birthdate = Birthdate[0].text
            Birthdate = Birthdate.strip()
            #print(Birthdate)

            nationality = soup.find_all("p")
            end = True
            counter = 0

            while (end):
                if "National Team" in nationality[counter].text or "Citizenship" in nationality[counter].text:
                    nationality = nationality[counter].text
                    end = False
                else:
                    counter += 1

            nationality = nationality.split(":")
            NationalTeam = nationality[1].split(" ")
            NationalTeam = NationalTeam[0].strip()
            #print(NationalTeam, end = " ")


            clubInfo = soup.find_all("p")
            end = True
            counter = 0

            while (end):
                if "Club:" in clubInfo[counter].text:
                    clubInfo = clubInfo[counter].text
                    end = False
                else:
                    counter += 1


            clubInfo = clubInfo.split(":")
            Club = clubInfo[1].strip()
            #print(Club)

            if "GK" in Position:
                #print(Name)
                stats = soup.find_all("tr")
                stat1 = stats[1].text
                stat1 = stat1[7:12]
                #print(stat1)
                stat2 = stats[2].text
                stat2 = stat2[13:17]
                #print(stat2)
                stat3 = stats[3].text
                stat3 = stat3[15:19]
                #print(stat3)
                stat4 = stats[4].text
                stat4 = stat4[8:12]
                #print(stat4)
                stat5 = stats[5].text
                stat5 = stat5[21:25]
                #print(stat5)
                stat6 = stats[6].text
                stat6 = stat6[22:26]
                #print(stat6)
                stat8 = stats[8].text
                stat8 = stat8[7:12]                
                #print(stat8)
                stat9 = stats[9].text
                stat9 = stat9[8:13]               
                #print(stat9)
                stat10 = stats[10].text
                stat10 = stat10[10:14]                
                #print(stat10)
                stat11 = stats[11].text
                stat11 = stat11[25:29]
                #print(stat11)
                stat13 = stats[13].text
                stat13 = stat13[17:21]
                #print(stat13)
                stat14 = stats[14].text
                stat14 = stat14[30:34]
                #print(stat14)
                stat15 = stats[15].text
                stat15 = stat15[29:33]
                #print(stat15)

                playerObject = createPlayerObjectGK(Name, Position, Footed, Birthdate, NationalTeam,
                                                       Club, stat1, stat2, stat3, stat4,
                                                       stat5, stat6, stat8, stat9,
                                                       stat10, stat11, stat13, stat14, stat15)
                playersGKs.append(playerObject)                
                
            else:
                #print(Name)
                stats = soup.find_all("tr")
                stat1 = stats[1].text
                stat1 = stat1[17:21]
                #print(stat1)
                stat2 = stats[2].text
                stat2 = stat2[20:24]
                #print(stat2)
                stat3 = stats[3].text
                stat3 = stat3[11:15]
                #print(stat3)
                stat4 = stats[4].text
                stat4 = stat4[7:11]
                #print(stat4)
                stat5 = stats[5].text
                stat5 = stat5[28:32]
                #print(stat5)
                stat6 = stats[6].text
                stat6 = stat6[10:14]
                #print(stat6)
                stat7 = stats[7].text
                stat7 = stat7[21:25]
                #print(stat7)
                stat9 = stats[9].text
                stat9 = stat9[16:20]    
                #print(stat9)     
                stat10 = stats[10].text
                stat10 = stat10[17:22]
                #print(stat10)
                stat11 = stats[11].text
                stat11 = stat11[18:22]
                #print(stat11)
                stat12 = stats[12].text
                stat12 = stat12[19:23]
                #print(stat12)
                stat12 = stats[13].text
                stat12 = stat12[19:23]  
                #print(stat12) 
                stat14 = stats[14].text
                stat14 = stat14[17:21]  
                #print(stat14) 
                stat15 = stats[15].text
                stat15 = stat15[22:26]  
                #print(stat15)        
                stat17 = stats[17].text
                stat17 = stat17[7:11]  
                #print(stat17)     
                stat18 = stats[18].text
                stat18 = stat18[13:17]  
                #print(stat18)     
                stat19 = stats[19].text
                stat19 = stat19[6:10]  
                #print(stat19)     
                stat20 = stats[20].text
                stat20 = stat20[10:14]  
                #print(stat20)     
                stat21 = stats[21].text
                stat21 = stat21[11:15]  
                #print(stat21)              
            
                playerObject = createPlayerObjectNonGK(Name, Position, Footed, Birthdate, NationalTeam,
                                                       Club, stat1, stat2, stat3, stat4,
                                                       stat5, stat6, stat7, stat9, stat10,
                                                       stat11, stat12, stat14, stat15, stat17,
                                                       stat18, stat19, stat20, stat21)
                playersNonGK.append(playerObject)

            time.sleep(2)

    return playersNonGK, playersGKs


if __name__ == '__main__':
    print("main")

    teamUrls = getTeamUrls()
    #print(teamUrls)
    
    NonGKs, GKs = retrievePlayerStats(teamUrls[0:2])
    print("Data of all players from chosen leagues has been successfully collected, what would you like to do next?")

    statCategory = "Non-Penalty Goals" #the output will only show the category the user chooses to sort by, along with basic info
    statCategoryGK = "Save Percentage"

    while True:
        print("\nMain Menu")
        print("0. Quit and Export Data.\n1. Work with outfield players (no GKs).\n2. Work with goalkeepers.")
        userInput = int(input())

        if userInput == 0:
            break
        elif userInput == 1:
            print("\nSort by: ")
            print("0. Return to Main Menu\n1. Name\n2. Position\n3. Footed\n4. Non-Penalty Goals\n5. Non-Penalty xG(npxG)\n6. Shots Total")
            print("7. Assist\n8. Expected Assisted Goals(xAG)\n9. npXG + xAG\n10. Shot-Creating Actions\n11. Passes Attempted\n12. Pass Completion %")
            print("13. Progessive Passes\n14. Progessive Carries\n15. Successful Take-Ons\n16. Touches(Att Pen)\n17. Tackles\n18. Interceptions\n19. Blocks")
            print("20. Clearances\n21. Aerials Won")
            userInput = int(input())
            match userInput:
                case 1:
                    NonGKs = sorted(NonGKs, key=lambda player: player["name"])
                case 2:
                    NonGKs = sorted(NonGKs, key=lambda player: player["position"], reverse=True)
                case 3:
                    NonGKs = sorted(NonGKs, key=lambda player: player["footed"], reverse=True)
                case 4:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Non-Penalty Goals"], reverse=True)
                    statCategory = "Non-Penalty Goals"
                case 5:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Non-Penalty xG(npxG)"], reverse=True)
                    statCategory = "Non-Penalty xG(npxG)"
                case 6:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Shots Total"])
                    statCategory = "Shots Total"
                case 7:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Assists"], reverse=True)
                    statCategory = "Assists"
                case 8:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Expected Assisted Goals(xAG)"], reverse=True)
                    statCategory = "Expected Assisted Goals(xAG)"
                case 9:
                    NonGKs = sorted(NonGKs, key=lambda player: player["npxG + xAG"], reverse=True)
                    statCategory = "npxG + xAG"
                case 10:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Shot-Creating Actions"], reverse=True)
                    statCategory = "Shot-Creating Actions"
                case 11:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Passes Attempted"])
                    statCategory = "Passes Attempted"
                case 12:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Pass Completion %"], reverse=True)
                    statCategory = "Pass Completion %"
                case 13:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Progessive Passes"], reverse=True)
                    statCategory = "Progessive Passes"
                case 14:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Progessive Carries"], reverse=True)
                    statCategory = "Progessive Carries"
                case 15:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Successful Take-Ons"], reverse=True)
                    statCategory = "Successful Take-Ons"
                case 16:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Touches(Att Pen)"])
                    statCategory = "Touches(Att Pen)"
                case 17:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Tackles"], reverse=True)
                    statCategory = "Tackles"
                case 18:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Interceptions"], reverse=True)
                    statCategory = "Interceptions"
                case 19:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Blocks"], reverse=True)
                    statCategory = "Blocks"
                case 20:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Clearances"], reverse=True)
                    statCategory = "Clearances"
                case 21:
                    NonGKs = sorted(NonGKs, key=lambda player: player["Aerials Won"], reverse=True)
                    statCategory = "Aerials Won"
            
        elif userInput == 2:
            print("\nSort by: ")
            print("0. Return to Main Menu\n1. Name\n2. Post-Shot Expected Goals minus Goals Allowed\n3. Goals Against\n4. Save Percentage")
            print("5. Post-Shot Expected Goals per Shot on Target\n6. Saves% (Penalty Kicks)\n7. Clean Sheet Percentage\n8. Touches\n9. Launch%")
            print("10. Goal Kicks\n11. Average length of Goal Kicks\n12. Crosses Stopped %\n13. Defensive Actions Outside Penalty Area\n14. Average Distance of Defense Actions")
            userInput = int(input())
            match userInput:
                case 1:
                    GKs = sorted(GKs, key=lambda player: player["name"], reverse=True)
                case 2:
                    GKs = sorted(GKs, key=lambda player: player["Post-Shot Expected Goals minus Goals Allowed"], reverse=True)
                    statCategoryGK = "Post-Shot Expected Goals minus Goals Allowed"
                case 3:
                    GKs = sorted(GKs, key=lambda player: player["Goals Against"], reverse=True)
                    statCategoryGK = "Goal Against"
                case 4:
                    GKs = sorted(GKs, key=lambda player: player["Save Percentage"], reverse=True)
                    statCategoryGK = "Save Percentage"
                case 5:
                    GKs = sorted(GKs, key=lambda player: player["Post-Shot Expected Goals per Shot on Target"], reverse=True)
                    statCategoryGK = "Post-Shot Expected Goals per Shot on Target"
                case 6:
                    GKs = sorted(GKs, key=lambda player: player["Saves% (Penalty Kicks)"], reverse=True)
                    statCategoryGK = "Saves% (Penalty Kicks)"
                case 7:
                    GKs = sorted(GKs, key=lambda player: player["Clean Sheet Percentage"], reverse=True)
                    statCategoryGK = "Clean Sheet Percentage"
                case 8:
                    GKs = sorted(GKs, key=lambda player: player["Touches"], reverse=True)
                    statCategoryGK = "Touches"
                case 9:
                    GKs = sorted(GKs, key=lambda player: player["Launch %"], reverse=True)
                    statCategoryGK = "Launch %"
                case 10:
                    GKs = sorted(GKs, key=lambda player: player["Goal Kicks"], reverse=True)
                    statCategoryGK = "Goal Kicks"
                case 11:
                    GKs = sorted(GKs, key=lambda player: player["Average length of Goal Kicks"], reverse=True)
                    statCategoryGK = "Average length of Goal Kicks"
                case 12:
                    GKs = sorted(GKs, key=lambda player: player["Crosses Stopped %"], reverse=True)
                    statCategoryGK = "Crosses Stopped %"
                case 13:
                    GKs = sorted(GKs, key=lambda player: player["Defensive Actions Outside Penalty Area"], reverse=True)
                    statCategoryGK = "Defensive Actions Outside Penalty Area"
                case 14:
                    GKs = sorted(GKs, key=lambda player: player["Average Distance of Defense Actions"], reverse=True)
                    statCategoryGK = "Average Distance of Defense Actions"
        else:
            print("Invalid Choice.")
         




    print("STATS ARE LISTED IN VALUES PER 90 MINUTES PLAYED")
    print("-----------------NonGKs-----------------------------------")
    print(f"{'Name':<19}  {'Position':<23} {'Footed':<20} {'Birthdate':<20} {'Nationality':<15} {'Club':<22} {statCategory:<15}")
    
    for x in range (len(NonGKs)):
        print(f"{NonGKs[x]['name']:<20} {NonGKs[x]['position']:<23} {NonGKs[x]['footed']:<20} {NonGKs[x]['birthdate']:<20} {NonGKs[x]['nationality']:<15} {NonGKs[x]['club']:<22} {NonGKs[x][statCategory]:<15} ")


    print("-----------------GoalKeepers-----------------------------------")
    print(f"{'Name':<19}  {'Position':<23} {'Footed':<20} {'Birthdate':<20} {'Nationality':<15} {'Club':<22} {statCategoryGK:<15}")

    for x in range (len(GKs)):
        print(f"{GKs[x]['name']:<20} {GKs[x]['position']:<23} {GKs[x]['footed']:<20} {GKs[x]['birthdate']:<20} {GKs[x]['nationality']:<15} {GKs[x]['club']:<22} {GKs[x][statCategoryGK]:<15} ")