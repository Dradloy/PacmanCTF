from game import *
import copy
from capture import SIGHT_RANGE

class Simulation:
    timeLimit=200

    def __init__(self, gameState,XLENGTH,YLENGTH,blue,dicPos,agentIndex,direction,redOnCapsule,blueOnCapsule,redTimer,blueTimer,myMinX,myMaxX,myStartPos,enemyStartPos):
        self.gameState=gameState
        dicRoles={0:'att',2:'df'}
        self.simState=SimulatedState(gameState,XLENGTH,YLENGTH,blue,dicRoles,dicPos,agentIndex,direction,redOnCapsule,blueOnCapsule,redTimer,blueTimer,myMinX,myMaxX,myStartPos,enemyStartPos)

    def run(self):
        time=0
        while time<self.timeLimit:
            time+=1
            self.simState.step()
        print "ran    eatdic"
        print self.simState.dicFoodCarried

    def step(self):
        print self.gameState.getRedTeamIndices()
        print self.gameState.getBlueTeamIndices()

    def toString(self):
        return str(self.simState.dicPos) + "   food eaten  me:"+str(self.simState.myEatingCounter)+";en;"+str(self.simState.enemyEatingCounter)+"    food carried"+str(self.simState.dicFoodCarried)

    def getScore(self,type,originalDicFoodCarried):
        return self.simState.getScore(type,originalDicFoodCarried)


