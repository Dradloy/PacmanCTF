# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint
from BehaviorTree import *
from simulation import *
import copy
from mcst import mcTree

#################     python capture.py -r myTeam -b baselineTeam
# Team creation #     python capture.py -r baselineTeam -b myTeam
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AgentGroup2', second = 'AgentGroup2'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class AgentGroup2(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
  myAction='Stop'
  securityDistance=4
  foodLimit=4
  mid=0
  aims = dict({})
  indexes=[]

  XLENGTH = 0
  YLENGTH = 0
  blue=True
  dicRoles={}
  dicPos={}
  dicStartPos={}
  dicFoodCarried={}
  partFilters=dict({})
  enemyIndexes=[]
  myIndexes=[]
  nbAgents=2
  myMinX=0
  myMaxX=0
  capsules = None
  enemyCapsules = None
  capsuleEffect = 0
  capsuleEnemy = 0
  lastFoodLost = None
  oldScore=0
  killCounter = 0
  spawnLane = 0

  def __init__(self, index):
    CaptureAgent.__init__(self,index)
    self.aim=[1,3]
    self.counter=0
    self.startPos=self.aim
    self.myPos=[1,3]
    self.myOldPos=[1,3]
    self.successor= None
    self.gameState= None
    self.danger = False
    AgentGroup2.aims[index]=self.aim
    self.enemyPos=None
    self.enemyCloseIndex=0
    self.behaviour = 0
    self.myFoodBoolArray=None
    self.myOldFoodBoolArray=None
    self.foodLost = None









  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''    Initialize maze distances    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''    Initialize the dictionary of roles    '''
    if(self.index<=1):
      AgentGroup2.dicRoles[self.index]='d'
    else:
      AgentGroup2.dicRoles[self.index]='a'

    '''    Initialize variables needed to know my position    '''
    self.gameState = gameState
    self.successor = self.getSuccessor(gameState, 'Stop')
    self.myPos = self.successor.getAgentPosition(self.index)
    self.myOldPos = self.successor.getAgentPosition(self.index)
    AgentGroup2.dicPos[self.index] = self.myPos

    '''    Compute the map size (needed for simulation    '''
    i = 0
    for a in gameState.getWalls():
        i += 1
    AgentGroup2.XLENGTH = i
    AgentGroup2.YLENGTH = len(gameState.getWalls()[0])

    """    Initialize my starting position    """
    self.startPos = self.myPos

    """    Compute the mid x (the one on our side)    """
    AgentGroup2.mid = self.distancer.dc.layout.width / 2
    if (self.startPos[0] < self.mid):
      print "mid is broken !!!!!!!!!!!!!!!!!!!!!!!!!"
      AgentGroup2.mid -= 1

    """    Determine if we are blue or red team    """
    if(self.index<=1):
      AgentGroup2.blue = not gameState.isOnRedTeam(self.index)

    """    Initialize indexes    """
    if(self.index<=1):
      if(AgentGroup2.blue):
        AgentGroup2.myIndexes=gameState.getBlueTeamIndices()
        AgentGroup2.enemyIndexes=gameState.getRedTeamIndices()
      else:
        AgentGroup2.myIndexes = gameState.getRedTeamIndices()
        AgentGroup2.enemyIndexes = gameState.getBlueTeamIndices()
    print 'myIndexed',AgentGroup2.myIndexes
    print 'enemyIndexed',AgentGroup2.enemyIndexes
    print 'blue',AgentGroup2.blue
    print 'myIndex',self.index


    """    Count number of agents per team     """
    AgentGroup2.nbAgents=len(AgentGroup2.myIndexes)


    """    Innitialise dictionary of positions (needed for simulation)    """
    AgentGroup2.dicPos[self.index]=self.myPos
    if(self.index<=1):
      for index in AgentGroup2.enemyIndexes:
        AgentGroup2.dicPos[index]=gameState.getInitialAgentPosition(index)

    """    Innitialise dictionary of starting positions (needed for simulation)    """
    AgentGroup2.dicStartPos[self.index] = self.myPos
    if (self.index <= 1):
        for index in AgentGroup2.enemyIndexes:
            AgentGroup2.dicStartPos[index] = gameState.getInitialAgentPosition(index)
            AgentGroup2.dicPos[index] = gameState.getInitialAgentPosition(index)

    """    Innitialise dictionary of carried food    """
    if (self.index <= 1):
      for index in AgentGroup2.myIndexes:
        AgentGroup2.dicFoodCarried[index] = 0
      for index in AgentGroup2.enemyIndexes:
        AgentGroup2.dicFoodCarried[index] = 0

    """    Initialize particle filters    """
    if (self.index <= 1):
      for index in AgentGroup2.enemyIndexes:
        AgentGroup2.partFilters[index]=ParticleFilter(gameState, self, self.index, AgentGroup2.dicPos[index])

    """    Initialize variables for the simulation    """
    if AgentGroup2.blue:
      AgentGroup2.myMinX=AgentGroup2.mid
      AgentGroup2.myMaxX=AgentGroup2.XLENGTH
    else:
      AgentGroup2.myMinX=0
      AgentGroup2.myMaxX=AgentGroup2.mid



    #Choose a semi random goal
    foodLeft = self.getFood(gameState).asList()
    self.aim = random.choice(self.closestFoods(foodLeft,9))

    if self.blue:
      self.capsules = self.gameState.getRedCapsules()
      self.enemyCapsules = self.gameState.getBlueCapsules()
      AgentGroup2.spawnLane = AgentGroup2.XLENGTH - 1
    else:
      self.capsules = self.gameState.getBlueCapsules()
      self.enemyCapsules = self.gameState.getRedCapsules()
      AgentGroup2.spawnLane = 1


  def chooseAction(self, gameState):
      startTime=time.time()

      """    Update variables related to position    """
      self.successor = self.getSuccessor(gameState, 'Stop')
      self.myPos = self.successor.getAgentPosition(self.index)
      self.gameState=gameState
      AgentGroup2.dicPos[self.index]=self.myPos

      """    Update my foodArray to check if something was eaten    """
      if AgentGroup2.blue:
        self.myFoodBoolArray=gameState.getBlueFood()
      else:
        self.myFoodBoolArray = gameState.getRedFood()


      #bestAction = self.findBestAction()
      #self.debugDraw(self.aim, [1, 0, 0], True)
      #"""
      # print("index: "+str(self.index)+"  counter: "+str(self.counter)+"  aim"+str(self.aim))+ "   current pos:"+str(self.myPos)






      """    Particles filter updates    """
      for eindex in AgentGroup2.enemyIndexes:
        AgentGroup2.partFilters[eindex].update(self.myPos,gameState.getAgentDistances()[eindex],self.index)


      """    Check if some food has been eaten and update the particles filter if so    """
      self.foodLost=self.myFoodChanged(self.myFoodBoolArray,self.myOldFoodBoolArray)
      if self.foodLost!=None:
        possible=[]
        for eindex in AgentGroup2.enemyIndexes:
          AgentGroup2.partFilters[eindex].knownPos(self.foodLost,AgentGroup2.partFilters.values())
          if AgentGroup2.partFilters[eindex].hasPos(self.foodLost):
            possible.append(eindex)
        if len(possible)==0:
          possible=AgentGroup2.enemyIndexes
        min=9999
        bestIndex=-1
        for eindex in AgentGroup2.enemyIndexes:
          if self.getMazeDistance(self.foodLost,AgentGroup2.dicPos.get(eindex))<min:
            min=self.getMazeDistance(self.foodLost,AgentGroup2.dicPos.get(eindex))
            bestIndex=eindex
        AgentGroup2.dicFoodCarried[bestIndex]+=1

      """      Check if some food has been return by the enemy      """
      min=9999
      best=AgentGroup2.enemyIndexes[0]
      if AgentGroup2.blue and gameState.getScore()>AgentGroup2.oldScore:
        for eindex in AgentGroup2.enemyIndexes:
          if abs(AgentGroup2.dicFoodCarried.get(eindex)-(gameState.getScore() - AgentGroup2.oldScore))+abs(AgentGroup2.dicPos.get(eindex)[0]-AgentGroup2.mid)<min:
            min=abs(AgentGroup2.dicFoodCarried.get(eindex)-(gameState.getScore() - AgentGroup2.oldScore))+abs(AgentGroup2.dicPos.get(eindex)[0]-AgentGroup2.mid)
            best=eindex
        AgentGroup2.dicFoodCarried[best] = 0
      elif not AgentGroup2.blue and gameState.getScore()<AgentGroup2.oldScore:
        for eindex in AgentGroup2.enemyIndexes:
          if abs(AgentGroup2.dicFoodCarried.get(eindex)+(gameState.getScore() - AgentGroup2.oldScore))+abs(AgentGroup2.dicPos.get(eindex)[0]-AgentGroup2.mid)<min:
            min=abs(AgentGroup2.dicFoodCarried.get(eindex)+(gameState.getScore() - AgentGroup2.oldScore))+abs(AgentGroup2.dicPos.get(eindex)[0]-AgentGroup2.mid)
            best=eindex
        AgentGroup2.dicFoodCarried[best] = 0
      AgentGroup2.oldScore=gameState.getScore()



      """    Check if the enemies are in sight    """
      for eindex in AgentGroup2.enemyIndexes:
        if(gameState.getAgentPosition(eindex)!=None):
          AgentGroup2.partFilters[eindex].knownThisPos(gameState.getAgentPosition(eindex))



      # if type(self.aim)==tuple:
      #   self.debugDraw(self.aim, [1, 0, 0], True)

      # """    Draw the particles    """
      # if True:
      #     for eindex in AgentGroup2.enemyIndexes:
      #       AgentGroup2.partFilters[eindex].draw()

      """    Save our old food array (to check if something hes been eaten    """
      self.myOldFoodBoolArray=self.myFoodBoolArray




      """      Update dicPos      """
      for eindex in AgentGroup2.enemyIndexes:
          AgentGroup2.dicPos[eindex]=AgentGroup2.partFilters.get(eindex).findBest()


      '''      Check if an enemy died      '''
      for eindex in AgentGroup2.enemyIndexes:
        if abs(AgentGroup2.dicStartPos.get(eindex)[0]-AgentGroup2.dicPos.get(eindex)[0])<6:
          AgentGroup2.dicFoodCarried[eindex]=0


      """      Draw dicPos      """
      if False:
          self.debugDraw(self.myPos, [1, 0, 0], True)
          for eindex in AgentGroup2.enemyIndexes:
              self.debugDraw(AgentGroup2.dicPos[eindex], [1, 0, 0], False)
          for index in AgentGroup2.myIndexes:
              self.debugDraw(AgentGroup2.dicPos[index], [1, 0, 0], False)



      '''      Update the roles      '''

      if(self.twoShouldDefend()):#if one of their agent has carries a lot or if we are too behind
        self.makeTwoDefend()

      elif(self.twoShouldAttack()):#
        self.makeTwoAttack()
      else:
        self.makeOneDefend()



      # print '______________________________________________________________________________'
      if AgentGroup2.dicRoles.get(self.index)=='a':
        # print self.index, "ATTACKER"
        self.AteCapsule()
        self.iKilledWithCapsule()
        tree = Fallback([
          # if i died i need to find a new food target
          Sequence([self.iDied,self.findFoodTarget]).run,   # 0 get into position

          Sequence([self.enemyClose,self.myTurf,self.chaseEnemy]).run,

          # if there's an enemy close but we can eat them,
          # chase them (until capsule close to running out)
          Sequence([self.capsuleActive,self.enemyClose,self.chaseEnemy]).run, 
          # if there is an enemy close, capsule close
          # and i am closer to the capsule than the enemy,
          # go to capsule
          Sequence([self.capsuleClose,self.eatCapsule]).run, 
          # if there is an enemy close i need to run away
          Sequence([self.enemyClose,self.runAway]).run,     # 1    
          # if i have too much food i go home
          Sequence([self.iAteTooMuch,self.goHome]).run,     # 2
          # if not i grab food
          Sequence([self.iAte,self.findFoodTarget]).run     # 3
        ])
        tree.run()
      else:
        # print self.index, "Defender"
        self.enemyAteCapsule()
        tree = Fallback([

          # if near enemy but enemy has eaten capsule, keep your distance
          Sequence([self.enemyCapsuleActive,self.enemyClose,self.runAway]).run,
          Sequence([self.iDied,self.randomPatrol]).run,  # 5
          # if killed enemy, start patrolling again
          Sequence([self.iKilled,self.randomPatrol]).run, # 5
          # try to eat enemy pacmans (even if they are far)
          Sequence([self.enemyVisible,self.chaseEnemy]).run,
          # if no enemy is visible but some of our food disappeared,
          # aim for the food closest to the last disappeared food
          Sequence([self.foodMissing,self.closestToMissing]).run,
          # if choose another random friendly pill
          Sequence([self.iChecked,self.randomPatrol]).run
        ])
        tree.run()
      #Elapsed time during decision making
      chosenAction = self.findBestActionWithTree(startTime)

      AgentGroup2.aims[self.index]=self.aim

      # print self.index, self.behaviour, self.aim
      # if(self.myPos[0]>10):
      #   raw_input()
      if(self.index<2):
      #   # print self.index, self.behaviour, self.aim
      #   if(self.behaviour == 3 or self.behaviour == 1):
      #     # print self.aim
      #     raw_input()
        print time.time()-startTime
        # print self.index, self.behaviour, self.myPos, self.aim, self.getMazeDistance(self.myPos,self.aim)
        # if(self.danger):
        #   print "aim", self.aim
        #   raw_input()
      return chosenAction




  '''
  Functions that return data
  '''
  def twoShouldDefend(self):
    sum=0
    for eindex in AgentGroup2.enemyIndexes:
      sum+=AgentGroup2.dicFoodCarried.get(eindex)
    if sum>=6 and self.capsuleEnemy==0:
      return True
    # print AgentGroup2.dicFoodCarried
    return False

  def makeTwoDefend(self):
    max1 = 0
    idmax1=-1
    idmax2=-1
    max2 = 0
    for eindex in AgentGroup2.enemyIndexes:
      if AgentGroup2.dicFoodCarried.get(eindex)>max1:
        idmax2=idmax1
        max2=max1
        idmax1=eindex
        max1=AgentGroup2.dicFoodCarried.get(eindex)
      elif AgentGroup2.dicFoodCarried.get(eindex)>max2:
        idmax2=eindex
        max2=AgentGroup2.dicFoodCarried.get(eindex)
    min1=9999
    min2=9999
    idmin1=0
    idmin2=0
    if idmax2>0:
      for index in AgentGroup2.myIndexes:
        dist=self.getMazeDistance(self.myPos,AgentGroup2.dicPos.get(idmax1))+self.getMazeDistance(self.myPos,AgentGroup2.dicPos.get(idmax2))
        if dist<min1:
          min2=min1
          idmin2=idmin1
          min1=dist
          idmin1=index
        elif dist<min2:
          min2=dist
          idmin2=index
    else:
      for index in AgentGroup2.myIndexes:
        dist=self.getMazeDistance(self.myPos,AgentGroup2.dicPos.get(idmax1))
        if dist<min1:
          min2=min1
          idmin2=idmin1
          min1=dist
          idmin1=index
        elif dist<min2:
          min2=dist
          idmin2=index
      for index in AgentGroup2.myIndexes:
        if index==idmin1 or index==idmin2:
          AgentGroup2.dicRoles[index]='d'
        else:
          AgentGroup2.dicRoles[index]='a'

  def twoShouldAttack(self):
    shouldDefend=False
    for eindex in AgentGroup2.enemyIndexes:
      if abs(AgentGroup2.dicPos.get(eindex)[0]-AgentGroup2.dicStartPos.get(eindex)[0])>5:
        shouldDefend=True
    if not shouldDefend:
      return True
    return False


  def makeTwoAttack(self):
    min1=9999
    min2=9999
    idmin1=0
    idmin2=0
    for index in AgentGroup2.myIndexes:
      min=999
      best = None
      for i in range(1, self.distancer.dc.layout.height - 1):
        if not self.distancer.dc.layout.isWall((self.mid, i)):
          if self.getMazeDistance((self.mid, i), self.myPos) < min:
            min = self.getMazeDistance((self.mid, i), self.myPos)
            best = (self.mid, i)
      dist=self.getMazeDistance(self.myPos,best)
      if dist<min1:
        min2=min1
        idmin2=idmin1
        min1=dist
        idmin1=index
      elif dist<min2:
        min2=dist
        idmin2=index
    for index in AgentGroup2.myIndexes:
      if index==idmin1 or index==idmin2:
        AgentGroup2.dicRoles[index]='a'
      else:
        AgentGroup2.dicRoles[index]='d'

  def makeOneDefend(self):
    idmax=-1
    max=0
    for eindex in AgentGroup2.enemyIndexes:
      if AgentGroup2.dicFoodCarried.get(eindex)>max:
        idmax=eindex
    if idmax>=0:
      min=999
      for index in AgentGroup2.myIndexes:
        dist=self.getMazeDistance(AgentGroup2.dicPos[index],AgentGroup2.dicPos.get(idmax))
        if AgentGroup2.dicRoles.get(index)=='a' and dist+3<min:
          min=dist
          best=index
        elif AgentGroup2.dicRoles.get(index)=='d' and dist<min:
          best=index
          min=dist
    else:
      min=999
      for index in AgentGroup2.myIndexes:
        if AgentGroup2.dicPos[index][0] < AgentGroup2.dicStartPos.get(index)[0]:
          best = index
          min = AgentGroup2.dicPos[index][0]
    for index in AgentGroup2.myIndexes:
      if index==best:
        AgentGroup2.dicRoles[index]='d'
      else:
        AgentGroup2.dicRoles[index]='a'




  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def closestFood(self,foodList):
    min=9999
    if(len(foodList)==0):
      return self.startPos
    best=foodList[0]
    for food in foodList:
      dist = self.getMazeDistance(self.myPos, food)
      if dist < min:
        best = food
        min = dist
    return best

  def closestFoods(self,foodList,maxDist):
    min = 9999
    closestFoodsList=[]
    if (len(foodList) == 0):
      return self.startPos
    for food in foodList:
      dist = self.getMazeDistance(self.myPos, food)
      if dist < min:
        min = dist
    for food in foodList:
      dist = self.getMazeDistance(self.myPos, food)
      if dist < min+maxDist:
        closestFoodsList.append(food)
    return closestFoodsList

  def findInvaders(self, successor):
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    return [a for a in enemies if a.isPacman and a.getPosition() != None]


  def countFood(self,foodBoolArray):
    i=0
    for a in foodBoolArray:
      for b in a:
        if b:
          i+=1
    return i

  def myFoodChanged(self,foodBoolArray,oldFoodBoolArray):
    if foodBoolArray==None or oldFoodBoolArray==None:
      return None
    length = 0
    for a in foodBoolArray:
        length += 1
    for i in range(0,length):
      for j in range(0,len(foodBoolArray[0])):
        if foodBoolArray[i][j]!=oldFoodBoolArray[i][j]:
          return (i,j)
    return None

  '''
  Functions that return stuff for the behavior tree
  '''

  def resetCounter(self):
    # print("index: " + str(self.index) + "  resetCounter")
    self.counter=0

  def iDied(self):
    #print("index: "+str(self.index)+"  iDied")
    self.behaviour = 0
    self.danger = False
    if self.myPos==self.startPos:
      self.counter=0
      self.gameState.getAgentPosition(self.index)
      return 'done'
      # print "I died"
    else:
      # print "I did not die"
      return 'failed'

  def iAte(self):
    #print("index: " + str(self.index) + "  iAte")
    self.behaviour = 0
    if self.myPos==self.aim and not self.danger:
      self.counter+=1
      return 'done'
    else:
      return 'failure'

  def iAteTooMuch(self):
    #print("index: " + str(self.index) + "  iAteTooMuch      counter:"+str(self.counter))
    minDist=9999
    for eindex in AgentGroup2.enemyIndexes:
      if self.getMazeDistance(self.myPos,AgentGroup2.dicPos[eindex])<minDist:
        minDist=self.getMazeDistance(self.myPos,AgentGroup2.dicPos[eindex])
    if minDist>12 and self.counter>=2*self.foodLimit:
      return 'failed'
    if self.counter>=self.foodLimit:
      self.behaviour = 2
      return 'done'
    else:
      return 'failed'

  def iKilled(self):
    #print("index: "+str(self.index)+"  iDied")
    if self.myPos == self.enemyPos:
      self.behaviour = 0
      self.lastFoodLost = None
      if self.capsuleEffect > 0:
        self.killCounter += 1
      return 'done'
    else:
      return 'failed'

  def iKilledWithCapsule(self):
    if self.myPos == self.enemyPos and self.capsuleEffect > 0:
      self.killCounter += 1

  def capsuleClose(self):

    minDist = 6
    minCapsule = None
    for capsule in self.capsules:
      dist = self.getMazeDistance(self.myPos,capsule)
      if dist < minDist:
        minDist = dist
        minCapsule = capsule
    
    if minCapsule != None and self.enemyClose() == 'done':
      if self.getMazeDistance(self.myPos,minCapsule) < self.getMazeDistance(self.enemyPos,minCapsule):
        self.behaviour = 3
        return 'done'
    else:
      return 'failed'

  def AteCapsule(self):
    flag = False
    for capsule in self.capsules:
      if self.myPos == capsule:
        self.capsuleEffect = 33
        self.foodLimit = 10
        flag = True
        break
    if flag:
      self.capsules.remove(capsule)

  def enemyAteCapsule(self):
    if self.blue:
      enemyCaps = self.gameState.getBlueCapsules()
    else:
      enemyCaps = self.gameState.getRedCapsules()
    
    for capsule in self.enemyCapsules:
      if capsule not in enemyCaps:
        self.capsuleEnemy = 38
        self.enemyCapsules.remove(capsule)
        break


  def capsuleActive(self):
    if self.killCounter == self.nbAgents:
      self.capsuleEffect = 0
      self.killCounter = 0
      return 'failed'

    if self.capsuleEffect > 10:
      self.capsuleEffect -= 1
      return 'done'
    elif self.capsuleEffect > 0:
      self.capsuleEffect -= 1
      self.foodLimit = 3
      return 'done'

    self.killCounter = 0
    return 'failed'

  def enemyCapsuleActive(self):
    if self.capsuleEnemy > 1:
      self.capsuleEnemy -= 1
      return 'done'
    return 'failed'

  def enemyClose(self):
    # print("index: " + str(self.index) + "  enemyClose")
    if AgentGroup2.myMinX<self.myPos[0] and self.myPos[0]<AgentGroup2.myMaxX:
      # print 'enemy close failed'
      return 'failed'
    min = 9999
    for eindex in AgentGroup2.enemyIndexes:
      if (self.gameState.getAgentPosition(eindex) != None):
        dist = self.getMazeDistance(self.myPos, self.gameState.getAgentPosition(eindex))
        if dist < min:
          min = dist
          self.enemyPos = self.gameState.getAgentPosition(eindex)
          self.enemyCloseIndex = eindex
    if min<self.securityDistance:
      self.danger=True
      # print 'enemy close done'
      return 'done'
    else:
      self.danger = False
      # print 'enemy close failed'
      return 'failed'

  def myTurf(self):
    if self.blue:
      if self.myPos[0]>self.mid and self.enemyPos[0]>self.mid-1:
        # print 'turf'
        return 'done'
    else:
      if self.myPos[0]<self.mid and self.enemyPos[0]<self.mid+1:
        # print 'turf'
        return 'done' 
    return 'failed'

  def enemyVisible(self):
    # print("index: " + str(self.index) + "  enemyClose")
    min = 9999
    allenemies = [self.successor.getAgentState(i) for i in self.getOpponents(self.successor)]
    enemies = [a for a in allenemies if a.isPacman and a.getPosition() != None]
    if len(enemies)==0:
      self.danger = 0
      return 'failed'
    for enemy in enemies:
      if(enemy.getPosition()!=None):

        dist = self.getMazeDistance(self.myPos, enemy.getPosition())
        if dist < min:
          min=dist
          self.enemyPos = enemy.getPosition()
    if min > self.securityDistance:
      self.danger = 0
    return 'done'

  def foodMissing(self):
    if self.foodLost != None:
      self.lastFoodLost = self.foodLost
      return 'done'
    elif self.lastFoodLost != None:
      return 'done'
    else:
      return 'failed'

  def closestToMissing(self):
    # print("index: " + str(self.index) + "  closestToMissing")
    if self.myFoodBoolArray==None:
      self.behavior = 0
      return
    self.behavior = 3
    length = 0
    for a in self.myFoodBoolArray:
        length += 1
    minDist = 999
    closestFood = None
    for i in range(0,length):
      for j in range(0,len(self.myFoodBoolArray[0])):
          if self.myFoodBoolArray[i][j]==True:
            dist = self.getMazeDistance((i,j),self.lastFoodLost)
            if dist < minDist:
              minDist = dist
              closestFood = (i,j)
    if closestFood != None:
      self.aim = closestFood
    else:
      self.behavior = 0

  def runAway(self):
    self.behaviour = 1
    # print("index: " + str(self.index) + "  runAway")
    min = 9999
    allenemies = [self.successor.getAgentState(i) for i in self.getOpponents(self.successor)]
    enemies = [a for a in allenemies if not a.isPacman and a.getPosition() != None]
    closest=None
    if len(enemies)==0:
      return 'failed'
    for enemy in enemies:
      if (enemy.getPosition() != None):
        dist = self.getMazeDistance(self.myPos, enemy.getPosition())
        if dist < min:
          closest = enemy
          min = dist
    if closest!=None:
      # print '__________________________________________________________'
      # print '__________________________________________________________'
      min=9999
      best = (self.mid, self.myPos[1])
      for i in range(1, AgentGroup2.YLENGTH - 1):
        if not self.gameState.hasWall(self.mid, i):
          if self.getMazeDistance((self.mid, i), self.myPos) < min:
            min = self.getMazeDistance((self.mid, i), self.myPos)
            best = (self.mid, i)
      min=9999
      max=self.getMazeDistance(self.myPos, closest.getPosition())
      actions = self.gameState.getLegalActions(self.index)
      for act in actions:
        successor2 = self.getSuccessor(self.gameState, act)
        pos2 = successor2.getAgentPosition(self.index)
        if pos2!=self.startPos and (2*self.getMazeDistance(best,pos2)-self.getMazeDistance(closest.getPosition(),pos2))<min:
          self.aim=pos2
          min = (2*self.getMazeDistance(best,pos2)-self.getMazeDistance(closest.getPosition(),pos2))
      #self.aim = 'None'
      return 'done'
    return 'failed'

  def chaseEnemy(self):
    # print("index: " + str(self.index) + "  chaseEnemy")
    min = 9999
    allenemies = [self.successor.getAgentState(i) for i in self.getOpponents(self.successor)]
    enemies = [a for a in allenemies if a.getPosition() != None]
    closest=None
    if len(enemies)==0:
      return 'failed'
    for enemy in enemies:
      if (enemy.getPosition() != None):
        dist = self.getMazeDistance(self.myPos, enemy.getPosition())
        if dist < min:
          closest = enemy.getPosition()
          min = dist
    if closest!=None:
      self.aim = closest
      self.behaviour = 3
      # print "CHASE", self.index, self.behaviour, self.aim
      return 'done'
    return 'failed'  

  def eatCapsule(self):
    # print("index: " + str(self.index) + "  eatCapsule")
    minCapsule = None
    minDist = 999
    for capsule in self.capsules:
      dist = self.getMazeDistance(self.myPos,capsule)
      if dist < minDist:
        minDist = dist
        minCapsule = capsule
    self.aim = minCapsule


  def randomPatrol(self):
    # print("index: " + str(self.index) + "  randomPatrol")
    foodLeft = self.getFoodYouAreDefending(self.gameState).asList()
    if not self.blue:
      max_x = max([i[0] for i in foodLeft])
    else:
      pass
      min_x = min([i[0] for i in foodLeft])
    while len(foodLeft)>0:
      self.aim = random.choice(foodLeft)
      if not self.blue and (self.aim[0] > self.mid/3 or max_x <= self.mid/3):
        break
      elif self.blue and (self.aim[0] < self.mid*5/3 or min_x >= self.mid*5/3):
        break

  def iChecked(self):
    # print("index: " + str(self.index) + "  iChecked")
    if self.getMazeDistance(self.myPos,self.aim)<3:
      return 'done'
    else:
      return 'failed'

  def findFoodTarget(self):
    # print("index: " + str(self.index) + "  findFoodTarget")
    foodLeft = self.getFood(self.gameState).asList()
    for index in AgentGroup2.myIndexes:
      if self.index!=index:
        if len(foodLeft)>0 and self.closestFood(foodLeft) == AgentGroup2.aims.get(index):
          foodLeft.remove(AgentGroup2.aims.get(index))
          print 'one food removed'
    self.aim = self.closestFood(foodLeft)

  def findBestAction(self):
    # print("index: " + str(self.index) + "  findBestAction")
    actions = self.gameState.getLegalActions(self.index)
    bestDist = 9999
    for action in actions:
      successor = self.getSuccessor(self.gameState, action)
      pos2 = successor.getAgentPosition(self.index)
      dist = self.getMazeDistance(self.aim, pos2)
      if dist < bestDist:
        bestAction = action
        bestDist = dist
    return bestAction

  def goHome(self):
    # print("index: " + str(self.index) + "  goHome")
    min=9999
    best=None
    for i in range(1,self.distancer.dc.layout.height-1):
      if not self.distancer.dc.layout.isWall((self.mid,i)):
        if self.getMazeDistance((self.mid,i),self.myPos)<min:
          min=self.getMazeDistance((self.mid,i),self.myPos)
          best=(self.mid,i)
    if best!=None:
      self.aim=best
    else:
      self.aim=self.startPos
    if self.getMazeDistance(self.myPos,self.aim)==0:
      self.counter=0
      return 'done'
    return 'running'


  def selectNode(self,root):
    if self.aim != 'None':
      maxTreeDepth = min(6,self.getMazeDistance(self.myPos,self.aim))-1
    else:
      maxTreeDepth = 5
    treeDepth = 1
    currNode = root

    #C = np.sqrt(20)

    while treeDepth < maxTreeDepth:
      treeDepth += 1
      if not currNode.children:
        return currNode

      maxScore = -9999
      maxNode = None
      for child in currNode.children:
        if child.score == None:
          return child
      currNode = random.choice(currNode.children)
          # ucb1Score = child.score + C*np.sqrt(np.log(currNode.numVisits)/child.numVisits)
          # if ucb1Score > maxScore:
          #   maxNode = child
          #   maxScore = ucb1Score
      
      # currNode = maxNode

    return currNode

  def expandNode(self,node):
    availableMoves = node.id.getLegalActions(self.index)
    for move in availableMoves:
      nextGameState = self.getSuccessor(node.id,move)
      if nextGameState in self.stateDict:
        continue
      newChild = mcTree(nextGameState,node)
      node.children.append(newChild)
      self.stateDict[nextGameState] = newChild
    
    if not node.children:
      return node
    return random.choice(node.children)

  def reverseDirection(self,action):
      if action == Directions.NORTH:
          return Directions.SOUTH
      if action == Directions.SOUTH:
          return Directions.NORTH
      if action == Directions.EAST:
          return Directions.WEST
      if action == Directions.WEST:
          return Directions.EAST
      return action

  def simulateOpponent(self,currState,currentPos,enemyPos):

    minDist = self.getMazeDistance(currentPos,enemyPos)
    minPos = enemyPos
    myPos = currState.getAgentPosition(self.index)

    if not currState.hasWall(enemyPos[0]+1,enemyPos[1]):
      eastPos = (enemyPos[0]+1, enemyPos[1])
      if(self.getMazeDistance(myPos,eastPos)<minDist):
        minDist = self.getMazeDistance(myPos,eastPos)
        minPos = eastPos

    if not currState.hasWall(enemyPos[0]-1,enemyPos[1]):
      westPos = (enemyPos[0]-1, enemyPos[1])
      if(self.getMazeDistance(myPos,westPos)<=minDist):
        minDist = self.getMazeDistance(myPos,westPos)
        minPos = westPos

    if not currState.hasWall(enemyPos[0],enemyPos[1]+1):
      northPos = (enemyPos[0], enemyPos[1]+1)
      if(self.getMazeDistance(myPos,northPos)<=minDist):
        minDist = self.getMazeDistance(myPos,northPos)
        minPos = northPos

    if not currState.hasWall(enemyPos[0],enemyPos[1]-1):
      southPos = (enemyPos[0], enemyPos[1]-1)
      if(self.getMazeDistance(myPos,southPos)<=minDist):
        minDist = self.getMazeDistance(myPos,southPos)
        minPos = southPos
    
    # print myPos, enemyPos, minPos
    # raw_input()
    return minPos

  def simulateGame(self,simStart):
    turnCounter = 0
    if self.aim != 'None':
      turnLimit = min(5,self.getMazeDistance(self.myPos,self.aim))
    else:
      turnLimit = 5
    currState = simStart.id
    prevAction = Directions.STOP
    enemyPosition = self.enemyPos
    # print currState, prevAction
    # raw_input()
    while(turnCounter < turnLimit):
      actions = currState.getLegalActions(self.index)
      actions.remove(Directions.STOP)
      # print self.reverseDirection(prevAction)
      if self.behaviour == 0 and prevAction!=Directions.STOP and len(actions) > 1:
        try:
          actions.remove(self.reverseDirection(prevAction))
        except ValueError:
          pass

      nextAction = random.choice(actions)
      turnCounter += 1
      currState = self.getSuccessor(currState, nextAction)
      prevAction = nextAction
      if(self.behaviour == 1):
        currentPos = currState.getAgentPosition(self.index)
        if(currentPos[0]==self.spawnLane):
          return -999999
        enemyPosition = self.simulateOpponent(currState,currentPos,enemyPosition)
        if(enemyPosition==currentPos):
          return -999999

    # print currState
    # raw_input()
    return self.simScore(currState,enemyPosition) 

  def spawnScore(self,currPos,currState):
    # print currPos, self.aim, self.getMazeDistance(currPos, self.aim)
    #(currState.getScore()-self.gameState.getScore()*60)
    return -self.getMazeDistance(currPos, self.aim)*50

  def escapeScore(self,currPos,enemyPosition):
    if(currPos[0]==self.spawnLane or currPos==enemyPosition):
      return -999999
    if(enemyPosition!=None):
      return -self.getMazeDistance(currPos, self.aim)*50 + self.getMazeDistance(currPos, enemyPosition)*40
    else:
      return -self.getMazeDistance(currPos, self.aim)*50

  def depositScore(self,currPos,currState):
     return -self.getMazeDistance(currPos, self.aim)*5
     #(currState.getScore()-self.gameState.getScore()*500)
  def chaseScore(self,currPos,currState):
    # print currPos, self.aim, self.getMazeDistance(currPos, self.aim)
    # raw_input()
    return -self.getMazeDistance(currPos, self.aim)*50
    #currState.getScore()*500
  def simScore(self,currState,enemyPosition):

      currPos = currState.getAgentPosition(self.index)
      if self.behaviour == 0:
        return self.spawnScore(currPos,currState)
      elif self.behaviour == 1:
        return self.escapeScore(currPos,enemyPosition)
      elif self.behaviour == 2:
        return self.depositScore(currPos,currState)
      else:
        return self.chaseScore(currPos,currState)

    # newScore = currState.getScore()
    # oldScore = startState.getScore()
    # if newScore != oldScore:
    #   return (newScore - oldScore)*50
     
    # newSoftScore = currState.data.agentStates[self.index].numCarrying*10
    # oldSoftScore = startState.data.agentStates[self.index].numCarrying*10

    # newSoftScore -= (20-currState.getRedFood().count())*10
    # oldSoftScore -= (20-startState.getRedFood().count())*10
    # if newSoftScore != oldSoftScore:
    #   return newSoftScore - oldSoftScore

    # initPos = startState.getAgentPosition(self.index)
    # currPos = currState.getAgentPosition(self.index)

    # aggression = 0
    # if not startState.data.agentStates[self.index].isPacman:
    #   aggression = np.abs(self.mid-self.myPos[0])*5

    # return self.getMazeDistance(initPos, currPos) + aggression



  def backpropagateScore(self,value,simStart):
    simStart.numVisits += 1
    simStart.value += value
    currNode = simStart
    simStart.score = simStart.value/simStart.numVisits

    # print "score: ", currNode.value, currNode.numVisits, currNode.score
    # print currNode.id.getAgentState(self.index).getPosition()
    # raw_input()
    while(currNode.parent != None):
      currNode = currNode.parent
      currNode.value += value
      currNode.numVisits += 1
      currNode.score = currNode.value/currNode.numVisits
      
      # if(self.index==0):
      #   print "score: ", currNode.value, currNode.numVisits, currNode.score
      #   print currNode.id.getAgentState(self.index).getPosition()
      #   raw_input()
      

  def printTree(self,root,depth):
    if(depth==0):
      print "root", root.id.getAgentState(self.index).getPosition(), root.score
    currNode = root
    depth += 1
    for child in currNode.children:
      for i in range(0,depth):
        print " ",
      print "depth ", depth, child.id.getAgentState(self.index).getPosition(), child.score
      self.printTree(child,depth)


  def monteCarloTreeSearch(self,startTime):
    self.stateDict = dict()
    currGameState = self.gameState

    maxSimulations = 300
    counter = 0
    root = mcTree(currGameState)
    self.stateDict[root.id] = root
    # currNode = root
    while(counter < maxSimulations):
      nodeForExpansion = self.selectNode(root)
      simStart = self.expandNode(nodeForExpansion)
      value = self.simulateGame(simStart)
      # print "VAL", value
      self.backpropagateScore(value,simStart)
      counter += 1
      # if time.time()-startTime>0.493:
      #   break
    # if(self.index==0 and self.getMazeDistance(self.myPos,self.aim)==1):
    #   self.printTree(root,0)
    #   raw_input()
  def findBestActionWithTree(self,startTime):
    # if(self.index!=0):
    #   return 'Stop'
    self.monteCarloTreeSearch(startTime)
    actions = self.gameState.getLegalActions(self.index)
    bestValue = -999999999
    bestAction = random.choice(actions)
    # if(self.index==0):
    #   print "behaviour= ", self.behaviour, "aim = ", self.aim, "danger = ", self.danger
    for action in actions:
      if action == 'Stop' or (self.behaviour == 0 and action == self.reverseDirection(self.myAction) and len(actions)>2):
        continue
      successor = self.getSuccessor(self.gameState, action)
      value = self.stateDict[successor].score
      # print(value)
      # if(self.index==0 and (self.behaviour == 0 or self.behaviour == 0) and self.getMazeDistance(self.myPos,self.aim)==1):
      #   print("action = ",action, value, self.stateDict[successor].value, self.stateDict[successor].numVisits)
      #raw_input()     
      if value > bestValue:
        bestValue = value
        bestAction = action
    self.myAction = bestAction
    # if(self.index==0 and (self.behaviour == 0 or self.behaviour == 0) and self.getMazeDistance(self.myPos,self.aim)==1):
    #   print "best action = ", bestAction
    #   raw_input()
    return bestAction 


class ParticleFilter:
  NUMBER_PARTICLES=100
  XLENGTH=0
  YLENGTH=0
  gameState=None
  bestIndex=0


  def __init__(self,gameState,agent,bestIndex,startPos=None):
    self.gameState=gameState
    self.agent=agent
    self.bestIndex=bestIndex
    self.bestEstimate=(1,1)
    i=0
    for a in gameState.getWalls():
      i+=1
    self.XLENGTH=i
    self.YLENGTH=len(gameState.getWalls()[0])
    self.NUMBER_PARTICLES=len(gameState.getWalls()[0])*i*1
    self.particles=[]
    if startPos is not None:
      for i in range(0,self.NUMBER_PARTICLES):
        self.particles.append((startPos[0],startPos[1]))

      for i in range(-2,3):
        for j in range(-2,3):
          if not gameState.hasWall(i, j):
            self.particles.append((i, j))

    else:
      for i in range(0,self.XLENGTH):
        for j in range(0, self.YLENGTH):
          if not gameState.hasWall(i,j):
            self.particles.append((i,j))
      originalParticles= copy.deepcopy(self.particles)
      for i in range(len(self.particles),self.NUMBER_PARTICLES):
        self.particles.append(random.choice(originalParticles))

  def resetParticles(self,startPos=None):
    self.particles=[]
    if startPos is not None:
      for i in range(0,self.NUMBER_PARTICLES):
        self.particles.append((startPos[0],startPos[1]))
    else:
      for i in range(0,self.XLENGTH):
        for j in range(0, self.YLENGTH):
          if not self.gameState.hasWall(i,j):
            self.particles.append((i,j))
      originalParticles= copy.deepcopy(self.particles)
      for i in range(len(self.particles),self.NUMBER_PARTICLES):
        self.particles.append(random.choice(originalParticles))

  def draw(self):
    for i in range(0, self.XLENGTH):
      for j in range(0, self.YLENGTH):
        if (i,j) in self.particles:
          self.agent.debugDraw((i,j), [0, 1, 1], False)

  def drawBest(self):
    self.agent.debugDraw(self.findBest(), [0, 1, 0], False)



  def update(self, pos, dist,index):
    if(index==self.bestIndex):
      originalParticles= copy.deepcopy(self.particles)
      visited=[]
      self.particles=[]
      for part in originalParticles:
        moves=self.getPossibleMoves(part)
        if not part in visited:
          visited.append(part)
          for move in moves:
            if abs(abs(move[0] - pos[0]) + abs(move[1] - pos[1]) - max(dist, 0)) <= 6:
              self.particles.append(move)
        else:
          if len(moves)>1:
            if random.randint(0,100)<8:
              move=moves[-1]
            else:
              move=moves[random.randint(0,len(move)-2)]
              if random.randint(0, 100) < 70:
                for choice in moves:
                  distToBest = abs(choice[0] - self.bestEstimate[0]) + abs(choice[1] - self.bestEstimate[1])
                  if distToBest>abs(part[0] - self.bestEstimate[0]) + abs(part[1] - self.bestEstimate[1]):
                    move=choice
          else:
            move=random.choice(moves)
          if abs(abs(move[0] - pos[0]) + abs(move[1] - pos[1]) - max(dist, 0)) <= 6:
            self.particles.append(move)
    else:
      originalParticles = copy.deepcopy(self.particles)
      self.particles = []
      for part in originalParticles:
        if (part == None):
          print 'NONE!!!!!'
        if (pos == None):
          print 'pos is NONE!!!'
        if abs(abs(part[0] - pos[0]) + abs(part[1] - pos[1]) - max(dist, 0)) <= 6:
          self.particles.append(part)
    originalParticles = copy.deepcopy(self.particles)

    if len(originalParticles)==0:
      self.resetParticles()
    else:
      for i in range(len(self.particles), self.NUMBER_PARTICLES):
        self.particles.append(random.choice(originalParticles))

    self.bestEstimate=self.findBest()


  def knownPos(self,pos,otherFilters):
    inOtherFilters=False
    for filter in otherFilters:
      if filter!=self and filter.hasPos(pos):
        inOtherFilters=True
    if pos in self.particles and not inOtherFilters:
      self.particles=[]
      for i in range(0,self.NUMBER_PARTICLES):
        self.particles.append(pos)
    else:
      for i in range(0,int(self.NUMBER_PARTICLES/len(otherFilters))):
        self.particles.append(pos)

  def hasPos(self,pos):
    return pos in self.particles


  def knownThisPos(self,pos):
    self.particles=[]
    for i in range(0,self.NUMBER_PARTICLES):
      self.particles.append(pos)


  def findBest(self):
    visited=[]
    max=0
    best=None
    for part in self.particles:
      if not part in visited:
        visited.append(part)
        count=self.particles.count(part)
        if(count>max):
          best=part
          max=count
    return best

  def getNumberOfCells(self):
    count=0
    for i in range(0, self.XLENGTH):
      for j in range(0, self.YLENGTH):
        if (i,j) in self.particles:
          count+=1
    return count



  def testForNone(self):
    for part in self.particles:
      if part==None:
        print 'part is none'

  def getPossibleMoves(self,part):
    possibleMoves=[]
    if not self.gameState.hasWall(part[0]+1,part[1]):
      possibleMoves.append((part[0]+1,part[1]))
    if not self.gameState.hasWall(part[0]-1,part[1]):
      possibleMoves.append((part[0]-1,part[1]))
    if not self.gameState.hasWall(part[0],part[1]+1):
      possibleMoves.append((part[0],part[1]+1))
    if not self.gameState.hasWall(part[0],part[1]-1):
      possibleMoves.append((part[0],part[1]-1))
    possibleMoves.append((part[0],part[1]))
    return possibleMoves



