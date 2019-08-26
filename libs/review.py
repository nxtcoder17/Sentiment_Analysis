#!/usr/bin/env python
# coding: utf-8

# In[2]:


import spacy
import re
from spacy.matcher import Matcher


# In[3]:


nlp = spacy.load ('en_core_web_sm')


# In[ ]:





# In[17]:


#######################################################################
### Every Review will be parsed as per this Review class            ###
#######################################################################

class Review:
    def __init__ (self):
        self.abbreviations = set ( "i.e. e.g. am mr mrs dr. prof. kg lbs cm in m mm ft".split() )
        self.stop_words = nlp.Defaults.stop_words
        if 'not' in self.stop_words:
            self.stop_words.remove ('not')
        # Removing adjectives fro
        self.stop_words = set (filter (lambda x: nlp(x)[0].pos != 84, self.stop_words))
        # This feature set would contain adjectives and verbs encountered throughout, the Reviews dataset
        self.features = set()
        
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
    
    def to_string (self, doc):
        """
            param:
                doc -> an nlp object ie. object of spacy.load() instance
        """
        if isinstance (doc, str):
            # Means, function got a string instead of a doc
            doc = nlp (doc)
        # doc.ents -> returns a tuple of spacy spans
        # spans -> returns tokens
        ne_indices = set()
        for span in doc.ents:
            for token in span:
                ne_indices.add (token.i)
        msg = []
        for token in doc:
            if token.text.lower() in self.stop_words:
                continue
            if token.i not in ne_indices:
                msg.append (str(token.text).lower())
            else:
                msg.append (token.text)
        return ' '.join(msg)
                
        
    def split_into_sentences (self, review):
        """
            While Splitting a big chunk of review, we need to take care of a few things first
            1. split on . (fullstops)
            2. Don't split if the (.) is a part of any standard abbreviation
            3. Split in case you found a conjunction joining the words, cause most of the time
               that sentence will convey 2 different sentiments, we don't want that for now.
            4. Drop Punctuations
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
                
            #### Also, we now need to build Feature List of Adjectives and Verbs and Adverbs, so
            ## 84: Adjectives | 100: verbs
            if (token.pos == 84 or token.pos == 100 or token.pos == 86) and token.text.lower() not in nlp.Defaults.stop_words:
                self.features.add (token.text.lower())
                
        if len (doc[start: ]) > 0:
            splits.append (doc[start: ])
        return splits
    
    def pre_process (self, msg):
        msg = self.remove_urls_hyperlinks (msg)
        sentences = self.split_into_sentences (msg)
        # return self.split_into_sentences (msg)
        return [self.to_string(span) for span in sentences]
    
    # For use in feature selection
    def pos (self, span):
        doc = nlp(span)
        return set([t.pos for t in doc])
        # return (token.pos, token.pos_, spacy.explain (token.tag_))


# In[18]:


if __name__ == '__main__':
    r = Review ()
    
    print ("Checking handling of NER")
    print (r.to_string ("Mr. Narendra Modi is the Prime minister of India."))
    
    msg = "Food was not tasty. It didn't taste good."
    for t in nlp(" ".join(r.pre_process(msg))):
        print (t.text, t.pos, t.pos_)
        
    for span in r.split_into_sentences ("Crust was not good."):
        for t in span:
            print (t, t.pos, t.pos_, t.tag_, spacy.explain (t.tag_))
            
    print (r.features)
    print ('not' in nlp.Defaults.stop_words)
            

