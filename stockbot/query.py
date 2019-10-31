#!/usr/bin/env python3
from .metrics import addQueryToMetrics
from .financial import *
import re


def doStockSymbolStatement(companyName):
    return companyName.capitalize() + "'s stock symbol is " + company_name_to_stock(companyName)[0]


def doRecommendationStatement(who, stockSymbol):
    if who == None or who == 'me' or who == 'myself' or who == 'i':
        who = 'you'
    else:
        who = who.title()

    # TODO actually decide something
    return "I think " + who + " should invest in " + stockSymbol.upper()


def doUnknownResponse():
    return "I'm sorry, I don't understand your question" # TODO random response?


def queryChatbot(statement):
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
    recommendRegex = r'^(?:should|(?:do\s+)?(?:you\s+)?(?:recommend))'
    optionalNameRegex = r'(?:' + nameRegex + r')?'
    investRegex = r'\s+(?:(?:to\s+)?invests?|(?:buys?|gets?)\s+(?:stocks?|shares?))\s+(?:in|for)'
    
    # Try to match the type of question
    # Stock symbol (first variant)
    # (What's|What is) [the] [stock] symbol|code for|of ... [in (XX(/(XX|month)/XXXX))][?!.]
    matches = re.match(whatRegex + optionalTheRegex + stockSymbolRegex + prepositionRegex + nameRegex + optionalDateRegex + questionEndRegex, statement, re.IGNORECASE)
    if matches != None:
        return doStockSymbolStatement(matches.group(1))
    
    # Stock symbol (second variant)
    # (What's|What is) ...['s] [stock] symbol|code [in (XX(/(XX|month)/XXXX))][?!.]
    matches = re.match(whatRegex + nameRegex + apostropheSRegex + stockSymbolRegex + optionalDateRegex + questionEndRegex, statement, re.IGNORECASE)
    if matches != None:
        return doStockSymbolStatement(matches.group(1))
    
    # Recommendation
    # (Should|[Do ][you ]recommend) [...] (to invest|invests|buys (stocks|shares)) in|for ...[?!.]
    matches = re.match(recommendRegex + optionalNameRegex + investRegex + nameRegex + questionEndRegex, statement, re.IGNORECASE)
    if matches != None:
        return doRecommendationStatement(matches.group(1), matches.group(2))
    
    return doUnknownResponse()
