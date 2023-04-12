from Grid import Grid
from BaseAI import BaseAI
from Displayer import Displayer

import math
import time
import random

class IntelligentAgent(BaseAI):
    

    def maximize(self, grid, alpha, beta, depth, maxDepth, startTime):

        if(depth >= maxDepth or time.process_time() - startTime > 0.18):
            return (None, self.getHeuristic(grid))

        (maxMove, maxUtility) = (None, -math.inf)

        for move in Grid.getAvailableMoves(grid):
            m = move[0]
            child = move[1]

            minned = self.minimize(child, alpha, beta, depth+1, maxDepth, startTime)
            utility = minned[1]

            if utility > maxUtility:
                maxMove = m
                maxUtility = utility
        
            if maxUtility >= beta:
                break
            if maxUtility > alpha:
                alpha = maxUtility

        return (maxMove, maxUtility)


    def minimize(self, grid, alpha, beta, depth, maxDepth, startTime):
        if(depth >= maxDepth or time.process_time() - startTime > 0.18):
            return (None, self.getHeuristic(grid))
        
        (minChild, minUtility) = (None, math.inf)

        for cell in Grid.getAvailableCells(grid):
            utility = self.chance(grid, cell, alpha, beta, depth, maxDepth, startTime)
            if utility < minUtility:
                (minChild, minUtility) = (cell, utility)
            
            if minUtility <= alpha:
                break
            if minUtility < beta:
                beta = minUtility

        return (minChild, minUtility)

    def chance(self, grid, location, alpha, beta, depth, maxDepth, startTime):

        copy2 = Grid.clone(grid)
        Grid.setCellValue(copy2, location, 2)

        copy4 = Grid.clone(grid)
        Grid.setCellValue(copy4, location, 4)

        maxed = 0.9*self.maximize(copy2, alpha, beta, depth+1, maxDepth, startTime)[1] + 0.1*self.maximize(copy4, alpha, beta, depth+1, maxDepth, startTime)[1]
        
        return maxed


    def getMove(self, grid):
        
        startTime = time.process_time()
        maxDepth = 1
        bestMove = (grid.getAvailableMoves()[0][0], self.getHeuristic(grid.getAvailableMoves()[0][1]))
    
        
        while True:
            move = self.maximize(grid, -math.inf, math.inf, 0, maxDepth, startTime)
            
            if move[1] > bestMove[1]:
                bestMove = (move[0], move[1])

            if time.process_time() - startTime > 0.16:
                break
            maxDepth += 1
            
        
        return bestMove[0]

    #Weights reach 2048 ~60% of the time

    def getHeuristic(self, grid):
        return 8*self.openSquares(grid) + 4*self.edgeValues(grid) + 8*self.corners(grid) + 0.5*self.snake(grid) + 12*self.maxTile(grid)

    def edgeValues(self, grid):
        score = 0
        edges = [(3,0), (3,1), (3,2), (3,3)]
        weights = [8,4,2,1]
        for count in range(len(edges)):
            if(grid.getCellValue(edges[count]) > 0):
                score += weights[count]*math.log2(grid.getCellValue(edges[count]))
        
        return score

    def corners(self, grid):
        corners = [(3,0)]
        for pos in corners:
            if(grid.getCellValue(pos) == grid.getMaxTile()):
                return math.log2(grid.getCellValue(pos))
        return 0

    def monotonicity(self, grid):
        '''
         or \
        (self.increasingRight(grid) and self.increasingUp(grid))or \
        (self.increasingLeft(grid) and self.increasingDown(grid)) or \
        (self.increasingLeft(grid) and self.increasingUp(grid))
        '''

        if (self.increasingRight(grid) and self.increasingDown(grid)) or \
            (self.increasingLeft(grid) and self.increasingDown(grid)):
            return 10*math.log2(grid.getMaxTile())
        
        return 0

    def snake(self, grid):
        order1 = [(3,0), (3,1), (3,2), (3,3), (2,3), (2,2), (2,1), (2,0)]
        score = 0
        for count in range(1, len(order1)):
            if(grid.getCellValue(order1[count]) > 0 and grid.getCellValue(order1[count-1]) > 0):
                if grid.getCellValue(order1[count]) < grid.getCellValue(order1[count-1]):
                    if count == 4:
                        score += 2*math.log2(grid.getCellValue(order1[count-1]))
                        score -= 2*math.log2(grid.getCellValue(order1[count-1])/grid.getCellValue(order1[count]))
                    else:
                        score += math.log2(grid.getCellValue(order1[count-1]))
                        score -= math.log2(grid.getCellValue(order1[count-1])/grid.getCellValue(order1[count]))
                else:
                    break
        return score
  

    def increasingRight(self, grid):
            for row in range(4):
                previous = grid.getCellValue((row, 0))
                for col in range(1,4):
                    if grid.getCellValue((row, col)) < previous:
                        return False
            return True

    def increasingLeft(self, grid):
        for row in range(4):
            previous = grid.getCellValue((row, 3))
            for col in reversed(range(1,4)):
                if grid.getCellValue((row, col)) < previous:
                    return False
        return True

    def increasingDown(self, grid):
        for col in range(4):
            previous = grid.getCellValue((0, col))
            for row in range(1,4):
                if grid.getCellValue((row, col)) < previous:
                    return False
        return True  

    def increasingUp(self, grid):
        for col in range(4):
            previous = grid.getCellValue((3, col))
            for row in reversed(range(1,4)):
                if grid.getCellValue((row, col)) < previous:
                    return False
        return True

    def smoothness(self, grid):
        score = 0
        
        for row in range(4):
            for col in range(0,3):
                if grid.getCellValue((row,col)) > 0 and grid.getCellValue((row, col+1)) > 0:
                    '''if grid.getCellValue((row,c1)) - grid.getCellValue((row, c2)) == 0:
                        score+=10'''
                    if abs(grid.getCellValue((row,col)) - grid.getCellValue((row, col+1))) > 0:
                        score -= math.log2(abs(max(grid.getCellValue((row,col)), grid.getCellValue((row, col+1)))/min(grid.getCellValue((row,col)), grid.getCellValue((row, col+1)))))

        for col in range(4):
            for row in range(0,3):
                if grid.getCellValue((row,col)) > 0 and grid.getCellValue((row+1, col)) > 0:
                    if abs(grid.getCellValue((row,col)) - grid.getCellValue((row+1, col))) > 0:
                        score -= math.log2(abs(max(grid.getCellValue((row,col)), grid.getCellValue((row+1, col)))/min(grid.getCellValue((row,col)), grid.getCellValue((row+1, col)))))
        
        return score

    def openSquares(self, grid):
        return len(Grid.getAvailableCells(grid))
    
    def maxTile(self, grid):
        return math.log2(grid.getMaxTile())