import re
import string

import spacy
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer() 
from nltk.corpus import stopwords

nlp = spacy.load('en_core_web_sm')

# Text Processing Class 
class PreProcessText(object):
    def __init__(self):
        pass

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

    def preprocess_text(self, sentence):
        sentence=str(sentence)
        sentence = sentence.lower()
        # HTML CLEAN 
        sentence=sentence.replace('{html}',"") 
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', sentence)
        rem_url=re.sub(r'http\S+', '',cleantext)
        # Number Clean
        rem_num = re.sub('[0-9]+', '', rem_url)
        print("Cleaner Txt:", cleantext)
        #text = re.sub(r"[-()\"#/@;:<>{}=~|.?,]", "", text)

        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(rem_num)  
        filtered_words = [w for w in tokens if len(w) > 2 if not w in stopwords.words('english')]
        #stem_words=[stemmer.stem(w) for w in filtered_words]
        lemma_words=[lemmatizer.lemmatize(w) for w in filtered_words]
        return " ".join(lemma_words)
    
    def clean_text(self, article_text): 
        rem_num = re.sub('[0-9]+', '', article_text)
        #print("Cleaner Text: ", article_text, rem_num)
        return rem_num

    def get_sentences(self, article_text):
        #sentences = re.split(r' *[\.\?!][\'"\)\]]* *', article_text)
        about_doc = nlp(article_text)
        sentences = list(about_doc.sents)
        print ('Sentences : ', sentences)
        return sentences

    def token_words(self,text=''):
        message = self.__remove_punctuation(text)
        words = self.__remove_stopwords(message)
        return words
    
    def search_sentence(self, sentence, article_text):
        start_i = 0
        end_i = 0
        steps = 5000
        print ('Size of Article : ', len(article_text))
        for i in range(start_i, len(article_text), steps):
            end_i += steps
            res = None
            try: 
                res = re.search(sentence, article_text[start_i:end_i]) # TODO Revisite                 
            except IndexError:
                print("IndexError")
            except re.error:
                print("re.error")   
            finally:    
                if res is not None:
                    found_start = start_i + res.start()
                    found_end = start_i + res.end()                    
                    print('Found : ', found_start, found_end)
                    return found_start, found_end
                start_i += steps
        return None, None
                
