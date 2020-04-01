from jira import JIRA
from configparser import ConfigParser

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
    firstInProgressDate = ''
    lastDoneDate = ''
    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == 'status':
                if item.toString == 'In Progress':
                    firstInProgressDate = history.created
                if item.toString == 'Done':
                    lastDoneDate = history.created
    print(issue.key)
    print("Start date: " + firstInProgressDate)
    print("End date: " + lastDoneDate)
    print("")