class SimulatedState:
    POSSIBLE_MOVES=["North","South","West","East"]
    DEATH_SCORE=-10
    KILL_SCORE=20
    DISTANCE_TO_HOME_SCORE=1
    FOOD_BROUGHT_BACK_SCORE=4
    FOOD_PICKED_UP_SCORE=2
    ENEMY_FOOD_BROUGHT_BACK_SCORE=-4
    ENEMY_FOOD_PICKED_UP_SCORE=-2

    def __init__(self, gameState,XLENGTH,YLENGTH, blue, dicRoles, dicPos, agentIndex, direction, redOnCapsule,blueOnCapsule,redTimer,blueTimer,myMinX,myMaxX,myStartPos,enemyStartPos):
        self.XLENGTH=XLENGTH
        self.YLENGTH=YLENGTH
        self.initialState=gameState
        self.dicRoles=dicRoles
        self.dicPos=dicPos
        self.agentIndex=agentIndex
        self.direction=direction
        self.gameState=gameState
        self.myMinX=myMinX
        self.myMaxX=myMaxX
        self.myStartPos=myStartPos
        self.enemyStartPos=enemyStartPos
        self.myEatingCounter=0
        self.enemyEatingCounter=0
        self.myDeathCounter=0
        self.enemyDeathCounter=0
        if blue:
            self.walls=gameState.getWalls()
            self.enemyFood=gameState.getRedFood()
            self.myFood=gameState.getBlueFood()
            self.enemyCapsules=gameState.getRedCapsules()
            self.myCapsules=gameState.getBlueCapsules()
            self.enemyIndexes=gameState.getRedTeamIndices()
            self.myIndexes=gameState.getBlueTeamIndices()
            self.enemyOnCapsule=redOnCapsule
            self.meOnCapsule=blueOnCapsule
            self.enemyTimer=redTimer
            self.myTimer=blueTimer
        else:
            self.walls=gameState.getWalls()
            self.myFood=gameState.getRedFood()
            self.enemyFood=gameState.getBlueFood()
            self.myCapsules=gameState.getRedCapsules()
            self.enemyCapsules=gameState.getBlueCapsules()
            self.myIndexes=gameState.getRedTeamIndices()
            self.enemyIndexes=gameState.getBlueTeamIndices()
            self.enemyOnCapsule=blueOnCapsule
            self.meOnCapsule=redOnCapsule
            self.enemyTimer=blueTimer
            self.myTimer=redTimer
        self.dicFoodCarried = {0: 0}
        for index in self.myIndexes:
            self.dicFoodCarried[index]=0
        for index in self.enemyIndexes:
            self.dicFoodCarried[index]=0

    def stepOld(self):
        for index in range(0,max(max(self.myIndexes),max(self.enemyIndexes))+1):
            if(index==0):
                if self.myTimer==0 and self.meOnCapsule:
                    self.meOnCapsule=False
                elif self.myTimer>0:
                    self.myTimer-=1
                if self.enemyTimer==0 and self.enemyOnCapsule:
                    self.enemyOnCapsule=False
                elif self.enemyTimer>0:
                    self.enemyTimer-=1
            self.predictEnemyAgent(index)
            #updateFood
            self.updateFood(self.dicPos[index],index)
            # updatePills
            self.updatePills(self.dicPos[index],index)
            #updateEatenAgents
            self.updateEaten()


    def step(self):
        for index in range(0,max(max(self.myIndexes),max(self.enemyIndexes))+1):
            if (index == 0):
                if self.myTimer == 0 and self.meOnCapsule:
                    self.meOnCapsule = False
                elif self.myTimer > 0:
                    self.myTimer -= 1
                if self.enemyTimer == 0 and self.enemyOnCapsule:
                    self.enemyOnCapsule = False
                elif self.enemyTimer > 0:
                    self.enemyTimer -= 1
            if(index in self.myIndexes):
                if(index==self.agentIndex):
                    #Try to continue in the same direction
                    if self.moveIsPossible(self.dicPos[index],self.direction):
                        self.dicPos[index]=self.getMove(self.dicPos[index],self.direction)
                    # change direction
                    else:
                        listOfDirections=copy.deepcopy(SimulatedState.POSSIBLE_MOVES)
                        listOfDirections.remove(self.direction)
                        for i in range(0,len(SimulatedState.POSSIBLE_MOVES)-1):
                            dir=random.choice(listOfDirections)
                            if self.moveIsPossible(self.dicPos[index], dir):
                                self.direction=dir
                                self.dicPos[index] = self.getMove(self.dicPos[index], self.direction)
                                break
                            else:
                                listOfDirections.remove(dir)

                else:
                    self.predictMyAgent(index)
            else:
                self.predictEnemyAgent(index)
            #updateFood
            self.updateFood(self.dicPos[index],index)
            #update saved food
            self.updateSavedFood(self.dicPos[index],index)
            # updatePills
            self.updatePills(self.dicPos[index],index)
            #updateEatenAgents
            self.updateEaten()

    def predictMyAgent(self,index):
        role=self.dicRoles.get(index)
        if role=='attack':
            print 'jattaque'
            None
        elif role=='defense':
            print 'non...'
            None
        else:
            moves = self.getPossibleMoves(self.dicPos[index])
            self.dicPos[index] = random.choice(moves)

    def predictEnemyAgent(self,index):
        moves=self.getPossibleMoves(self.dicPos[index])
        self.dicPos[index] = random.choice(moves)


    def getPossibleMoves(self, part):
        possibleMoves = []
        if not self.gameState.hasWall(part[0] + 1, part[1]):
            possibleMoves.append((part[0] + 1, part[1]))
        if not self.gameState.hasWall(part[0] - 1, part[1]):
            possibleMoves.append((part[0] - 1, part[1]))
        if not self.gameState.hasWall(part[0], part[1] + 1):
            possibleMoves.append((part[0], part[1] + 1))
        if not self.gameState.hasWall(part[0], part[1] - 1):
            possibleMoves.append((part[0], part[1] - 1))
        possibleMoves.append((part[0], part[1]))
        return possibleMoves

    def moveIsPossible(self, part, move):
        if move == 'East':
            return not self.gameState.hasWall(part[0] + 1, part[1])
        if move == "West":
            return not self.gameState.hasWall(part[0] - 1, part[1])
        if move == "North":
            return not self.gameState.hasWall(part[0], part[1] + 1)
        if move == "South":
            return not self.gameState.hasWall(part[0], part[1] - 1)

    def getMove(self, part, move):
        if move == 'East':
            return (part[0] + 1, part[1])
        if move == "West":
            return (part[0] - 1, part[1])
        if move == "North":
            return (part[0], part[1] + 1)
        if move == "South":
            return (part[0], part[1] - 1)

    def updateFood(self,pos, index):
        if index in self.myIndexes and self.enemyFood[pos[0]][pos[1]]:
            self.dicFoodCarried[index]+=1
            self.enemyFood[pos[0]][pos[1]]=False
            #print "We have eaten "+str(pos)
        elif index in self.enemyIndexes and self.myFood[pos[0]][pos[1]]:
            self.dicFoodCarried[index]+=1
            self.myFood[pos[0]][pos[1]]=False
            #print "They have eaten "+str(pos)

    def updateSavedFood(self,pos,index):
        if index in self.myIndexes:
            if pos[0] >= self.myMinX and pos[0] <= self.myMaxX:
                self.myEatingCounter+=self.dicFoodCarried[index]
                self.dicFoodCarried[index]=0
        else:
            if not (self.dicPos.get(index)[0] >= self.myMinX and self.dicPos.get(index)[0] <= self.myMaxX):
                self.enemyEatingCounter+=self.dicFoodCarried[index]
                self.dicFoodCarried[index]=0


    def updateEaten(self):
        for index in self.myIndexes:
            for eindex in self.enemyIndexes:
                if self.dicPos.get(index) == self.dicPos.get(eindex):
                    #print "collision at:"+str(self.dicPos.get(index))+"  "+str(self.myMinX)+";"+str(self.myMaxX)+"   "+str(self.dicPos)
                    if self.dicPos.get(index)[0]>=self.myMinX and self.dicPos.get(index)[0]<=self.myMaxX :
                        if self.enemyOnCapsule:
                            self.kill(index)
                        else:
                            self.kill(eindex)
                    else:

                        if self.meOnCapsule:
                            self.kill(eindex)
                        else:
                            self.kill(index)


    def updatePills(self,pos,index):
        if index in self.myIndexes and pos in self.enemyCapsules:
            print "I ate capsule"
            self.enemyCapsules.remove(pos)
            self.meOnCapsule=True
            self.myTimer=40
        elif index in self.enemyIndexes and pos in self.myCapsules:
            print "They ate capsule"
            self.myCapsules.remove(pos)
            self.enemyOnCapsule=True
            self.enemyTimer=40

    def kill(self,index):
        if index in self.myIndexes:
            #print "I was killed  (capsule:"+str(self.enemyOnCapsule)+")"+"   pos: "+str(self.dicPos.get(index))
            #self.dropFood(index)
            self.dicPos[index]=self.myStartPos
            self.myDeathCounter+=1
        else:
            #print "They were killed  (capsule:"+str(self.meOnCapsule)+")"+"   pos: "+str(self.dicPos.get(index))
            #self.dropFood(index)
            self.dicPos[index] = self.enemyStartPos
            self.enemyDeathCounter+=1

    def dropFood(self,index):
        pos=self.dicPos.get(index)
        i=self.dicFoodCarried.get(index)
        squaresize=1
        if index in self.myIndexes:
            if i > 0:
                while i>0:
                    for x in range(-squaresize,squaresize+1):
                        if pos[0]+x>=0 and pos[0]+x<self.XLENGTH and pos[1]+squaresize<self.YLENGTH and not self.gameState.hasWall(pos[0]+x,pos[1]+squaresize) and not self.enemyFood[pos[0]+x][pos[1]+squaresize] and pos[0]+x>=self.myMinX and pos[0]+x<=self.myMaxX:
                            self.enemyFood[pos[0]+x][pos[1]+squaresize]=True
                            i-=1
                        if pos[0]+x>=0 and pos[0]+x<self.XLENGTH and pos[1]-squaresize>=0 and not self.gameState.hasWall(pos[0]+x,pos[1]-squaresize) and not self.enemyFood[pos[0]+x][pos[1]-squaresize] and pos[0]+x>=self.myMinX and pos[0]+x<=self.myMaxX:
                            self.enemyFood[pos[0]+x][pos[1]-squaresize]=True
                            i-=1

                    for y in range(-squaresize, squaresize + 1):
                        if pos[0]+squaresize<self.XLENGTH and pos[1]+y>=0 and pos[1]+y<self.YLENGTH and not self.gameState.hasWall(pos[0]+squaresize,pos[1]+y) and not self.enemyFood[pos[0]+squaresize][pos[1]+y] and pos[0]+x>=self.myMinX and pos[0]+x<=self.myMaxX:
                            self.enemyFood[pos[0]+squaresize][pos[1]+y]=True
                            i-=1
                        if pos[0]-squaresize<self.XLENGTH and pos[1]+y>=0 and pos[1]+y<self.YLENGTH and not self.gameState.hasWall(pos[0]-squaresize,pos[1]+y) and not self.enemyFood[pos[0]-squaresize][pos[1]+y] and pos[0]+x>=self.myMinX and pos[0]+x<=self.myMaxX:
                            self.enemyFood[pos[0]-squaresize][pos[1]+y]=True
                            i-=1
                        # if not food and not wall
                    squaresize+=1

        self.dicFoodCarried[index]=0

    def getScore(self,type,originalDicFoodCarried):
        if type=='attack':
            #add distance to closest food
            return self.myDeathCounter*SimulatedState.DEATH_SCORE + self.dicFoodCarried.get(self.agentIndex)*SimulatedState.FOOD_PICKED_UP_SCORE + self.myEatingCounter*self.FOOD_BROUGHT_BACK_SCORE
        elif type=='defense':
            foodpicked=0
            for index in self.enemyIndexes:
                foodpicked+=self.dicFoodCarried.get(index)-originalDicFoodCarried.get(index)
            return self.enemyDeathCounter*SimulatedState.KILL_SCORE+self.enemyEatingCounter*SimulatedState.ENEMY_FOOD_BROUGHT_BACK_SCORE+foodpicked*SimulatedState.ENEMY_FOOD_PICKED_UP_SCORE
        elif type=='gohome' or type=='home' or type=='go home' or type=='goHome':
            distToMid=min(abs(self.dicPos.get(self.agentIndex)[0]-self.myMaxX),abs(self.dicPos.get(self.agentIndex)[0]-self.myMaxX))
            return (self.myMaxX-self.myMinX-distToMid)*SimulatedState.DISTANCE_TO_HOME_SCORE + self.myDeathCounter*SimulatedState.DEATH_SCORE + (self.dicFoodCarried.get(self.agentIndex)-originalDicFoodCarried.get(self.agentIndex))*SimulatedState.FOOD_PICKED_UP_SCORE + self.myEatingCounter*self.FOOD_BROUGHT_BACK_SCORE*2
        else:
            return 0