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
import numpy as np
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
  foodLimit=3
  mid=0
  aims = dict({})
  indexes=[]
  myFoodBoolArray=None
  myOldFoodBoolArray=None
  XLENGTH = 0
  YLENGTH = 0
  blue=True
  dicPos={}
  dicStartPos={}
  partFilters=dict({})
  enemyIndexes=[]
  myIndexes=[]
  nbAgents=2
  myMinX=0
  myMaxX=0

  def __init__(self, index):
    CaptureAgent.__init__(self,index)
    self.aim=[1,3]
    self.counter=0
    self.startPos=self.aim
    self.myPos=[1,3]
    self.myOldPos=[1,3]
    self.successor= None
    self.gameState= None
    self.danger=False
    self.aims[index]=self.aim









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

    """    Compute the mid x (the one on our side)    """
    AgentGroup2.mid = self.distancer.dc.layout.width / 2
    if (self.startPos[0] < self.mid):
      AgentGroup2.mid -= 1

    """    Determine if we are blue or red team    """
    if(self.index<=1):
      self.blue = not gameState.isOnRedTeam(self.index)

    """    Initialize indexes    """
    if(self.index<=1):
      if(AgentGroup2.blue):
        AgentGroup2.myIndexes=gameState.getBlueTeamIndices()
        AgentGroup2.enemyIndexes=gameState.getRedTeamIndices()
      else:
        AgentGroup2.myIndexes = gameState.getRedTeamIndices()
        AgentGroup2.enemyIndexes = gameState.getBlueTeamIndices()

    """    Count number of agents per team     """
    AgentGroup2.nbAgents=len(AgentGroup2.myIndexes)

    """    Initialize my starting position    """
    self.startPos = self.myPos

    """    Innitialise dictionary of positions (needed for simulation)    """
    AgentGroup2.dicPos[self.index]=self.myPos
    if(self.index<=1):
      for index in AgentGroup2.enemyIndexes:
        AgentGroup2.dicPos[index]=gameState.getInitialAgentPosition(index)

    """    Innitialise dictionary of starting positions (needed for simulation)    """
    AgentGroup2.dicStartPos[self.index] = self.myPos
    if (self.index <= 1):
        for index in AgentGroup2.enemyIndexes:
            AgentGroup2.dicPos[index] = gameState.getInitialAgentPosition(index)


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

    #Example as how to run a simulation
    agentIndex=self.index
    #direction diven by the node of the tree
    direction="South"
    dicPos={0:(1,1),1:self.startPos,2:(1,1),3:self.startPos}
    sim = Simulation(gameState,AgentGroup2.XLENGTH,AgentGroup2.YLENGTH,self.blue,dicPos,agentIndex,direction,False,False,0,0,AgentGroup2.myMinX,AgentGroup2.myMaxX,AgentGroup2.dicStartPos)
    #run the simulation
    sim.run()
    # Need to keep an update of the food carried
    dicFoodCarried={}
    for index in AgentGroup2.myIndexes:
      dicFoodCarried[index]=0
    for index in AgentGroup2.enemyIndexes:
      dicFoodCarried[index]=0
    print 'score: '+str(sim.getScore('attack',dicFoodCarried))
    print "index:"+str(self.index)+"  pos="+str(self.myPos)
    print sim.toString()

    #Choose a semi rando goal
    foodLeft = self.getFood(gameState).asList()
    self.aim = random.choice(self.closestFoods(foodLeft,9))



  def chooseAction(self, gameState):
      startTime=time.time()

      """    Update variables related to position    """
      self.successor = self.getSuccessor(gameState, 'Stop')
      self.myPos = self.successor.getAgentPosition(self.index)
      self.gameState=gameState
      AgentGroup2.dicPos[self.index]=self.myPos

      """    Update my foodArray to check if something was eaten    """
      if AgentGroup2.blue:
        AgentGroup2.myFoodBoolArray=gameState.getBlueFood()
      else:
        AgentGroup2.myFoodBoolArray = gameState.getBlueFood()

      #Example of a behavior tree
      """
      tree = Fallback([
        #if i died i need to find a new food target
        Sequence([self.iDied,self.findFoodTarget]).run,
        #if there is an enemy close i need to run away
        Sequence([self.enemyClose,self.runAway]).run,
        # if i have too much food i go home
        Sequence([self.iAteTooMuch,self.goHome]).run,
        # if not i grab food
        Sequence([self.iAte,self.findFoodTarget]).run
      ])
      #tree.run()
      #bestAction = self.findBestAction()
      #self.debugDraw(self.aim, [1, 0, 0], True)
      """

      print("index: "+str(self.index)+"  counter: "+str(self.counter)+"  aim"+str(self.aim))+ "   current pos:"+str(self.myPos)




      for eindex in AgentGroup2.enemyIndexes:
        AgentGroup2.partFilters[eindex].testForNone()


      """    Particles filter updates    """
      for eindex in AgentGroup2.enemyIndexes:
        AgentGroup2.partFilters[eindex].update(self.myPos,gameState.getAgentDistances()[eindex],self.index)


      print "done0"

      """    Check if some food has been eaten and update the particles filter if so    """
      foodLost=self.myFoodChanged(self.myFoodBoolArray,self.myOldFoodBoolArray)
      if foodLost!=None:
        for eindex in AgentGroup2.enemyIndexes:
          AgentGroup2.partFilters[eindex].knownPos(foodLost,AgentGroup2.partFilters.values())


      """    Check if the enemies are in sight    """
      for eindex in AgentGroup2.enemyIndexes:
        if(gameState.getAgentPosition(eindex)!=None):
          AgentGroup2.partFilters[eindex].knownThisPos(gameState.getAgentPosition(eindex))


      """    Draw the particles    """
      if False:
          for eindex in AgentGroup2.enemyIndexes:
            AgentGroup2.partFilters[eindex].draw()

      """    Save our old food array (to check if something hes been eaten    """
      AgentGroup2.myOldFoodBoolArray=AgentGroup2.myFoodBoolArray




      """      Update dicPos      """
      for eindex in AgentGroup2.enemyIndexes:
          AgentGroup2.dicPos[eindex]=AgentGroup2.partFilters.get(eindex).findBest()

      """      Draw dicPos      """
      if False:
          self.debugDraw(self.myPos, [1, 0, 0], True)
          for eindex in AgentGroup2.enemyIndexes:
              self.debugDraw(AgentGroup2.dicPos[eindex], [1, 0, 0], False)
          for index in AgentGroup2.myIndexes:
              self.debugDraw(AgentGroup2.dicPos[index], [1, 0, 0], False)








      #Elapsed time during decision making
      chosenAction = self.findBestActionWithTree(startTime)
      print time.time()-startTime

      return chosenAction




  '''
  Functions that return data
  '''

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
    print("index: " + str(self.index) + "  resetCounter")
    self.counter=0

  def iDied(self):
    print("index: "+str(self.index)+"  iDied")
    if self.myPos==self.startPos:
      self.counter=0
      return 'done'
    else:
      return 'failed'

  def iAte(self):
    print("index: " + str(self.index) + "  iAte")
    if self.myPos==self.aim and not self.danger:
      self.counter+=1;
      return 'done'
    else:
      return 'failure'

  def iAteTooMuch(self):
    print("index: " + str(self.index) + "  iAteTooMuch      counter:"+str(self.counter))
    if self.counter>=self.foodLimit:
      return 'done'
    else:
      return 'failed'

  def enemyClose(self):
    print("index: " + str(self.index) + "  enemyClose")
    min = 9999
    allenemies = [self.successor.getAgentState(i) for i in self.getOpponents(self.successor)]
    enemies = [a for a in allenemies if not a.isPacman and a.getPosition() != None]
    if len(enemies)==0:
      self.danger = False
      return 'failed'
    for enemy in enemies:
      if(enemy.getPosition()!=None):

        dist = self.getMazeDistance(self.myPos, enemy.getPosition())
        if dist < min:
          min=dist
    if min<self.securityDistance:
      self.danger=True
      return 'done'
    self.danger = False
    return 'failed'

  def runAway(self):
    print("index: " + str(self.index) + "  runAway")
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
      max=self.getMazeDistance(self.myPos, closest.getPosition())
      actions = self.gameState.getLegalActions(self.index)
      for act in actions:
        successor2 = self.getSuccessor(self.gameState, act)
        pos2 = successor2.getAgentPosition(self.index)
        if self.getMazeDistance(closest.getPosition(),pos2)>max:
          self.aim=pos2
      return 'done'
    return 'failed'

  def findFoodTarget(self):
    print("index: " + str(self.index) + "  findFoodTarget")
    foodLeft = self.getFood(self.gameState).asList()
    for index in self.indexes:
      if self.index!=index:
        if len(foodLeft)>0 and self.closestFood(foodLeft) == self.aims.get(index):
          foodLeft.remove(self.aims.get(index))

    self.aim = self.closestFood(foodLeft)

  def findBestAction(self):
    print("index: " + str(self.index) + "  findBestAction")
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
    print("index: " + str(self.index) + "  goHome")
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
      maxTreeDepth = 5
      treeDepth = 1
      currNode = root

      C = np.sqrt(2)

      while treeDepth < maxTreeDepth:
        treeDepth += 1
        if not currNode.children:
          return currNode

        maxScore = -9999
        maxNode = None
        for child in currNode.children:
          if child.score == None:
            return child
          else:
            ucb1Score = child.score + C*np.sqrt(np.log(currNode.numVisits)/child.numVisits)
            if ucb1Score > maxScore:
              maxNode = child
              maxScore = ucb1Score
        
        currNode = maxNode

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


  def simulateGame(self,simStart):
    turnCounter = 0
    turnLimit = 50
    currState = simStart.id
    prevAction = Directions.STOP
    while(turnCounter < turnLimit):
      actions = currState.getLegalActions(self.index)
      actions.remove('Stop')
      # print self.reverseDirection(prevAction)
      if prevAction!=Directions.STOP and len(actions) > 1:
        try:
          actions.remove(self.reverseDirection(prevAction))
        except ValueError:
          pass

      nextAction = random.choice(actions)
      turnCounter += 1
      currState = self.getSuccessor(currState, nextAction)
      prevAction = nextAction
      # print currState
      # raw_input()
      if currState.data._lose == True:
        return -999
      elif currState.data._win == True:
        return 999

    # print currState
    # raw_input()
    return self.simScore(simStart.id,currState,0) 

  def simScore(self,startState,currState,behaviorMode):
    
    newScore = currState.getScore()
    oldScore = startState.getScore()
    if newScore != oldScore:
      return (newScore - oldScore)*50
     
    newSoftScore = currState.data.agentStates[self.index].numCarrying*10
    oldSoftScore = startState.data.agentStates[self.index].numCarrying*10

    newSoftScore -= (20-currState.getRedFood().count())*10
    oldSoftScore -= (20-startState.getRedFood().count())*10
    if newSoftScore != oldSoftScore:
      return newSoftScore - oldSoftScore

    initPos = startState.getAgentPosition(self.index)
    currPos = currState.getAgentPosition(self.index)

    aggression = 0
    if not startState.data.agentStates[self.index].isPacman:
      aggression = np.abs(self.mid-self.myPos[0])*5

    return self.getMazeDistance(initPos, currPos) + aggression



  def backpropagateScore(self,value,simStart):
    simStart.score = value
    simStart.numVisits = 1
    simStart.value = value
    currNode = simStart
    while(currNode.parent != None):
      currNode = currNode.parent
      currNode.value += value
      currNode.numVisits += 1
      currNode.score = currNode.value/currNode.numVisits




  def monteCarloTreeSearch(self,startTime):
    self.stateDict = dict()
    currGameState = self.gameState
    maxSimulations = 200
    counter = 0
    root = mcTree(currGameState)
    self.stateDict[root.id] = root

    while(counter < maxSimulations):
      nodeForExpansion = self.selectNode(root)
      simStart = self.expandNode(nodeForExpansion)
      value = self.simulateGame(simStart)
      self.backpropagateScore(value,simStart)
      counter += 1
      if time.time()-startTime>0.49:
        break

  def findBestActionWithTree(self,startTime):
    self.monteCarloTreeSearch(startTime)
    actions = self.gameState.getLegalActions(self.index)
    bestValue = -9999
    bestAction = random.choice(actions)
    for action in actions:
      if action == 'Stop' or (action == self.reverseDirection(self.myAction) and len(actions)>2):
        continue
      successor = self.getSuccessor(self.gameState, action)
      value = self.stateDict[successor].score
      print(value)
      print("action = ",action)
      # raw_input()     
      if value > bestValue:
        bestValue = value
        bestAction = action
    self.myAction = bestAction
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



