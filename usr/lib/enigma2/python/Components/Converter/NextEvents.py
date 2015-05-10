from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.VariableText import VariableText
from enigma import eLabel, eEPGCache, eServiceReference
from time import localtime, strftime, mktime, time
from datetime import datetime

class NextEvents(Converter, object):
    TimeNext = 0
    TimeAfter = 1
    NameNext = 3
    NameAfter = 4
    DescNext = 6
    DescAfter = 7

    def __init__(self, type):
        Converter.__init__(self, type)
        self.epgcache = eEPGCache.getInstance()
        if type == 'NameAfter':
            self.type = self.NameAfter
        elif type == 'TimeNext':
            self.type = self.TimeNext
        elif type == 'TimeAfter':
            self.type = self.TimeAfter
        elif type == 'DescNext':
            self.type = self.DescNext
        elif type == 'DescAfter':
            self.type = self.DescAfter
        else:
            self.type = self.NameNext


    @cached
    def getText(self):
        ref = self.source.service
        info = ref and self.source.info
        event = self.source.event
        if info is None:
            return ''
        if event is None:
            return ''
        if self.type <= 1:
            curEvent = self.source.getCurrentEvent()
            if curEvent:
                self.epgcache.startTimeQuery(eServiceReference(ref.toString()), curEvent.getBeginTime() + curEvent.getDuration())
                for i in range(self.type):
                    self.epgcache.getNextTimeEntry()
                next = self.epgcache.getNextTimeEntry()
                if next:
                    return self.formatEvent(next)
        if self.type >= 2:
            nextEvents = self.epgcache.lookupEvent(['ITSECX', (ref.toString(), 1, -1, 1440)])  
            if nextEvents:
                try:
                    if self.type == self.NameNext and nextEvents[1][1]:
                        return nextEvents[1][1]
                    if self.type == self.DescNext and (nextEvents[1][2] or nextEvents[1][3]):
                        description = nextEvents[1][2]
                        extended = nextEvents[1][3]
                        if description and extended and description[0:20] != extended[0:20]:
                            description += '\n'
                        return description + extended
                    if self.type == self.NameAfter and nextEvents[2][1]:
                        return nextEvents[2][1]
                    if self.type == self.DescAfter and (nextEvents[2][2] or nextEvents[2][3]):
                        description = nextEvents[2][2]
                        extended = nextEvents[2][3]
                        if description and extended and description[0:20] != extended[0:20]:
                            description += '\n'
                        return description + extended
                    return ''
                except:
                    return ''

    text = property(getText)

    def formatEvent(self, event):
        begin = strftime('%H:%M', localtime(event.getBeginTime()))
        end = strftime('%H:%M', localtime(event.getBeginTime() + event.getDuration()))
        if begin:
             f = '{begin} - {end}'
             return f.format(begin=begin, end=end,)
        return ''
