"""
Simple example of playing Tick Tack Toe between two agents.
"""
import asyncio
import random
from cess import Simulation, Agent


class tttRandomAgnet(Agent):
    """ Agent to play TickTackToe by choosing  random location 
    for next move. Key needs:
    - to set-up and maintain own state, 
    - notify back to sim changes/update to make
    """

    def __init__(self, mark='X'):
        """create superobject, sets our own mark(X,O) """
        self._super(tttRandomAgnet, self).__init__(state={} )
        self.mark = mark
   
    def pickMove(self, board):
        """ Decides next place to put a mark.
        @board is  a tuple of  tuple, the current board state, 
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

        #return our pick
        return (x,y) 

class TickTackToeSim(Simulation): 
    """ Contains the simulation 'space/state', but not
    agent-state. requres @step function to 
    call agents and let agents do their decisions. """

    def __init__(self, agents): 
        """Crate our base object, arent, our board, and our list
        of win-cases """
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
        """ Run our next simulation-round 
        X and 0 both pick and mark, and win-state is checked
        @return None"""
        x = self.agents[0]
        o = self.agents[1]
        newMark = x.pickMove(self.board)
        if newMark is not None:
            self.boardUpdate(newMark, x.mark)
        else: #no new mark, must be no move, must be a tie
            #print("tie, no win")
            self.isDone = True 
        won = self.checkIfWon(x.mark)
        if not won: 
            newMark = o.pickMove(self.board)
            if newMark is not None:
                self.boardUpdate(newMark, o.mark)
            else: #no new mark, must be no move, must be a tie
                #print("tie, no win")
                self.isDone= True
            won = self.checkIfWon(o.mark)
            if won:
                self.isDone = True 
                #print("O Won")
        else:
            self.isDone = True
            #print("X Won")

        
    def checkIfWon(self, mark):
        """" Check if a win-state was reached, 
        @returns True if a win detected, False otherwise"""
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
        """ Update board state with the passed-in move
        @move is a tuple of (x,y) location. 
        @return True if updaetd, False if not updated."""
        if move is None:
            #return False to flag this
            return False 

        x,y = move
        self.board[int(y)][int(x)] =  mark
        return True

    def getBoard(self):
        """returns a multi-line string of the state of the board"""
        ret = []
        ret.append('----------')
        if self.board : 
            for i in range(0,len(self.board)):
                #import pdb; pdb.set_trace()
                c = [ str(x) for x in self.board[i] ]
                line  = '\t'.join(c)
                ret.append(line)
        ret.append('----------')
        return '\n'.join(ret)

def main():
    runOneRound_RandomAgents()

def runOneRound_RandomAgents():
    """ runs one round of tick tack toe using a random'choice agent """
    print("starting tick-tack-toe between random agent")
    agentA = tttRandomAgnet('X')
    agentB = tttRandomAgnet('O')
    ttSim = TickTackToeSim([agentA, agentB])
    ttSim.run(10)
    b = ttSim.getBoard()
    print(b)

    


if __name__ == '__main__':
    main()

