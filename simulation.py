from game import *
from capture import SIGHT_RANGE

class Simulation:
    timeLimit=2

    def __init__(self, gameState):
        self.gameState=gameState
        dicRoles={0:'attack',2:'def'}
        self.simState=SimulatedState(gameState,False,dicRoles)

    def run(self):
        time=0
        while time<self.timeLimit:
            time+=1
            self.simState.step()

    def step(self):
        print self.gameState.getRedTeamIndices()
        print self.gameState.getBlueTeamIndices()


class SimulatedState:


    def __init__(self, gameState, blue, dicRoles):
        self.initialState=gameState
        self.dicRoles=dicRoles
        if blue:
            self.walls=gameState.getWalls()
            self.enemyFood=gameState.getRedFood()
            self.myFood=gameState.getBlueFood()
            self.enemyCapsules=gameState.getRedCapsules()
            self.myCapsules=gameState.getBlueCapsules()
            self.enemyIndexes=gameState.getRedTeamIndices()
            self.myIndexes=gameState.getBlueTeamIndices()
        else:
            self.walls=gameState.getWalls()
            self.myFood=gameState.getRedFood()
            self.enemyFood=gameState.getBlueFood()
            self.myCapsules=gameState.getRedCapsules()
            self.enemyCapsules=gameState.getBlueCapsules()
            self.myIndexes=gameState.getRedTeamIndices()
            self.enemyIndexes=gameState.getBlueTeamIndices()

    def step(self):
        for index in range(0,max(max(self.myIndexes),max(self.enemyIndexes))+1):
            if(index in self.myIndexes):
                self.predictMyAgent(index)
            else:
                self.predictEnemyAgent(index)

    def predictMyAgent(self,index):
        role=self.dicRoles.get(index)
        if role=='attack':
            print 'jattaque'
            None
        else:
            print 'non...'
            None

    def predictEnemyAgent(self,index):
        None

