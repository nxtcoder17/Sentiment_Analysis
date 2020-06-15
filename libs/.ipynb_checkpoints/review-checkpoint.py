#!/usr/bin/env python
# coding: utf-8

# In[1]:


import spacy
import re
from spacy.matcher import Matcher


# In[2]:


nlp = spacy.load ('en_core_web_sm')

#######################################################################
### Every Review will be parsed as per this Review class            ###
#######################################################################

class Review:
    def __init__ (self):
        self.abbreviations = set ( "i.e. e.g. am mr mrs dr. prof. kg lbs cm in m mm ft".split() )
        
    def remove_urls_hyperlinks (self, review):
        pattern = r"\s*(http[s]?:[/]{2}www[.])?([a-z0-9]+)[.]([a-z]{3})([/][A-Za-z0-9?='.]*)*\s*"
        
        """
        Pattern matched below urls and hyperlinks, i guess it works for now
            http://www.google.com 
            https://www.google.com
            www.google.com
            google.com 
            zomato.com
            zomato.com/
            zomato.com/items/this?dir=hello
            https://www.zomato.com/places/NewDelhi/bbqnation/12.html
        """
        return re.sub (pattern, '', review)
        
        
    def token_merge (self, doc):
        # patterns for can't, didn't shouldn't wouldn't wasn't
        verb_patterns = [
            [{"TEXT": {"REGEX": r"ca|did|should|would|was"}}, {"LOWER": "n't"}],
        ]
        matcher = Matcher (nlp.vocab)
        matcher.add ('neg_verbs', None, *verb_patterns)
        for _,start,end in matcher (doc):
            span = doc[start: end]
            span.merge()
        
        return doc
        
    def split_into_sentences (self, review):
        """
            While Splitting a big chunk of review, we need to take care of a few things first
            1. split on . (fullstops)
            2. Don't split if the (.) is a part of any standard abbreviation
            3. Split in case you found a conjunction joining the words, cause most of the time
               that sentence will convey 2 different sentiments, we don't want that for now.
        """
        doc = nlp (review)
        doc = self.token_merge (doc)
        start = 0
        splits = []
        for token in doc:
            # print (token, end=' # ')
            ## Step 1:
            if token.text.strip() == '.':
                # Step 2: Check for previous token being an Abbreviation
                if (token.i-1) >= 0 and doc[token.i - 1].text.lower() in self.abbreviations:
                    pass
                else:
                    splits.append (doc[start: token.i])
                    start = token.i + 1
            # Step 3: Splitting on Conjunctions or ADP
            elif token.pos == 89:
                splits.append (doc[start: token.i])
                start = token.i + 1
                
        if len (doc[start: ]) > 0:
            splits.append (doc[start: ])
        return splits
    
    def pre_process (self, msg):
        msg = self.remove_urls_hyperlinks (msg)
        return self.split_into_sentences (msg)