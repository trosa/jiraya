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
startDate = config['Filter']['startdate']
endDate = config['Filter']['enddate']
startStatuses = config['Statuses']['startstatuses'].split(',')
endStatuses = config['Statuses']['endstatuses'].split(',')
csvHeaders = config['Output']['csvheaders'].split(',')

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
    if issue.fields.components:
        issueComponentName = issue.fields.components[0].name
    else:
        issueComponentName = "Other"
    if inProgressDates:
        firstInProgressDate = min(inProgressDates).strftime("%d %b %Y")
    else:
        firstInProgressDate = "none"
    if doneDates:
        lastDoneDate = max(doneDates).strftime("%d %b %Y")
    else:
        lastDoneDate = "none"

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
    writer.writerows([csvHeaders])
    writer.writerows(csvOutput)
