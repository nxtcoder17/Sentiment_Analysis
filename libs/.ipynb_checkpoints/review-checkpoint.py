#######################################################################
### Every Review that we will parse will be an object of this class ###
#######################################################################

class Review:
    def __init__(self, review):
        self.review = review
        
    def split_into_sentences (self):
        """
            Alert: Prior to splitting, we need to make sure [.] encountered is not a part of a URL (http/https/www or domain names etc)
        """
        """
            This splitter pattern would split into sentences on account of 
                word.
                word .
                word .      abc         # Here, it will consume whitespace too b/w . and abc
        """
        split_pattern = r"([A-Za-z]+)\s*[.,](\s*)"
