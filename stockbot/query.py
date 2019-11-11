#!/usr/bin/env python3
from .qr_pil import QRCode
from random import choice
from .predict import load_predict_model, predict
from .metrics import addQueryToMetrics
from .financial import *
from .currency import *
import re


class QueryHandler:
    def __init__(self):
        self.predict_model = load_predict_model()
        print("QueryHandler -- loaded prediction model")
        
    def doStockSymbolStatement(self, companyName):
        symbol = company_name_to_stock(companyName)[0]
        text = companyName.capitalize() + "'s stock symbol is " + symbol
        image = QRCode("https://www.google.com/search?q=" + symbol).toImage()
        return text, image


    def doRecommendationStatement(self, who, stockSymbol):
        who = who.lower()
        stockSymbol = stockSymbol.upper()
        if who == None or who == 'me' or who == 'myself' or who == 'i':
            who = 'you'
        elif who == 'you' or who == 'yourself':
            return "I don't think I should invest in " + stockSymbol + ", because I am a robot!"
        else:
            if who != 'he' and who != 'she' and who != 'it' and who != 'they' and who != 'them':
                who = who.title()

        # TODO actually decide something
        return "I think " + who + " should invest in " + stockSymbol, None

    def doCurrencyStatement(self, num, currency1, currency2):
        print(num, currency1, currency2)
        currency1 = currency1.upper()
        currency2 = currency2.upper()
        try:
            data = convert(currency1,currency2)
        except:
            return "Sorry, I don't know how to convert that", None
        text = num + " " + getCurrencyData(data,2) + " converted is " + str(round(int(num) * float(getCurrencyData(data,5)),4)) + " " + getCurrencyData(data,4)
        return text, None


    def doPredictionStatement(self, symbol):
        pred = None
        try:
            pred = predict(self.predict_model, symbol.lower())
        except Exception as e:
            print(e)
            return "Sorry, I can't predict for that company", None
        return "I predict the stocks for next week are worth " + str(pred), None
    
    
    def doUnknownResponse(self):
        responses = [
            "I'm sorry, I don't understand your question",
            "I'm sorry, I don't understand you",
            "I'm sorry, I don't know what you mean",
            "I don't understand your question",
            "I don't understand you",
            "I don't know what you mean",
            "What?",
        ]
        
        return choice(responses), None


    def queryChatbot(self, statement):
        """ Ask the bot a question [statement]. Returns a response string and a pillow image as a tuple """
        addQueryToMetrics()
        
        # Regular expression parts. These are concatenated to generate the final expression
        # Most of these expressions are big due to matching broken english or unreasonable input
        optionalDateRegex = r'(?:\s+in\s+(?:[0-9]+|[0-9]+\s*(?:st|nd|rd|th)?(?:\s+|\s*\/\s*)(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may?|june?|july?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|0*[1-9]|0*1[0-2])(?:(?:\s+|\s*\/\s*)[0-9]+)?))?'
        nameRegex = r'\s+((?!\s).+?)'
        questionEndRegex = r'[?!.\s]*$'
        stockSymbolRegex = r'(?:\s+stock)?\s+(?:symbol|code)'
        apostropheSRegex = r'(?:\'|\'?s)?'
        whatRegex = r'^wh?at(?:\'?s|\s+is)'
        prepositionRegex = r'\s+(?:for|of)'
        optionalTheRegex = r'(?:\s*the)?'
        recommendRegex = r'^(?:should|(?:do\s+)?(?:you\s+)?(?:recommend|think))'
        optionalNameRegex = r'(?:' + nameRegex + r')?'
        investRegex = r'\s+(?:(?:to\s+)?invests?|(?:buys?|gets?)\s+(?:stocks?|shares?))\s+(?:in|for)'
        convertRegex = r'\s(?:converted to|in)'
        numRegex = r'\s([0-9]*)'
        
        # Try to match the type of question
        # Stock symbol (first variant)
        # (What's|What is) [the] [stock] symbol|code for|of ... [in (XX(/(XX|month)/XXXX))][?!.]
        matches = re.match(whatRegex + optionalTheRegex + stockSymbolRegex + prepositionRegex + nameRegex + optionalDateRegex + questionEndRegex, statement, re.IGNORECASE)
        if matches != None:
            return self.doStockSymbolStatement(matches.group(1))
        
        # Stock symbol (second variant)
        # (What's|What is) ...['s] [stock] symbol|code [in (XX(/(XX|month)/XXXX))][?!.]
        matches = re.match(whatRegex + nameRegex + apostropheSRegex + stockSymbolRegex + optionalDateRegex + questionEndRegex, statement, re.IGNORECASE)
        if matches != None:
            return self.doStockSymbolStatement(matches.group(1))
        
        # Recommendation
        # (Should|[Do ][you ]recommend) [...] (to invest|invests|buys (stocks|shares)) in|for ...[?!.]
        matches = re.match(recommendRegex + optionalNameRegex + investRegex + nameRegex + questionEndRegex, statement, re.IGNORECASE)
        if matches != None:
            return self.doRecommendationStatement(matches.group(1), matches.group(2))
        
        # Stock prediction
        # what do you predict for this company ...
        matches = re.match('^\s*what\s+(?:are\s+the\s+stock\s+predictions\s+for\s+this|do\s+you\s+predict\s+for\s+this)\s+company\s+([a-z]+?)\s*$', statement, re.IGNORECASE)
        if matches != None:
            return self.doPredictionStatement(matches.group(1))
        
        # Currency Conversion
        # (What's|What is) ...['s] [value] in ...?
        matches = re.match(whatRegex + numRegex + nameRegex + apostropheSRegex + convertRegex + nameRegex + questionEndRegex, statement, re.IGNORECASE)
        if matches != None:
            return self.doCurrencyStatement(matches.group(1),matches.group(2),matches.group(3))
        
        return self.doUnknownResponse()
