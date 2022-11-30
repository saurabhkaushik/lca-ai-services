import re
import string
import pytextrank # TextRank 

import spacy
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

class PreProcessText(object):
    nlp = spacy.load('en_core_web_md')
    nlp.add_pipe("textrank")

    def __init__(self):
        pass

    stopwords = nlp.Defaults.stop_words
    tokenizer = RegexpTokenizer(r'\w+')

    def get_nlp(self): 
        return self.nlp

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
        words = []
        for x in text.split():

            if x.lower() in self.stopwords:
                pass
            else:
                words.append(x)
        return words

    def preprocess_text(self, sentence):
        sentence = str(sentence)
        sentence = sentence.lower()
        # HTML CLEAN
        sentence = sentence.replace('{html}', "")
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', sentence)
        rem_url = re.sub(r'http\S+', '', cleantext)
        # Number Clean
        rem_num = re.sub('[0-9]+', '', rem_url)
        #print("Cleaner Txt:", cleantext)
        # text = re.sub(r"[-()\"#/@;:<>{}=~|.?,]", "", text)

        tokens = self.tokenizer.tokenize(rem_num)
        filtered_words = [w for w in tokens if len(
            w) > 2 if not w in self.stopwords]
        #stem_words=[stemmer.stem(w) for w in filtered_words]
        lemma_words = [lemmatizer.lemmatize(w) for w in filtered_words]
        return " ".join(lemma_words)

    def get_lemmantizer(self, text): 
        lem_txt = lemmatizer.lemmatize(text)
        return lem_txt

    def clean_text(self, article_text):
        rem_num = re.sub('[0-9]+', '', article_text)
        #print("Cleaner Text: ", article_text, rem_num)
        return rem_num

    def clean_input_text(self, text): 
        #text = text.replace("@#$%^&*()[]\r\n`~-=_+", "") # @#$%^&*()[]{};:/<>\|`~-=_+
        #text = text.replace('\n','')
        #text = text.replace('\r', '')
        '''escaped = text.translate(str.maketrans({"'":  r"\'",
                                          "\"":  r"\"",
                                          "^":  r"\^",
                                          "$":  r"\$",
                                          "*":  r"\*"}))'''

        return text

    def get_sentences(self, article_text):
        sentences = re.split(r' *[\.\?!][\'"\)\]]* *', article_text)
        sent_list = []
        start = 0
        end = 0
        for sent in sentences:                  
            end = start + len(sent) + 1    
            trailing_space = len(article_text[start:end]) - len(article_text[start:end].lstrip()) 
            start += trailing_space
            end += trailing_space       
            #print('Sent:', repr(sent), (len(sent)+1))
            #print('Article:', repr(article_text[start:end]), len(article_text[start:end]), start, end)
            json_sent = {
                'sentance': article_text[start:end], 'start': start, 'end': end}
            sent_list.append(json_sent)
            start = end 
        #print(sent_list)
        return sent_list

    def get_sentences_old(self, article_text):
        #sentences = re.split(r' *[\.\?!][\'"\)\]]* *', article_text)
        about_doc = self.nlp(article_text)
        sentences = list(about_doc.sents)
        print('Sentences : ', sentences)
        return sentences

    def token_words(self, text=''):
        message = self.__remove_punctuation(text)
        words = self.__remove_stopwords(message)
        return words


''' 
    def search_sentence(self, sentence, article_text):
        start_i = 0
        end_i = 0
        steps = 5000
        #print ('Size of Article : ', article_text, len(article_text))
        for i in range(start_i, len(article_text), steps):
            end_i += steps
            res = None
            print ('Input To Search: \n', article_text[start_i:end_i], start_i, end_i)
            try: 
                #res = re.findall(sentence, article_text[start_i:end_i]) # TODO Revisite   
                res = re.compile(sentence)
                res_list = res.finditer(article_text[start_i:end_i])
                for m in res_list:
                    st = int (m.start())
                    en = int (m.end())
                    print ("\n RES>>>>>>>> \n", sentence, st, en, article_text[st:en])           
            except IndexError as e:
                print("IndexError : ", e)
            except re.error as e:
                print("re.error : ", e)   
            finally:    
                if res is not None:
                    found_start = start_i + res.start()
                    found_end = start_i + res.end()                    
                    print('Found : ', found_start, found_end)
                    return found_start, found_end
                start_i += steps
        return None, None


    def search_sentence(self, sentence, article_text):
        #print ('Size of Article : ', article_text, len(article_text))
        text = re.split('[.?]', article_text)
        start_i = 0
        end_i = 0
        for sent in text:
            sent += "."
            end_i = len(sent)
            print (sent)
            try: 
                res = re.search(sentence, sent)                
            except IndexError as e:
                print("IndexError : ", e)
            except re.error as e:
                print("re.error : ", e)   
            finally:    
                if res is not None:
                    found_start = start_i + res.start()
                    found_end = start_i + res.end()                    
                    print('Found : ', found_start, found_end)
                    return found_start, found_end
                start_i = end_i
        return None, None


    def search_sentence(self, sentence, article_text):
        start_i = 0
        end_i = 0
        steps = 2000
        #print ('Size of Article : ', article_text, len(article_text))
        for i in range(start_i, len(article_text), steps):
            end_i += steps
            res = None
            print ('Input To Search: \n', article_text[start_i:end_i], start_i, end_i)
            try: 
                res = re.search(sentence, article_text[start_i:end_i]) # TODO Revisite                 
            except IndexError as e:
                print("IndexError : ", e)
            except re.error as e:
                print("re.error : ", e)   
            finally:    
                if res is not None:
                    found_start = start_i + res.start()
                    found_end = start_i + res.end()                    
                    print('Found : ', found_start, found_end)
                    return found_start, found_end
                start_i += steps
        return None, None
'''
