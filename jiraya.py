from jira import JIRA
from configparser import ConfigParser
from datetime import datetime
import csv

config = ConfigParser()
config.read('./config')

server = config['Jira']['server']
user = config['Jira']['user']
apikey = config['Jira']['apikey']
query = config['Filter']['query']
startdate = config['Filter']['startdate']
enddate = config['Filter']['enddate']
startstatuses = config['Statuses']['startstatuses'].split(',')
endstatuses = config['Statuses']['endstatuses'].split(',')

query += " AND resolutiondate >= " + startdate
query += " AND resolutiondate <= " + enddate

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
                if item.toString in startstatuses:
                    inProgressDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    inProgressDates.append(inProgressDate)
                if item.toString in endstatuses:
                    lastDoneDate = history.created
                    doneDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    doneDates.append(doneDate)


    issueKey = issue.key
    issueSummary = issue.fields.summary
    if issue.fields.components:
        issueComponentName = issue.fields.components[0].name
    else:
        issueComponentName = "Other"
    firstInProgressDate = min(inProgressDates).strftime("%d %b %Y")
    lastDoneDate = max(doneDates).strftime("%d %b %Y")

    csvOutput.append([issueComponentName, issueSummary, firstInProgressDate, lastDoneDate])

    print(issueKey)
    print(issueComponentName)
    print(issueSummary)
    print("Start date: " + firstInProgressDate)
    print("End date: " + lastDoneDate)
    print("")

outputFile = open('output.csv', 'w')
with outputFile:
    writer = csv.writer(outputFile)
    writer.writerows(csvOutput)
