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

for issue in issues:
    print(issue.key)
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


    if issue.fields.components:
        print(issue.fields.components[0].name)

    firstInProgressDate = min(inProgressDates).strftime("%d %b %Y")
    lastDoneDate = max(doneDates).strftime("%d %b %Y")
    print("Start date: " + firstInProgressDate)
    print("End date: " + lastDoneDate)
    print("")

