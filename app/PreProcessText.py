import string
import spacy 
import re 
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer,PorterStemmer
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer() 
from nltk.corpus import stopwords

nlp = spacy.load('en_core_web_sm')

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

    def preprocess(self, sentence):
        sentence=str(sentence)
        #sentence = sentence.lower()
        sentence=sentence.replace('{html}',"") 
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', sentence)
        rem_url=re.sub(r'http\S+', '',cleantext)
        rem_num = re.sub('[0-9]+', '', rem_url)
        print("Cleaner Txt:", cleantext)

        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(rem_num)  
        filtered_words = [w for w in tokens if len(w) > 2 if not w in stopwords.words('english')]
        stem_words=[stemmer.stem(w) for w in filtered_words]
        lemma_words=[lemmatizer.lemmatize(w) for w in stem_words]
        return " ".join(filtered_words)

    def get_sentences(self, article_text):
        #sentences = re.split(r' *[\.\?!][\'"\)\]]* *', content)
        about_doc = nlp(article_text)
        sentences = list(about_doc.sents)
        return sentences


    def token_words(self,text=''):
        message = self.__remove_punctuation(text)
        words = self.__remove_stopwords(message)
        return words