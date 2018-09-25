########################################################################################################
###
##     the code for the characters belongs here
#
########################################################################################################

# import basic libs
import json

# import the other internal libs
import src.items
import src.saveing
import src.quests

# bad code: containers for global state
characters = None
calculatePath = None
roomsOnMap = None

"""
this is the class for characters meaning both npc and pcs. 
all characters except the pcs always have automated = True to
make them to things on their own
"""
class Character(src.saveing.Saveable):
    '''
    sets basic info AND adds default behaviour/items
    '''
    def __init__(self,display="＠",xPosition=0,yPosition=0,quests=[],automated=True,name="Person",creator=None):
        super().__init__()

        # set basic state
        self.display = display # bad code: the character should have a rendering+chaching caching method instead of attrbute
        self.automated = automated
        self.quests = []
        self.name = name
        self.inventory = []
        self.watched = False
        self.listeners = {"default":[]}
        self.path = []
        self.subordinates = []
        self.reputation = 0
        self.events = []
        self.room = None
        self.terrain = None
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.satiation = 1000
        self.dead = False
        self.deathReason = None
        self.questsToDelegate = []
        self.unconcious = False
        self.displayOriginal = display
        self.isMilitary = False
        self.hasFloorPermit = True
        self.id = {
                   "other":"character",
                   "xPosition":xPosition,
                   "yPosition":yPosition,
                   "counter":creator.getCreationCounter()
                  }
        self.id["creator"] = creator.id
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

        self.attributesToStore.extend([
               "gotBasicSchooling","gotMovementSchooling","gotInteractionSchooling","gotExamineSchooling",
               "xPosition","yPosition","name","satiation","unconcious","reputation","tutorialStart"])
        self.objectsToStore.append("serveQuest")
        self.objectsToStore.append("room")

        # bad code: story specific state
        self.serveQuest = None
        self.tutorialStart = 0
        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False

        # bad code: this approach is fail, but works for now. There has to be a better way
        self.basicChatOptions = []

        self.questsDone = []
        self.solvers = []

        # default quests
        self.assignQuest(src.quests.SurviveQuest(creator=self))
        for quest in quests:
            self.assignQuest(quest)

        # default items
        self.inventory.append(src.items.GooFlask(creator=self))

        # save state and register
        self.initialState = self.getState()
        loadingRegistry.register(self)

    @property
    def container(self):
        if self.room:
            return self.room
        else:
            return self.terrain

    '''
    proxy room quest when asked for a job
    '''
    def getQuest(self):
        if self.room and self.room.quests:
            return self.room.quests.pop()
        else:
            return None

    '''
    almost straightforward adding of events to the characters event queue
    ensures that the events are added in proper order
    '''
    def addEvent(self,event):
        index = 0
        for existingEvent in self.events:
            if event.tick < existingEvent.tick:
                break
            index += 1
        self.events.insert(index,event)

    '''
    reset the path to the current quest
    bad code: is only needed because path is contained in character instead of quest
    '''
    def recalculatePath(self):
        self.setPathToQuest(self.quests[0])

    '''
    straightforward removeing of events from the characters event queue
    '''
    def removeEvent(self,event):
        self.events.remove(event)

    '''
    almost straightforward getter for chat options
    # bad code: adds default chat options
    '''
    def getChatOptions(self,partner):
        chatOptions = self.basicChatOptions[:]
        if not self in partner.subordinates:
            chatOptions.append(interaction.RecruitChat)
            pass
        return chatOptions

    '''
    get the changes in state since creation
    '''
    def getDiffState(self):
        # the to be result
        result = super().getDiffState()

        # save path
        if not self.path == self.initialState["path"]:
            result["path"] = self.path

        # save inventory
        (itemStates,changedItems,newItems,removedItems) = self.getDiffList(self.inventory,self.initialState["inventory"]["inventoryIds"])
        inventory = {}
        if changedItems:
            inventory["changed"] = changedItems
        if newItems:
            inventory["new"] = newItems
        if removedItems:
            inventory["removed"] = removedItems
        if itemStates:
            inventory["states"] = itemStates
        if itemStates or removedItems:
            result["inventory"] = inventory

        # save quests
        (questStates,changedQuests,newQuests,removedQuests) = self.getDiffList(self.quests,self.initialState["quests"]["questIds"])
        quests = {}
        if changedQuests:
            quests["changed"] = changedQuests
        if newQuests:
            quests["new"] = newQuests
        if removedQuests:
            quests["removed"] = removedQuests
        if questStates:
            quests["states"] = questStates
        if questStates or removedQuests:
            result["quests"] = quests

        # store events diff
        (eventStates,changedEvents,newEvents,removedEvents) = self.getDiffList(self.events,self.initialState["eventIds"])
        if changedEvents:
            result["changedEvents"] = changedEvents
        if newEvents:
            result["newEvents"] = newEvents
        if removedEvents:
            result["removedEvents"] = removedEvents
        if eventStates:
            result["eventStates"] = eventStates

        # save chat options
        # bad code: storing the Chat options as class instead of object complicates things
        chatOptions = []
        for chat in self.basicChatOptions:
            if not isinstance(chat,dict):
                chatOptions.append(chat.id)
            else:
                option = {}
                option["chat"] = chat["chat"].id
                option["dialogName"] = chat["dialogName"]
                option["params"] = {}
                if "params" in chat:
                    for key, value in chat["params"].items():
                        option["params"][key] = value.id
                chatOptions.append(option)
        result["chatOptions"] = chatOptions

        return result

    '''
    getter for the players state
    '''
    def getState(self):
        state = super().getState()

        state.update({ 
                 "inventory": {},
                 "quests": {},
                 "path":self.path,
               })
                 
        # store inventory
        inventory = []
        for item in self.inventory:
            inventory.append(item.id)
        state["inventory"]["inventoryIds"] = inventory

        # store quests
        quests = []
        for quest in self.quests:
            quests.append(quest.id)
        state["quests"]["questIds"] = quests

        # store events
        (eventIds,eventStates) = self.storeStateList(self.events)
        state["eventIds"] = eventIds

        # store serve quest
        # bad code: storing the Chat options as class instead of object complicates things
        chatOptions = []
        for chat in self.basicChatOptions:
            if not isinstance(chat,dict):
                chatOptions.append(chat.id)
            else:
                option = {}
                option["chat"] = chat["chat"].id
                option["dialogName"] = chat["dialogName"]
                option["params"] = {}
                if "params" in chat:
                    for key, value in chat["params"].items():
                        option["params"][key] = value.id
                    chatOptions.append(option)
        state["chatOptions"] = chatOptions

        return state

    '''
    setter for the players state
    '''
    def setState(self,state):
        super().setState(state)

        # set uncoincious state
        if "unconcious" in state:
            if self.unconcious:
                self.fallUnconcious()
                self.display = displayChars.unconciousBody

        # set path
        if "path" in state:
            self.path = state["path"]

        # set inventory
        if "inventory" in state:
            self.loadFromList(state["inventory"],self.inventory,src.items.getItemFromState)

        # set quests
        if "quests" in state:
            self.loadFromList(state["quests"],self.quests,quests.getQuestFromState)

        # set chat options
        # bad code: storing the Chat options as class instead of object complicates things
        if "chatOptions" in state:
            chatOptions = []
            for chatType in state["chatOptions"]:
                if not isinstance(chatType,dict):
                    chatOptions.append(chats.chatMap[chatType])
                else:
                    option = {}
                    option["chat"] = chats.chatMap[chatType["chat"]]
                    option["dialogName"] = chatType["dialogName"]
                    if "params" in chatType:
                        params = {}
                        for (key,value) in chatType["params"].items():
                            '''
                            set value
                            '''
                            def setParam(instance):
                                params[key] = instance
                            loadingRegistry.callWhenAvailable(value,setParam)
                        option["params"] = params
                    chatOptions.append(option)
            self.basicChatOptions = chatOptions

        # add new events
        if "newEvents" in state:
            for eventId in state["newEvents"]:
                eventState = state["eventStates"][eventId]
                event = events.getEventFromState(eventState)
                self.addEvent(event)

        return state

    '''
    starts the next quest in the quest list
    bad code: this is kind of incompatible with the meta quests
    '''
    def startNextQuest(self):
        if len(self.quests):
            self.quests[0].recalculate()
            try:
                self.setPathToQuest(self.quests[0])
            except:
                # bad pattern: exceptions should be logged
                pass

    '''
    straightforward getting a string with detailed info about the character
    '''
    def getDetailedInfo(self):
        return "\nname: "+str(self.name)+"\nroom: "+str(self.room)+"\ncoordinate: "+str(self.xPosition)+" "+str(self.yPosition)+"\nsubordinates: "+str(self.subordinates)+"\nsat: "+str(self.satiation)+"\nreputation: "+str(self.reputation)

    '''
    adds a quest to the characters quest list
    bad code: this is kind of incompatible with the meta quests
    '''
    def assignQuest(self,quest,active=False):
            if active:
                self.quests.insert(0,quest)
            else:
                self.quests.append(quest)
            quest.assignToCharacter(self)
            quest.activate()
            if (active or len(self.quests) == 1):
                try:
                    if self.quests[0] == quest:
                        self.setPathToQuest(quest)
                except:
                    # bad pattern: exceptions should be logged
                    pass

    '''
    set the path to a quest
    bad pattern: this should be determined by a quests solver
    bad pattern: the walking should be done in a quest solver so this method should removed on the long run
    '''
    def setPathToQuest(self,quest):
        if hasattr(quest,"dstX") and hasattr(quest,"dstY"):
            # bad code: room and terrain should be unified into a container object
            if self.room:
                self.path = self.room.calculatePath(self.xPosition,self.yPosition,quest.dstX,quest.dstY,self.room.walkingPath)
            elif self.terrain:
                self.path = self.terrain.findPath((self.xPosition,self.yPosition),(quest.dstX,quest.dstY))
            else:
                debugMessages.append("this should not happen, character tried to go sowhere but is nowhere")
                self.path = []
        else:
            self.path = []

    '''
    straightforward adding to inventory
    '''
    def addToInventory(self,item):
        self.inventory.append(item)

    '''
    this wrapper converts a character centred call to a solver centered call
    bad code: should be handled in quest
    '''
    def applysolver(self,solver):
        if not self.unconcious and not self.dead:
            solver(self)

    '''
    set state and display to unconcious
    '''
    def fallUnconcious(self):
        self.unconcious = True
        self.display = displayChars.unconciousBody # bad code: should be a render method
        messages.append("*thump,snort*") # bad code: should ony be shown for main character or characters near player
        self.changed("fallen unconcious",self)

    '''
    set state and display to not unconcious
    '''
    def wakeUp(self):
        self.unconcious = False
        self.display = self.displayOriginal # bad code: should be a render method
        messages.append("*grown*") # bad code: should ony be shown for main character or characters near player

    '''
    kill the character and do a bit of extra stuff like placing corpses
    '''
    def die(self,reason=None):
        # replace character with corpse
        # bad code: terain and room should be unified in container object
        # bad code: redundant code
        if self.room:
            room = self.room
            room.removeCharacter(self)
            corpse = src.items.Corpse(self.xPosition,self.yPosition,creator=self)
            room.addItems([corpse])
        elif self.terrain:
            terrain = self.terrain
            terrain.removeCharacter(self)
            corpse = src.items.Corpse(self.xPosition,self.yPosition,creator=self)
            terrain.addItems([corpse])
        else:
            debugMessages.append("this should not happen, character died without beeing somewhere ("+str(self)+")")

        # set attributes
        self.dead = True
        self.changed("died",{"character":self,"corpse":corpse,"reason":reason})
        if reason:
            self.deathReason = reason
        self.path = []

        # notify listeners
        self.changed()

    '''
    walk the predetermined path
    return:
        True when done
        False when not done

    bad pattern: should be contained in quest solver
    '''
    def walkPath(self):
        # bad code: a dead charactor should not try to walk
        # bad pattern: this should log
        if self.dead:
            return

        # bad code: a charactor should not try to walk if it has no path
        # bad pattern: this should be a logging assertion
        if not self.path:
            self.setPathToQuest(self.quests[0])

        # move along the predetermined path
        currentPosition = (self.xPosition,self.yPosition)
        if not (self.path and not self.path == [currentPosition]):
            return True

        nextPosition = self.path[0]

        item = None
        if self.room:
            # move naively within a room
            if nextPosition[0] == currentPosition[0]:
                if nextPosition[1] < currentPosition[1]:
                    item = self.room.moveCharacterDirection(self,"north")
                elif nextPosition[1] > currentPosition[1]:
                    item = self.room.moveCharacterDirection(self,"south")
                else:
                    # smooth over impossible state
                    if not debug:
                        # resorting to teleport
                        self.xPosition = nextPosition[0]
                        self.yPosition = nextPosition[1]
                        self.changed()
                    else:
                        debugMessages.append("character moved on non continious path")
            elif nextPosition[0] == currentPosition[0]-1 and nextPosition[1] == currentPosition[1]:
                item = self.room.moveCharacterDirection(self,"west")
            elif nextPosition[0] == currentPosition[0]+1 and nextPosition[1] == currentPosition[1]:
                item = self.room.moveCharacterDirection(self,"east")
            else:
                # smooth over impossible state
                if not debug:
                    # resorting to teleport
                    self.xPosition = nextPosition[0]
                    self.yPosition = nextPosition[1]
                    self.changed()
                else:
                    debugMessages.append("character moved on non continious path")
        else:
            # check if a room was entered
            # basically checks if a walkable space/door within a room on the coordinate the chracter walks on. If there is
            # an item it will be saved for interaction
            # bad pattern: collision detection and room teleportation should be done in terrain

            for room in self.terrain.rooms:
                def moveCharacter(localisedEntry,direction):
                    if localisedEntry in room.walkingAccess:
                        # check whether the chracter walked into something
                        if localisedEntry in room.itemByCoordinates:
                            for listItem in room.itemByCoordinates[localisedEntry]:
                                if not listItem.walkable:
                                    return listItem
                        # move the chracter into the room
                        room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                        self.terrain.characters.remove(self)
                        self.terrain = None
                        self.changed()
                        return
                    else:
                        # show message the character bumped into a wall
                        # bad pattern: why restrict the player to standard entry points?
                        messages.append("you cannot move there ("+direction+")")
                        return

                # handle the character moving into the rooms boundaries
                # check north
                if room.yPosition*15+room.offsetY+room.sizeY == nextPosition[1]+1:
                    if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                        localisedEntry = (self.xPosition%15-room.offsetX,nextPosition[1]%15-room.offsetY)
                        item = moveCharacter(localisedEntry,"north")
                        break
                # check south
                if room.yPosition*15+room.offsetY == nextPosition[1]:
                    if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                        localisedEntry = ((self.xPosition-room.offsetX)%15,((nextPosition[1]-room.offsetY)%15))
                        item = moveCharacter(localisedEntry,"south")
                        break
                # check east
                if room.xPosition*15+room.offsetX+room.sizeX == nextPosition[0]+1:
                    if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                        localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                        item = moveCharacter(localisedEntry,"east")
                        break
                # check west
                if room.xPosition*15+room.offsetX == nextPosition[0]:
                    if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                        localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                        item = moveCharacter(localisedEntry,"west")
                        break
            else:
                # move the char to the next position on path
                self.xPosition = nextPosition[0]
                self.yPosition = nextPosition[1]
                self.changed()
            
        if item:
            # open doors
            # bad pattern: this should not happen here
            if isinstance(item,src.items.Door):
                item.apply(self)
            return False
        else:
            # smooth over impossible state
            if not debug:
                if not self.path or not nextPosition == self.path[0]:
                    return False

            # remove last step from path
            if (self.xPosition == nextPosition[0] and self.yPosition == nextPosition[1]):
                self.path = self.path[1:]
        return False

    """
    almost straightforward dropping of items
    """
    def drop(self,item):
        self.inventory.remove(item)
        item.xPosition = self.xPosition
        item.yPosition = self.yPosition
        # bad pattern: room and terrain should be combined into a container object
        if self.room:
            self.room.addItems([item])
        else:
            self.terrain.addItems([item])
        item.changed()
        self.changed()

    """
    examine an item
    """
    def examine(self,item):
        messages.append(item.description)
        if item.description != item.getDetailedInfo():
            messages.append(item.getDetailedInfo())
        self.changed("examine",item)

    """
    advance the character one tick
    """
    def advance(self):
        # smooth over impossible state
        while self.events and gamestate.tick > self.events[0].tick:
            event = self.events[0]
            debugMessages.append("something went wrong and event"+str(event)+"was skipped")
            self.events.remove(event)

        # handle events
        while self.events and gamestate.tick == self.events[0].tick:
            event = self.events[0]
            event.handleEvent()
            if event in self.events:
                self.events.remove(event)

        # handle satiation
        self.satiation -= 1
        if self.satiation < 0:
            self.die(reason="you starved. This happens when your satiation falls below 0\nPrevent this by drinking using the "+commandChars.drink+" key")
            return

        # call the autosolver
        if self.automated:
            if len(self.quests):
                self.applysolver(self.quests[0].solver)
                self.changed()

    '''
    registering for notifications
    '''
    def addListener(self,listenFunction,tag="default"):
        # create container if container doesn't exist
        # bad performace: string comparison, should use enums
        if not tag in self.listeners:
            self.listeners[tag] = []

        # added listener function
        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregistering for notifications
    '''
    def delListener(self,listenFunction,tag="default"):
        # remove listener
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clear up dict
        # bad performance: probably better to not clean up and recreate
        if not self.listeners[tag]:
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    '''
    def changed(self,tag="default",info=None):
        if not tag in self.listeners:
            return

        for listenFunction in self.listeners[tag]:
            if info == None:
                listenFunction()
            else:
                listenFunction(info)

"""
the class for mice. Intended to be used for manipulating the gamestate used for example to attack the player
bad code: animals should not be characters. This means it is possible to chat with a mouse 
"""
class Mouse(Character):
    '''
    basic state setting
    '''
    def __init__(self,display="🝆 ",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse",creator=None):
        super().__init__(display, xPosition, yPosition, quests, automated, name, creator=creator)
        self.vanished = False

    '''
    disapear
    '''
    def vanish(self):
        if self.room:
            self.room.removeCharacter(self)
        else:
            self.terrain.removeCharacter(self)
        self.vanished = True
