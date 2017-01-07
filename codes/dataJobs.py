__author__ = 'Yiyou'
import urllib2
import pandas as pd
import xml
import xml.etree.ElementTree as ET
import numpy as np

def getTotalResults(query):
    """Obtain total number of jobs given a query
    Inputs:
        string: query, seperated by +
    Outputs:
        int: indicating no. of total jobs of the query
    """

    #form url
    query = "\"" + query + "\""   #double quotes mean it's querying exact title
    url = "http://api.indeed.com/ads/apisearch?publisher=" + publisher_key + "&v=2&q="+query +"&l=&sort=&radius=&st=&jt=fulltime&start=0&limit=26&fromage=365&highlight=0&filter=&latlong=1&co=us&chnl=&userip=45.56.94.21&useragent=&v=2"

    #read website
    response = urllib2.urlopen(url)
    content = response.read()

    #parse XML
    root = ET.fromstring(content)
    num = int(root.find('totalresults').text)
    return num

def indeedrequest(query, start):
    """form the url using query and startNo
    Input:
        query: String, job title, using double quotes means exact wording in the title
        startNo : int, for mannually "turning page" as the indeed API has a restriction on number of jobs returned per query at 25
    Output:
        content: String, the XML file read from constructed API url
    """
    query = "\"" + query + "\""
    url = "http://api.indeed.com/ads/apisearch?publisher=" + publisher_key + "&v=2&q="+query +"&l=&sort=&radius=&st=&jt=fulltime&start="+str(start)+"&limit=26&fromage=365&highlight=0&filter=&latlong=1&co=us&chnl=&userip=45.56.94.21&useragent=&v=2"
    response = urllib2.urlopen(url)
    content = response.read()
    return(content)

def parseXMLtoDF(query, startNo):
    """parse xml file and then return a dataFrame of the 25 job results on the page
    Input:
        query: String, job title, using double quotes means exact wording in the title
        startNo : int, for mannually "turning page" as the indeed API has a restriction on number of jobs returned per query at 25
    Output:
        positionDB: a dataframe containing all job details from the XML page
    """

    #Read and parse XML file
    content = indeedrequest(query, startNo)
    root = ET.fromstring(content)

    #Iter through node result and store in dataframe
    position_nodes = root.iter('result') #obtain all 25 XML formated Job files as an iterator
    positionDB  = pd.DataFrame()

    for position_node in position_nodes: #iterate through 25 XML formatted jobs
        position = position_node.getchildren()  #obtain all tags and its content for one particular job

        #construct a row in the dataframe
        row = dict()
        for jd in position: #iterate through all tags
            row[jd.tag] = jd.text

        #append the row into positionDB
        positionDB = positionDB.append(row, ignore_index=True)

    return(positionDB)

def queryJobs(query):
    """Given a query, obtain all the job results as much as the API could return
    Input:
        query: String, job title, using double quotes means exact wording in the title
    Output:
        dataframe, containing all the job details and query
    """
    total = min(1025,getTotalResults(query))  #as the API has a constrain at 1025 records to return at maximum
    start = 0 # for mannually "turning page" as the indeed API has a restriction on number of jobs returned per query at 25

    jobs = []
    while(start <= total):
        jobs.append(parseXMLtoDF(query, start)) #append dataframe on each page to jobs
        start += 25 #"turn the page"
    allDf =  pd.concat(jobs) #concate all the dataframe to one
    allDf['query'] = query #record the query

    return allDf

def queryAllJobs(queries):
    """Given a list of queries, obtain all the job results as much as the API could return
    Input:
        queries: List of String, job title, using double quotes means exact wording in the title
    Output:
        dataframe, containing all the job details and query
    """
    dataJobs = []
    for i in queries:
        dataJobs.append(queryJobs(i));
    dataJobs = pd.concat(dataJobs)

    #drop duplicated record from the dataframe, given unique jobkey
    dataJobs = dataJobs.drop_duplicates(subset = "jobkey", keep = "first")
    return dataJobs

if __name__ == '__main__':
    publisher_key = ""
    data = ["data+scientist", "data+engineer","data+analyst", "business+analyst","marketing+analyst", "machine+learning"]
    queryAllJobs(data).to_csv("dataJobs.csv")   #This step takes one hour to process, so it's temporarily commented out