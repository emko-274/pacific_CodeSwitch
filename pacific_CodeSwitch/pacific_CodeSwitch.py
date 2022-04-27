import os
import re
import cleantext
import fasttext
from joblib import dump, load
from pathlib import Path
import numpy as np
import cytoolz as ct

#----------------------------------------------------
class Tokenizer(object):
    
    def __init__(self, sample_size = 1000):
        self.sample_size = sample_size

    ##-------
    ## This function controls string cleaning
    ##-------
    def clean_line(self, line):
            
        line = cleantext.clean(line,
                fix_unicode = True,
                to_ascii = False,
                lower = True,
                no_line_breaks = True,
                no_urls = True,
                no_emails = True,
                no_phone_numbers = True,
                no_numbers = True,
                no_digits = True,
                no_currency_symbols = True,
                no_punct = True,
                replace_with_url = "",
                replace_with_email = "",
                replace_with_phone_number = "",
                replace_with_number = "",
                replace_with_digit = "",
                replace_with_currency_symbol = ""
                )
                
        cleanr1 = re.compile('<.*?>')
        cleanr2 = re.compile('<.*?\s')
        
        line = re.sub(cleanr1, '', line)
        line = line.replace("\\", "<")
        line = re.sub(cleanr2, '', line)

        return line.lstrip().rstrip()
#----------------------------------------------------

class LID(object):

    #---------
    def __init__(self, language = "mri", algorithm = "v2"):
    
        self.langs = ['ace','bug','ceb','cha','chk','fij','gil','haw','hil','hmo','ilo','jav','mah','mlg',
                      'mri','msa','niu','pag','pon','rar','smo','sun','tah','tgl','ton','tvl','war','wls','yap']

        self.language = language
        
        if self.language not in self.langs:
            print("Language is not supported!")
            sys.kill()
        
        self.location = __file__.replace("pacific_CodeSwitch.py","")
        self.model_name = "model.lid.eng_" + self.language + ".v2.epoch20.neg100.dim100.ns.small.minCount.ftz"
        self.model = fasttext.load_model(os.path.join(self.location, self.model_name))
        self.langs_total = ["eng", self.language]
        
        if algorithm == "v2":
            self.predict = self.predict_v2
        elif algorithm == "v1":
            self.predict = self.predict_v1
        elif algorithm == "v3":
            self.predict = self.predict_v3
        
        tokenizer = Tokenizer()
        self.clean = tokenizer.clean_line

        return
    
    #----------
    def ft_predict(self, line):
    
        result = self.model.predict(line)
        
        label = result[0][0].replace("__label__","")
        prob = result[1][0]

        if label != "eng":
            prob = -(prob)
        
        #print(line, result, prob)
        
        return prob

    #----------
    def predict_v1(self, line):
    
        #Clean it
        line = self.clean(line)
        overall = self.ft_predict(line)
        
        #Get all sub-sequences
        window_pre = [line[:i] for i in range(1,10)]
        window = ["".join(x) for x in ct.sliding_window(20, line)]
        window_post = [line[-i:] for i in range(1,11)]
            
        #Predict over each sub-sequence
        probabilities = []
        for span in window_pre + window + window_post:
            probabilities.append(self.ft_predict(span))

        #Get word indexes
        words = [m.start() for m in re.finditer("\s", line)]
        words.insert(0, 0) 
        words = list(ct.sliding_window(2, words)) + [(words[-1],len(line))]
            
        #Get word and summed probability
        text = [line[word[0]:word[1]] for word in words]

        label = []
        for word in words:
            span = probabilities[word[0]:word[1]]
            label.append(sum(span)/len(span))
        
        final = []
        for i in range(len(text)):
            string = text[i]
            prob_return = label[i]
            
            if prob_return > 0:
                prob_return = "eng"
            else:
                prob_return = self.language
            final.append((string, prob_return))
            
        return final, overall
    
    #----------

    def predict_v2(self, line):
    
        #Clean it and get overall prediction
        line = self.clean(line)
        overall_pred = self.ft_predict(line)
       
        line_list = line.split()
        line_return = []
        
        for i in range(len(line_list)):
        
            #Get current word and its prediction
            word = line_list[i]
            word_pred = self.ft_predict(word)
            
            #Get sequence trigram around word and its prediction
            start = max(0, i-1)
            stop = min(i+2, len(line_list))
            context = " ".join(line_list[start:stop])
            context_pred = self.ft_predict(context)

            #Take the smallest and adjust by overall prediction
            if overall_pred > 0:
                pred = max(word_pred,context_pred)
            else:
                pred = min(word_pred,context_pred)
            
            if pred > 0:
                pred = "eng"
            else:
                pred = self.language
            line_return.append((word, pred))
              
        return line_return, overall_pred
    
    #----------
    def predict_v3(self, line):
    
        #Clean it and get overall prediction
        line = self.clean(line)
        overall_pred = self.ft_predict(line)
        
        line_list = line.split()
        line_return = []
        
        for i in range(len(line_list)):
        
            #Get current word and its prediction
            word = line_list[i]
            pred = self.ft_predict(word)
            
            if pred > 0:
                pred = "eng"
            else:
                pred = self.language
            line_return.append((word, pred))
              
        return line_return, overall_pred