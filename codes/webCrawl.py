# -*- coding: utf-8 -*-
__author__ = 'Yiyou'

import sys
from bs4 import BeautifulSoup
import re
import pandas as pd
import urllib2
import nltk
reload(sys)
sys.setdefaultencoding('utf-8')

def webCrawl(url):
    """Given an indeed job url, return the whole text excluding script and style
    Input:
        url: String
    Output:
        content: String
    """
    try:
        html = urllib2.urlopen(url).read() # Connect to the job posting
    except:
        return ""


    soup = BeautifulSoup(html, "html.parser")

    # Reference for this step: https://jessesw.com/Data-Science-Skills/
    for script in soup(["script", "style"]):
        script.extract() # Remove these two elements from the BS4 object to get clean text
    content = soup.getText().lower()
    return content

def extractUseful (content):
    if type(content) == float: #i
        return "notok"
    else:
        content = content.replace("\r"," ").replace("\n", " ")
        startwords = ["qualification", "responsibilit", "require", "skill", "role", "experience", "demonstrat"]
        start = set([content.find(i) for i in startwords])
        if (-1 in start): #if doesn't find then it will be -1
            start.remove(-1)
        if (len(start) != 0): #if at least one of words is found
            start_pos = min(start)
            end_pos = content.find("days ago")-3 #end pos -3 is because we want to eliminate number if possible
            return  content[start_pos:end_pos]
        else:
            return "notok"

def process(text,  filters = nltk.corpus.stopwords.words('english')):
    """ Normalizes case and handles punctuation
    Inputs:
        text: str: raw text
        lemmatizer: an instance of a class implementing the lemmatize() method
                    (the default argument is of type nltk.stem.wordnet.WordNetLemmatizer)
    Outputs:
        list(str): tokenized text
    """
    lemmatizer=nltk.stem.wordnet.WordNetLemmatizer()
    word_list = nltk.word_tokenize(text);

    lemma_list = [];
    for i in word_list:
        if i not in filters:
            try:
                lemma = lemmatizer.lemmatize(i);
                lemma_list.append(str(lemma));
            except:
                pass
    return " ".join(lemma_list)


if __name__ == '__main__':
    #construct filter for processor
    file = open("accountant.txt").read().lower()
    filters = set(nltk.word_tokenize(file))
    filters.update(nltk.corpus.stopwords.words('english'))
    filters = list(filters)

    #webcrawling
    webContent = []
    dataJobs = pd.read_csv("dataJobs.csv");
    webContent = []
    for i in dataJobs["url"]:
        content = webCrawl(i);
        webContent.append(content);

    #clean the crawled text
    cleaned_list = []
    for j in webContent:
            cleaned = extractUseful(j);
            processed = process(cleaned, lemmatizer=nltk.stem.wordnet.WordNetLemmatizer());
            cleaned_list.append(processed)

    #save to csv
    contents = pd.DataFrame({ "Content":webContent, "Cleaned": cleaned_list})
    contents.to_csv("webcrawled.csv")


    dataJobs[['jd']]= cleaned_list
    dataJobs.to_csv("dataJobs_v2_crawled.csv")
