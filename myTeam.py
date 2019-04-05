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

#################     python capture.py -r myTeam -b baselineTeam
# Team creation #     python capture.py -r baselineTeam -b myTeam
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
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

class DummyAgent(CaptureAgent):
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

  def __init__(self, index):
    CaptureAgent.__init__(self,index)
    self.aim=[1,3]
    self.counter=0
    self.startPos=self.aim
    self.myPos=[1,3]
    self.successor= None
    self.gameState= None
    self.danger=False
    self.aims[index]=self.aim
    self.indexes.append(index)

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

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.gameState = gameState
    self.successor = self.getSuccessor(gameState, 'Stop')
    self.myPos = self.successor.getAgentPosition(self.index)

    foodLeft = self.getFood(gameState).asList()
    self.aim = random.choice(self.closestFoods(foodLeft,9))

    self.startPos=self.myPos

    self.mid = self.distancer.dc.layout.width / 2
    if (self.startPos[0] < self.mid):
      self.mid -= 1



  def chooseAction(self, gameState):
    """
    self.debugDraw(self.aim, [1,0,0], True)
    """


    self.successor = self.getSuccessor(gameState, 'Stop')
    self.myPos = self.successor.getAgentPosition(self.index)
    self.gameState=gameState

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


    tree.run()

    '''
    fallback([
      #if i died i need to find a new food target
      sequence([self.iDied,self.findFoodTarget]),
      #if there is an enemy close i need to run away
      sequence([self.enemyClose,self.runAway]),
      # if i have too much food i go home
      sequence([self.iAteTooMuch,self.goHome]),
      # if not i grab food
      sequence([self.iAte,self.findFoodTarget])
    ]
    )
    '''

    print("index: "+str(self.index)+"  counter: "+str(self.counter)+"  aim"+str(self.aim))

    self.aims[self.index] = self.aim
    bestAction = self.findBestAction()
    self.debugDraw(self.aim, [1, 0, 0], True)
    return bestAction




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



