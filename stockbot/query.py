#!/usr/bin/env python3
from .metrics import addQueryToMetrics
import re


def doStockSymbolStatement(matches):
    companyName = matches.group(1)
    return "STUB - got stock symbol for " + companyName # TODO implement


def doUnknownResponse():
    return "I'm sorry, I don't understand your question" # TODO random response?


def queryChatbot(statement):
    addQueryToMetrics()
    
    # Try to match the type of question
    # Stock symbol (first variant)
    # What is the stock symbol of ... (in XX/XX/XXXX)?
    # Most of the expression is for matching broken english and dates in multiple formats
    dateRegex = r'(?:\s+in\s+(?:[0-9]+|[0-9]+\s*(?:st|nd|rd|th)?(?:\s+|\s*\/\s*)(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may?|june?|july?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|0*[1-9]|0*1[0-2])(?:(?:\s+|\s*\/\s*)[0-9]+)?))?'
    matches = re.match(r'^wh?at(?:\s+is(?:\s*the)?)?(?:\s+stock)?\s+(?:symbol|code)\s+(?:for|of)\s+((?!\s).+?)(?:\s+in\s+(?:[0-9]+|[0-9]+\s*(?:st|nd|rd|th)?(?:\s+|\s*\/\s*)(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may?|june?|july?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?|0*[1-9]|0*1[0-2])(?:(?:\s+|\s*\/\s*)[0-9]+)?))?[?!.\s]*$', statement, re.IGNORECASE)
    if matches != None:
        return doStockSymbolStatement(matches)
    
    # Stock symbol (second variant)
    # What is ...'s stock symbol
    matches = re.match(r'^wh?at\s+is\s+((?!\s).+?)(?:\'|s|\'s)?(?:\s+stock)?\s+(?:symbol|code)' + dateRegex + r'[?!.\s]*$', statement, re.IGNORECASE)
    if matches != None:
        return doStockSymbolStatement(matches)
    
    return doUnknownResponse()
