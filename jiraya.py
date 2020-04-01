from jira import JIRA
from configparser import ConfigParser

config = ConfigParser()
config.read('./config')

server = config['Jira']['server']
user = config['Jira']['user']
apikey = config['Jira']['apikey']
query = config['Filter']['query']

options = {
    'server': server
}

jira = JIRA(options, basic_auth=(user,apikey))

issues = jira.search_issues(query)

for issue in issues:
    print(issue.key)

