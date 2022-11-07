import string
import spacy 

# Text Processing Class 
class PreProcessText(object):
    def __init__(self):
        pass

    nlp = spacy.load("en_core_web_sm")
    stopwords = nlp.Defaults.stop_words

    def __remove_punctuation(self, text):
        """
        Takes a String
        return : Return a String
        """
        message = []
        for x in text:
            if x in string.punctuation:
                pass
            else:
                message.append(x)
        message = ''.join(message)

        return message

    def __remove_stopwords(self, text):
        """
        Takes a String
        return List
        """
        words= []
        for x in text.split():

            if x.lower() in self.stopwords:
                pass
            else:
                words.append(x)
        return words

    def token_words(self,text=''):
        message = self.__remove_punctuation(text)
        words = self.__remove_stopwords(message)
        return words