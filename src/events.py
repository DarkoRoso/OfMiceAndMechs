cinematics = None
messages = None
callShow_or_exit = None
loop = None

class Event(object):
    def __init__(self,tick):
        self.tick = tick

    def handleEvent(self):
        pass

class ShowCinematicEvent(Event):
    def __init__(self,tick,cinematic):
        super().__init__(tick)
        self.cinematic = cinematic

    def handleEvent(self):
        cinematics.cinematicQueue.append(self.cinematic)
        loop.set_alarm_in(0.0, callShow_or_exit, '~')

