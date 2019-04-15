from game import *
import copy
from capture import SIGHT_RANGE

class Simulation:
    timeLimit=20000

    def __init__(self, gameState,blue,dicPos,agentIndex,direction,redOnCapsule,blueOnCapsule,redTimer,blueTimer,myMinX,myMaxX,myStartPos,enemyStartPos):
        self.gameState=gameState
        dicRoles={0:'att',2:'df'}
        self.simState=SimulatedState(gameState,blue,dicRoles,dicPos,agentIndex,direction,redOnCapsule,blueOnCapsule,redTimer,blueTimer,myMinX,myMaxX,myStartPos,enemyStartPos)

    def run(self):
        time=0
        while time<self.timeLimit:
            time+=1
            self.simState.step()

    def step(self):
        print self.gameState.getRedTeamIndices()
        print self.gameState.getBlueTeamIndices()

    def toString(self):
        return str(self.simState.dicPos)


class SimulatedState:
    POSSIBLE_MOVES=["North","South","West","East"]

    def __init__(self, gameState, blue, dicRoles, dicPos, agentIndex, direction, redOnCapsule,blueOnCapsule,redTimer,blueTimer,myMinX,myMaxX,myStartPos,enemyStartPos):
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
            self.enemyFood[pos[0]][pos[1]]=False
            #print "We have eaten "+str(pos)
        elif index in self.enemyIndexes and self.myFood[pos[0]][pos[1]]:
            self.myFood[pos[0]][pos[1]]=False
            #print "They have eaten "+str(pos)

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
            self.dicPos[index]=self.myStartPos
        else:
            #print "They were killed  (capsule:"+str(self.meOnCapsule)+")"+"   pos: "+str(self.dicPos.get(index))
            self.dicPos[index] = self.enemyStartPos