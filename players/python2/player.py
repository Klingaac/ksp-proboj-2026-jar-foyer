#!/bin/env python
import sys
from typing import List
from data import World, Move, Person, World, Map, Shade, Tombstone, Point
from game import Game, PlayerInterface
from random import shuffle

# // C:/Users/vikis/AppData/Local/Programs/Python/Python38/python.exe

def get_closest_human(player, p: Point, blocked: set, world: World):
    
    people_positions = set()
    for person in world.alive_people:
        people_positions.add(person.position)
    
    explored = {}
    current = [p]
    
    explored[p] = None
    
    while len(current) > 0:
        
        new_current = []
        for cur in current:
            
            neighbours = cur.get_neighbouring()
        
            for neighbour in neighbours:
                
                if neighbour in explored:
                    continue
                
                if neighbour in blocked:
                    continue
                
                if world.map.can_move_to(neighbour):
                    
                    new_current.append(neighbour)
                    explored[neighbour] = cur
                    
                    # nasli sme cloveka
                    if neighbour in people_positions:
                        
                        player.log("found guy :)") 
                        
                        path = []
                        prev = neighbour
                        while explored[prev] != None:
                            prev = explored[prev]
                            path.append(prev)
                        
                        return path
                    
                    
                    
        current = new_current  
            
    

class Player(PlayerInterface):
    
    @staticmethod
    def log(*args):
        print(*args, file=sys.stderr)

    def init(self, world: World) -> None:
        Player.log("init")
        pass

    def get_turn(self, world: World) -> List[Move]:
        
        moves = []
        blocked = set()
        
        for shade_id, shade in world.alive_shades.items():
            if shade.owner != world.my_id:
                continue
                
            pathToHuman = get_closest_human(self, shade.position, blocked, world)
            if pathToHuman != None:
                nextStep = pathToHuman[len(pathToHuman) - 2]
                moves.append(Move(shade_id, nextStep))
                blocked.add(nextStep)
                if nextStep == shade.position:
                    self.log("problem")
            
        
        
        # for shade_id, shade in world.alive_shades.items():
        #     neighbours = shade.position.get_neighbouring()
        #     shuffle(neighbours)
        #     for ngb in neighbours:
        #         if world.map.can_move_to(ngb):
        #             moves.append(Move(shade_id, ngb))
        #             break
        return moves

if __name__ == "__main__":
    game = Game(Player())
    game.run()