from bs4 import BeautifulSoup
import requests
import string
from googlesearch import search
import math
from stopwords import stopwords_list


stopwords = stopwords_list()


#change the number of relevant links to return 
RELEVANT_LINKS = 5
#number of files that match
FILE_MATCHES = 5
#number of sentences that match 
SENTENCE_MATCHES = 15

#question tokenizer i.e creates tokenized query in format for parser 
def tokenize(document): 
    words = document.split()
    #put in list and return list 
    return [word.lower() for word in words if word not in string.punctuation and word not in stopwords]


#parser takes tokenized query and uses scrapes results 
def query_builder(tokenized_query):     
    query = " ".join([word for word in tokenized_query]) + " wikipedia"
    return query 

#get all google search results
def get_links(query): 
    return [link for link in search(query, tld="co.in", num=RELEVANT_LINKS, start=0, stop=RELEVANT_LINKS, pause=0.1) if "wiki" in link]
    
        
#user web scraper to get data from links
def web_scraper(links):
    #iterate over list of links 
    documents = {}
    
    for link in links: 
        #add headers to make website think actual user
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

        #open each link 
        content = requests.get(link, headers=headers)
        #grab data 
        soup = BeautifulSoup(content.content,'html5lib')
        #only take paras 
        paragraphs = [str(para.get_text()) for para in soup.findAll('p')]

        text = [paragraph for paragraph in paragraphs]

        text = ' '.join(text)

        documents[link] = text
   
   
    return documents




 

    


def compute_idfs(documents):
    #documents is a dict with links and values are words in that document 
    number_of_documents = len(documents)

    idf_values = {}
    
    frequency = 0
    
    for data in documents.values(): 
        #check for frequency of each word in each document
        for word in data: 
            for data_words in documents.values():
                if word in data_words:
                    frequency += 1 
            idf_values[word] = math.log(number_of_documents/frequency)
            frequency = 0

    return idf_values


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    sentencesvalues = {}

    for sentence, words in sentences.items(): 
        querywords = query.intersection(words)

        value = 0 
        for word in querywords: 
            value += idfs[word]

        numwordsinquery = sum(map(lambda x: x in querywords, words))

        query_term_density = numwordsinquery/ len(words)

        sentencesvalues[sentence] = {
            'idf': value,
            'qtd': query_term_density, 
        }

    ranked_sentences = sorted(sentencesvalues.items(), key=lambda x: (x[1]['idf'], x[1]['qtd']), reverse=True)
    ranked_sentences = [x[0] for x in ranked_sentences]

    return ranked_sentences[:n]

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidf = {}

    for file in files.keys(): 
        tfidf[file] = 0

    #for each in the query set
    for word in query:
        for file, values in files.items(): 
            if word in values: 
                tfidf[file] += idfs[word] * values.count(word)

    querymatch = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)

    return ([element[0] for element in querymatch][:n])


def relevant_data(question):
    #tokenize the query 
    tokenized_query = tokenize(question)
    #format the query for search module 
    formatted_query = query_builder(tokenized_query)
    #get relevant links for search query
    links = get_links(formatted_query)
  
    #web scrape all related data from links in dict with link: data 
    documents = web_scraper(links)
   
    #tokenize all data in document key wise 
    file_words = {link: tokenize(data) for link, data in documents.items()}
   
    #idf scores
    file_idfs = compute_idfs(file_words)
   
    #Determine top file matches according to TF-IDF
    query = set(tokenized_query)
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()

    for filename in filenames:
        for passage in documents[filename].split("\n"):
            for sentence in passage.split('.'):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens
    
    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    
    matches = " ".join([str(sentence) for sentence in matches])
    return matches

