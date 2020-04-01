from jira import JIRA
from configparser import ConfigParser
from datetime import datetime
import numpy
import csv
#import sys
import argparse

config = ConfigParser()
config.read('./config')

server = config['Jira']['server']
user = config['Jira']['user']
apikey = config['Jira']['apikey']
query = config['Filter']['query']
category = config['Filter']['category']
startStatuses = config['Statuses']['startstatuses'].split(',')
endStatuses = config['Statuses']['endstatuses'].split(',')
csvHeaders = config['Output']['csvheaders'].split(',')

parser = argparse.ArgumentParser()
parser.add_argument("--start", type=datetime.fromisoformat, help="Start date for filter query. Format: YYYY-MM-DD")
parser.add_argument("--end", type=datetime.fromisoformat, help="End date for filter query. Format: YYYY-MM-DD")
args = parser.parse_args()

if args.start:
    startDate = args.start.strftime("%Y-%m-%d")
else:
    startDate = config['Filter']['startdate']

if args.end:
    endDate = args.end.strftime("%Y-%m-%d")
else:
    endDate = config['Filter']['enddate']

query += " AND resolutiondate >= " + startDate
query += " AND resolutiondate <= " + endDate

print(query)

options = {
    'server': server
}
jira = JIRA(options, basic_auth=(user,apikey))

issues = jira.search_issues(query, expand="changelog", maxResults=999)

csvOutput = []

for issue in issues:
    inProgressDates = []
    doneDates = []
    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == 'status':
                if item.toString in startStatuses:
                    inProgressDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    inProgressDates.append(inProgressDate)
                if item.toString in endStatuses:
                    lastDoneDate = history.created
                    doneDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    doneDates.append(doneDate)


    issueKey = issue.key
    issueSummary = issue.fields.summary
    if category == "components":
        if issue.fields.components:
            issueCategoryName = issue.fields.components[0].name
        else:
            issueCategoryName = "Other"
    else:
        if issue.fields.labels:
            issueCategoryName = issue.fields.labels[0]
        else:
            issueCategoryName = "Other"
    if inProgressDates:
        firstInProgressDate = min(inProgressDates)
        startDate = firstInProgressDate.strftime("%d %b %Y")
    else:
        firstInProgressDate = None
        startDate = "not found"
    if doneDates:
        lastDoneDate = max(doneDates)
        doneDate = lastDoneDate.strftime("%d %b %Y")
        doneWeekNumber = str(int(lastDoneDate.strftime("%W"))+1) #LOL
    else:
        lastDoneDate = None
        doneDate = "not found"
        doneWeekNumber = "not found"

    if firstInProgressDate and lastDoneDate:
        timeStart = firstInProgressDate.strftime("%Y-%m-%d")
        timeEnd = lastDoneDate.strftime("%Y-%m-%d")
        leadTime = numpy.busday_count(timeStart, timeEnd)
        leadTime += 1 # count stories started and finished on the same day as 1 day
        leadTime = str(leadTime)
    else:
        leadTime = "none"

    csvOutput.append([issueCategoryName, issueSummary, startDate, doneDate, doneWeekNumber, leadTime])

    print(issueKey)
    print(issueCategoryName)
    print(issueSummary)
    print("Start date: " + startDate)
    print("End date: " + doneDate)
    print("Done week: " + doneWeekNumber)
    print("Lead time: " + leadTime)

    print("")

outputFile = open('output.csv', 'w')
with outputFile:
    writer = csv.writer(outputFile)
    writer.writerows([csvHeaders])
    writer.writerows(csvOutput)
