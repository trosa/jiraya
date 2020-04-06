from jira import JIRA
from configparser import ConfigParser
from datetime import datetime
import numpy
import csv
#import sys
import argparse

config = ConfigParser()
config.read('./config')

jiraConfigs = config['Jira']
filterConfigs = config['Filter']
statuses = config['Statuses']

server = jiraConfigs['server']
user = jiraConfigs['user']
apikey = jiraConfigs['apikey']
query = filterConfigs['query']
category = filterConfigs['category']
startStatuses = statuses['startstatuses'].split(',')
reviewStatuses = statuses['reviewstatuses'].split(',')
signOffStatuses = statuses['signoffstatuses'].split(',')
endStatuses = statuses['endstatuses'].split(',')
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
    reviewDates = []
    signOffDates = []
    doneDates = []
    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == 'status':
                #Records status change date to In Progress
                if item.toString in startStatuses:
                    inProgressDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    inProgressDates.append(inProgressDate)
                #Records status change date to In Review / QA
                if item.toString in reviewStatuses:
                    lastReviewDate = history.created
                    reviewDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    reviewDates.append(reviewDate)
                #Records status change date to Sign Off
                if item.toString in signOffStatuses:
                    lastSignOffDate = history.created
                    signOffDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    signOffDates.append(signOffDate)
                #Records status change date to Done
                if item.toString in endStatuses:
                    lastDoneDate = history.created
                    doneDate = datetime.strptime(history.created.split("T")[0], "%Y-%m-%d")
                    doneDates.append(doneDate)


    issueKey = issue.key
    issueSummary = issue.fields.summary

    #Selects either Component or Label as issue category
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

    #Fetches the first In Progress date for the issue
    if inProgressDates:
        firstInProgressDate = min(inProgressDates)
        startDate = firstInProgressDate.strftime("%d %b %Y")
    else:
        firstInProgressDate = None
        startDate = "not found"

    #Fetches the last Review / QA date for the issue
    if reviewDates:
        lastReviewDate = max(reviewDates)
        reviewDate = lastReviewDate.strftime("%d %b %Y")
    else:
        lastReviewDate = None
        reviewDate = "not found"

    #Fetches the last Sign Off date for the issue
    if signOffDates:
        lastSignOffDate = max(signOffDates)
        signOffDate = lastSignOffDate.strftime("%d %b %Y")
    else:
        lastSignOffDate = None
        signOffDate = "not found"

    #Fetches the last Done date for the issue
    if doneDates:
        lastDoneDate = max(doneDates)
        doneDate = lastDoneDate.strftime("%d %b %Y")
        doneWeekNumber = str(int(lastDoneDate.strftime("%W"))+1) #LOL
    else:
        lastDoneDate = None
        doneDate = "not found"
        doneWeekNumber = "not found"

    if not firstInProgressDate:
        #Issue skipped In Progress and went straight to review
        if lastReviewDate:
            firstInProgressDate = lastReviewDate
        else:
            #Issue skipped both In Progress and Review and went straight to sign off
            if lastSignOffDate:
                firstInProgressDate = lastSignOffDate
            else:
                #Issue skipped all transitions and went straight to Done
                firstInProgressDate = lastDoneDate

    if firstInProgressDate and lastDoneDate:
        timeStart = firstInProgressDate.strftime("%Y-%m-%d")
        timeEnd = lastDoneDate.strftime("%Y-%m-%d")
        leadTime = numpy.busday_count(timeStart, timeEnd)
        leadTime += 1 # count stories started and finished on the same day as 1 day
        leadTime = str(leadTime)

        #if issue has passed through sign off
        if lastSignOffDate:
            signOffStart = lastSignOffDate.strftime("%Y-%m-%d")
        else:
            signOffStart = timeEnd

        #if issue has passed through review
        if lastReviewDate:
            reviewStart = lastReviewDate.strftime("%Y-%m-%d")
        else:
            reviewStart = signOffStart

        timeInProgress = numpy.busday_count(timeStart, reviewStart) + 1
        timeInReview = numpy.busday_count(reviewStart, signOffStart)
        timeInSignOff = numpy.busday_count(signOffStart, timeEnd)

    else:
        leadTime = "none"
        timeInProgress = "none"
        timeInReview = "none"
        timeInSignOff = "none"

    csvOutput.append([issueCategoryName, issueSummary, startDate, doneDate, doneWeekNumber, leadTime, timeInProgress, timeInReview, timeInSignOff])

    print(issueKey)
    print(issueCategoryName)
    print(issueSummary)
    print("Start date: " + startDate)
    print("Review date: " + reviewDate)
    print("Sign Off date: " + signOffDate)
    print("End date: " + doneDate)
    print("Done week: " + doneWeekNumber)
    print("Lead time: " + leadTime)

    print("")

outputFile = open('output.csv', 'w')
with outputFile:
    writer = csv.writer(outputFile)
    writer.writerows([csvHeaders])
    writer.writerows(csvOutput)
