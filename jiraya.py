from jira import JIRA
from configparser import ConfigParser
from datetime import datetime

config = ConfigParser()
config.read('./config')

server = config['Jira']['server']
user = config['Jira']['user']
apikey = config['Jira']['apikey']
query = config['Filter']['query']
startdate = config['Filter']['startdate']
enddate = config['Filter']['enddate']

query += " AND resolutiondate >= " + startdate
query += " AND resolutiondate <= " + enddate

print(query)

options = {
    'server': server
}
jira = JIRA(options, basic_auth=(user,apikey))

issues = jira.search_issues(query, expand="changelog")

for issue in issues:
    inProgressDates = []
    doneDates = []
    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == 'status':
                if item.toString == 'In Progress':
                    inProgressDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    inProgressDates.append(inProgressDate)
                if item.toString == 'Done':
                    lastDoneDate = history.created
                    doneDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    doneDates.append(doneDate)


    if issue.fields.components:
        print(issue.fields.components[0].name)
    print(issue.key)

    firstInProgressDate = min(inProgressDates).strftime("%d %b %Y")
    lastDoneDate = max(doneDates).strftime("%d %b %Y")
    print("Start date: " + firstInProgressDate)
    print("End date: " + lastDoneDate)
    print("")

