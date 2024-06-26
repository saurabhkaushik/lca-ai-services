import re
import string
import pytextrank # TextRank 
import spacy

class PreProcessText(object):
    nlp = spacy.load('en_core_web_md')
    nlp.add_pipe("textrank")

    def __init__(self):
        pass

    stopwords = nlp.Defaults.stop_words

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
        # Lower Case 
        sentence = sentence.lower()

        # HTML CLEAN
        sentence = sentence.replace('{html}', "")
        cleanr = re.compile('<.*?>')
        sentence = re.sub(cleanr, '', sentence)
        sentence = re.sub(r'http\S+', '', sentence)
        #sentence = re.sub("https?:\/\/.*[\r\n]*", "", sentence)
        sentence = re.sub("@\S+", "", sentence)
        sentence = re.sub("\$", "", sentence)

        # Unicode Text 
        ''' text_encode = sentence.encode(encoding="ascii", errors="ignore")
        text_decode = text_encode.decode()
        sentence = " ".join([word for word in text_decode.split()])
        ''' 

        # Number Clean
        sentence = re.sub('[0-9]+', '', sentence)

        # Stop Words
        doc = self.nlp(sentence)
        stop_words = [token.text for token in doc if not token.is_stop]
        sentence = " ".join(stop_words).strip()

        # Lemmentize 
        doc = self.nlp(sentence)
        lemma_words = [token.lemma_ for token in doc]
        sentence = " ".join(lemma_words).strip()

        return sentence

    def get_lemmantizer(self, text): 
        doc = self.nlp(text)
        lemma_words = [token.lemma_ for token in doc]
        lem_text = " ".join(lemma_words).strip()
        return lem_text

    def clean_text(self, article_text):
        rem_num = re.sub('[0-9]+', '', article_text)
        return rem_num

    def get_sentences(self, article_text):
        sentences = self.get_sentences_spacy(article_text)
        sent_list = []
        start = 0
        end = 0
        for sent in sentences:     
            sent = str(sent)             
            end = start + len(sent) + 1    
            trailing_space = len(article_text[start:end]) - len(article_text[start:end].lstrip()) 
            start += trailing_space
            end += trailing_space       
         
            stmt = self.clean_text(sent)            

            json_sent = {
                'sentance': str(stmt), 'start': start, 'end': end}
            sent_list.append(json_sent)
            start = end 
        return sent_list


    def get_sentences_spacy(self, article_text):
        about_doc = self.nlp(article_text)
        sentences = list(about_doc.sents)  
        return sentences

    def token_words(self, text=''):
        message = self.__remove_punctuation(text)
        words = self.__remove_stopwords(message)
        return words


''' 
    def get_sentences_regex(self, article_text):
        sentences = re.split(r' *[\.\?!][\'"\)\]]* *', article_text)
        return sentences

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
