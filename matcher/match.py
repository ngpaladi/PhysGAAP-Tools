# Mentor-Mentee Matching Code for PhysGAAP
# 2021
# To run:
# python matcher/match.py path/to/mentors.tsv path/to/mentees.tsv path/to/output.csv

import csv
import sys

BaseMatchScore = 10
StateMatchBonus = 10
NumCategories = 10

def MatchAny(mentor_values, mentee_values):
    for quary_val in [x.strip() for x in mentee_values.split(',')]:
        for test_val in [x.strip() for x in mentor_values.split(',')]:
            if quary_val == test_val:
                return True
    return False

def PairScore(mentor, mentee):
    score = 0

    for category in ["UndergradInstitution", "UndergradMajor", "GapYear", "GenderIdentity", "SexualOrientation", "EthnicBackground", "Disability", "FirstGeneration", "ResearchArea", "CountryOfOrigin"]:
        if MatchAny(mentor[category].lower(), mentee[category].lower()) or mentee[category] == "":
            score += BaseMatchScore + (NumCategories-int(mentee["Rank"+category]))
        else:
            if int(mentee["Rank"+category]) == 1 and "No" in mentee["NoTopPriorityOkay"]:
                return -1

    
    if "US" in mentee["CountryOfOrigin"].upper() and "US" in mentor["CountryOfOrigin"].upper() and MatchAny(mentor["CountryOfOrigin"].lower(), mentee["CountryOfOrigin"].lower()):
        score += StateMatchBonus

    return score





csv_labels_mentor = {
    "FirstName": 18,
    "LastName": 19,
    "Email": 17,
    "UndergradInstitution": 22,
    "UndergradMajor": 23,
    "GapYear": 29,
    "GenderIdentity": 32,
    "SexualOrientation": 34,
    "EthnicBackground": 35,
    "FirstGeneration": 37,
    "Disability": 38,
    "Citizenship": 39,
    "CountryOfOrigin": 40,
    "StateOfOrigin":41,
    "ResearchArea": 30,
    "NumberMentees": 42
}
csv_labels_mentee = {
    "FirstName": 18,
    "LastName": 19,
    "Email": 17,
    "UndergradInstitution": 23,
    "UndergradMajor": 24,
    "GapYear": 30,
    "GenderIdentity": 31,
    "SexualOrientation": 33,
    "EthnicBackground": 35,
    "FirstGeneration": 37,
    "Disability": 38,
    "Citizenship": 39,
    "CountryOfOrigin": 40,
    "StateOfOrigin":41,
    "ResearchArea": 43,
    "ApplyThisYear": 59,
    "RankUndergradInstitution": 46,
    "RankUndergradMajor": 47,
    "RankGapYear": 48,
    "RankGenderIdentity": 49,
    "RankSexualOrientation": 50,
    "RankEthnicBackground": 51,
    "RankFirstGeneration": 52,
    "RankDisability": 53,
    "RankCountryOfOrigin": 54,
    "RankResearchArea": 55,
    "NoTopPriorityOkay": 57
}

mentor_csv = str(sys.argv[1])
mentee_csv = str(sys.argv[2])
output_csv = str(sys.argv[3])


mentors = []
mentees = []

with open(mentor_csv, newline='', encoding="utf16", errors='ignore') as mentor_file:
    mentor_reader = csv.reader(mentor_file, delimiter="\t", quotechar='"')
    for row in mentor_reader:
        if(not "@" in row[csv_labels_mentor["Email"]]):
            continue
        mentor = {}
        for key in csv_labels_mentor:
            mentor[key] = row[csv_labels_mentor[key]]

        if "Professional" in mentor["FirstGeneration"] or "Doctorate" in mentor["FirstGeneration"]:
            mentor["FirstGeneration"] = "Yes"
        else:
            mentor["FirstGeneration"] = "No"

        if "Yes" in mentor["Citizenship"] and mentor["CountryOfOrigin"] == "":
            mentor["CountryOfOrigin"] = "US"

        mentors.append(mentor)

print("Loaded Mentors ...")

with open(mentee_csv, newline='', encoding="utf16", errors='ignore') as mentee_file:
    mentee_reader = csv.reader(mentee_file, delimiter="\t", quotechar='"')
    for row in mentee_reader:
        if(not "@" in row[csv_labels_mentee["Email"]]):
            continue
        if(not "Yes" in row[csv_labels_mentee["ApplyThisYear"]]):
            continue
        mentee = {}
        for key in csv_labels_mentee:
            mentee[key] = row[csv_labels_mentee[key]]

        if "Professional" in mentee["FirstGeneration"] or "Doctorate" in mentee["FirstGeneration"]:
            mentee["FirstGeneration"] = "Yes"
        else:
            mentee["FirstGeneration"] = "No"

        if "Yes" in mentee["Citizenship"] and mentee["CountryOfOrigin"] == "":
            mentee["CountryOfOrigin"] = "US"

        mentees.append(mentee)

print("Loaded Mentees ...")

best_pairings = []
best_score = 0

print("Starting Matching ...")

for start in range(len(mentees)):
    for mentor in mentors:
        mentor["NumberMenteesRemaining"] = int(mentor["NumberMentees"])
    pairings = []
    score = 0
    for offset in range(len(mentees)):
        i = (offset + start) % (len(mentees))

        best_mentor_match = -1
        best_match_score = 0
        for j in range(len(mentors)):
            if(mentors[j]["NumberMenteesRemaining"] == 0):
                continue
            match_score = PairScore(mentors[j], mentees[i])
            if match_score >= best_match_score:
                best_match_score = match_score
                best_mentor_match = j
            
        if(best_mentor_match >= 0):
            pairings.append((best_mentor_match, i, best_match_score))
            score += best_match_score
            mentors[best_mentor_match]["NumberMenteesRemaining"] -= 1

    if score > best_score or (score == best_score and len(pairings) > len(best_pairings)):
        best_pairings = pairings
        best_score = score
        print("Made %d Pairs with Total Score %d ... New Best!!" % (len(pairings), score))
    else:
        print("Made %d Pairs with Total Score %d ..." % (len(pairings), score))

print("Writing Optimal Pairings to: %s ..." % (output_csv))
with open(output_csv, 'w', newline='') as output_csv_file:
    output_writer = csv.writer(output_csv_file, delimiter=",")
    output_writer.writerow(['Mentee Email', 'Mentee First Name', 'Mentee Last Name', 'Mentor Email', 'Mentor First Name', 'Mentor Last Name', 'Score'])

    for pairing in best_pairings:
        output_writer.writerow([mentees[pairing[1]]["Email"], mentees[pairing[1]]["FirstName"], mentees[pairing[1]]["LastName"], mentors[pairing[0]]["Email"], mentors[pairing[0]]["FirstName"], mentors[pairing[0]]["LastName"], pairing[2]])

print("Done!")
    




        

