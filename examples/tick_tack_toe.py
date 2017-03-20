"""
Simple example of playing Tick Tack Toe between two agents.

"""
import asyncio
import random
from cess import Simulation, Agent


class TickTackToeAgent(Agent):
    """ Agent to play TickTackToe. Key needs:
        - to set-up and maintain own state, 
        - notify back to sim changes/update to make
        - etc
    """

    def __init__(self, mark='X'):
        self._super(TickTackToeAgent, self).__init__(state={} )
        self.mark = mark
   
    def pickMove(self, board):
        """ board is  a tuple of  tuple, current board state, 
        states are 'X','O',None
        @returns x,y tuple for where to mark our spot, 
        None if no spots left"""
        #remove points used 
        b = [i for i in range(0,9) ]
        for  x in range( 0,len(board) ):
            for y in range( 0,len(board[x]) ):
                if board[x][y] is not None:
                    b.remove((x*3) + y) 
        if len(b) < 1: 
            return None

        #random pick an open place
        pick = random.choice(b) 
        x = pick % 3   
        y = (pick - x)/3
        return (x,y) 

class TickTackToeSim(Simulation): 
    """ Contains the simulation 'space/state', but not
    agent-state. requres @step function to 
    call agents and let agents do their decisions. """

    def __init__(self, agents): 
        super().__init__(agents)
        self.board = [ 
                [None, None, None], 
                [None, None, None],
                [None, None, None] ]

        k = []
        for i in range(0,3): 
            k.append( [(i,n) for n in range(0,3)] )
            k.append( [(n,i) for n in range(0,3)] ) 
        k.append( ( (0,0),(1,1),(2,2) ) )
        k.append( ( (2,2),(1,1),(0,0) ) ) 
        self.winConditions = k

    @asyncio.coroutine
    def step (self):
        x = self.agents[0]
        o = self.agents[1]
        newMark = x.pickMove(self.board)
        if newMark is None:
            print("tie, no win")
            self.isDone = True 
        self.boardUpdate(newMark, x.mark)
        won = self.checkIfWon(x.mark)
        if not won: 
            newMark = o.pickMove(self.board)
            if newMark is None:
                print("tie, no win")
                self.isDone= True
            self.boardUpdate(newMark, o.mark)
            won = self.checkIfWon(o.mark)
            if won:
                self.isDone = True 
                print("O Won")
        else:
            self.isDone = True
            print("X Won")
        print( self.board  )
        print( '----' )

        
    def checkIfWon(self, mark):
        """" if someone has one, returns the mark of the winner."""
        #there are more elegant ways of this, but it works
        k = []
        for i in range(0,3): 
            k.append( [(i,n) for n in range(0,3)] )
            k.append( [(n,i) for n in range(0,3)] ) 
        k.append( ( (0,0),(1,1),(2,2) ) )
        k.append( ( (2,2),(1,1),(0,0) ) ) 

        #check/scan for win conditions
        for win_cond in self.winConditions:
            row = 0 
            for pt in win_cond:
                x,y = pt
                if self.board[x][y] == mark:
                    row = row+1
            if row == 3:
                #import pdb; pdb.set_trace() 
                return True
        return False

    def boardUpdate(self, move, mark): 
        """ Update board state. w new move
        @move is a tuple of (x,y) location"""
        if move is None:
            print("No possible Move. Tie")
            return None

        x,y = move
        self.board[int(y)][int(x)] =  mark

def main():
    print("starting tick-tack-toe demo")
    agentA = TickTackToeAgent('X')
    agentB = TickTackToeAgent('O')

    #import pdb; pdb.set_trace() 
    ttSim = TickTackToeSim([agentA, agentB])
    ttSim.run(10)
    


if __name__ == '__main__':
    main()

