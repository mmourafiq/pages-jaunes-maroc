# -*- coding: utf-8 -*-
'''
Created on Mar 01, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from bs4 import BeautifulSoup

import cPickle as pickle
import re
import random
import time
import urllib
import urllib2
import urlparse

url_base = "http://www.pj.ma/pagesjaunes?"

class PJ(object):
    """
        PJ object that executes queries and returns set of results
        
        URL templates to make PJ searches.
            http://www.pj.ma/pagesjaunes?page=2&pro_quiquoi=ophtalmologue&pro_ou=Casablanca
            http://www.google.com/search?
            page=page number
            &pro_quiquoi= object of search
            &pro_ou= location
    """
    def __init__(self, pause=5.0, page=1, query="", location=""):
        """
            @type  pause: long
            @param url: not to burden the server
            @type  page: int
            @param page: pagination 
            @type  query: str
            @param query: the object of the search
            @type  location: str
            @param location: where to look
        
            @rtype:  object
            @return: the instance of PJ
        """
        self.pause = pause
        self.page = page        
        self.query = query
        self.location = location
        
    def set_pause(self, pause):
        self.pause = pause

    def set_page(self, page = 0):        
        self.page = next if page > 0 else self.page + 1  
    
    def get_page(self):
        return self.page
    
    def set_query(self, query):
        self.query = query
    
    def set_location(self, location):
        self.location = location 
    
    def __url_contruction(self):
        """
        Construct the search url
        """                                  
        url_search = url_base
        #page
        page = "page=%(page)s&" % {"page":self.page}        
        url_search += page
        # pro_quiquoi        
        query = "pro_quiquoi=%(query)s&" % {"query":self.query}
        url_search += query
        # pro_ou
        location = "pro_ou=%(location)s&" % {"location":self.location}
        url_search += location
        return url_search        
        
    # Returns a generator that yields URLs.
    def search(self, file=None):
        """
        Returns search results for the current query as a iterator.                
        """            
        # pause, so as to not overburden PJ
        #time.sleep(self.pause+(random.random()-0.5)*5)                        
    
        # Prepare the URL of the first request.
        url_search = self.__url_contruction()
        print url_search
        # Request the PJ Search results page.
        stat = True
        while stat:
            try:
                html = self.__get_result(url_search)
                # Parse the response and extract the summaries
                soup = BeautifulSoup(html)
                if soup.findAll(text=re.compile("captcha")) != []:                    
                    print "Failed page "+self.get_page()+", captcha retrying"
                else:
                    stat = False
            except:
                print "Failed page "+self.get_page()+", retrying"
                time.sleep(4)            
        
        if soup.findAll(text=re.compile("cette recherche")) != []:
            print soup.findAll(text=re.compile("cette recherche"))
            return False
        
        for table in soup.findAll("li", {"class": "gauchezonebcenter"}):
            result = ""
            try :
                prof = ' '.join(re.findall('\w+', table.findNext("h2", {"class": "annoncesd-ttre"}).a.findNext(text=True)))                                  
                result += prof + ' | '
                activity = ' '.join(re.findall('\w+', table.findNext("div", {"class": "annoncesd-Activite"}).span.findNextSiblings(text=True)[0]))
                result += activity + ' | '
                address_phone = table.findNext("li", {"class": "annoncesd-adressec"})
                glo_address = address_phone.div.div
                address = ' '.join(re.findall('\w+', glo_address.next.string))
                result += address + ' | '
                city = ' '.join(re.findall('\w+', glo_address.strong.string))
                result += city + ' | '
                phones = address_phone.span.findNextSibling('strong')
                phone1 = ' '.join(re.findall('\w+', phones.string))                
                result += phone1 + ' | '
                phone2 = ' '.join(re.findall('\w+', phones.findNextSibling('strong').string))
                result += phone2 + ' | '                          
            except :
                pass
            pickle.dump(result, file)
        return True
    
        
    # Request the given URL and return the response page, using the cookie jar.
    def __get_result(self, url):
        """
        Request the given URL and return the response page, using the cookie jar.
    
        @type  url: str
        @param url: URL to retrieve.
    
        @rtype:  str
        @return: Web page retrieved for the given URL.
    
        @raise IOError: An exception is raised on error.
        @raise urllib2.URLError: An exception is raised on error.
        @raise urllib2.HTTPError: An exception is raised on error.
        """
        request = urllib2.Request(url)
        request.add_header('User-Agent',
                           'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0)')        
        response = urllib2.urlopen(request)        
        html = response.read()
        response.close()        
        return html

    
# When run as a script, take all arguments as a search query and run it.
if __name__ == "__main__":    
    prof = open("medecins.txt", "w")    
    query = 'medecin'
    pj = PJ()
    pj.set_query(query)
    stat = True        
    while stat:
        stat = pj.search(prof)
        pj.set_page()
    prof.close()
