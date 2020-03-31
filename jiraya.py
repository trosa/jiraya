from jira import JIRA
from configparser import ConfigParser

config = ConfigParser()
config.read('./config')

server = config['Jira']['server']
user = config['Jira']['user']
apikey = config['Jira']['apikey']

options = {
    'server': server
}

jira = JIRA(options, basic_auth=(user,apikey))

print(jira)
