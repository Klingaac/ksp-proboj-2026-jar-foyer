#!/bin/env python
import sys
from typing import List
from data import World, Move, Person, World, Map, Shade, Tombstone, Point
from game import Game, PlayerInterface
from random import shuffle

# // C:/Users/vikis/AppData/Local/Programs/Python/Python38/python.exe



def scan_map(player, p: Point, blocked: set, world: World):
    
    people_positions = set()
    for person in world.alive_people:
        people_positions.add(person.position)
    
    explored = {}
    current = [p]
    
    closestHuman = None
    closestMyTombstone = None
    closestEnemyTombstone = None
    
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
                        player.log("found person")
                        
                        path = []
                        prev = neighbour
                        while explored[prev] != None:
                            prev = explored[prev]
                            path.append(prev)
                        
                        if len(path) >= 2:
                            closestHuman = path[len(path) - 2]
                            
                    if neighbour in player.myTombstones:
                        player.log("found my tombstone")
                        
                        path = []
                        prev = neighbour
                        while explored[prev] != None:
                            prev = explored[prev]
                            path.append(prev)
                        
                        if len(path) >= 2:
                            closestMyTombstone = path[len(path) - 2]
                    
        current = new_current  
        
    return closestHuman, closestMyTombstone, closestEnemyTombstone
            
def move_to(player, start: Point, finish: Point, blocked: set):
    
    world = player.world
    
    explored = {}
    current = [start]
    
    explored[start] = None
    
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
                    if neighbour == finish:
                        
                        player.log("found guy :)") 
                        
                        path = []
                        prev = neighbour
                        while explored[prev] != None:
                            prev = explored[prev]
                            path.append(prev)
                        
                        if len(path) >= 2:
                            return path[len(path) - 2]
                        else:
                            return
                    
        current = new_current  

class Player(PlayerInterface):
    
    @staticmethod
    def log(*args):
        print(*args, file=sys.stderr)

    def init(self, world: World) -> None:
        Player.log("init")
        pass

    def get_turn(self, world: World) -> List[Move]:
        
        self.world = world
        self.myShades: set[Shade] = set()
        self.myTombstones: set[Tombstone] = set()
        self.enemyTombstones: set[Tombstone] = set()
        
        moves = []
        blocked = set()
        
        # ziskam svoje shades
        for shade_id, shade in world.alive_shades.items():
            if shade.owner == world.my_id:
                self.myShades.add(shade)
                
        # ziskam moje tombstones
        for tombstone in world.alive_tombstones:
            if tombstone.owner == world.my_id:
                self.myTombstones.add(tombstone)
            else:
                self.enemyTombstones.add(tombstone)
                
        attach_treshold = 9 * len(self.myTombstones) 
        
        shadeToClosestMyTombstone = {}
        shadeToClosestEnemyTombstone = {}
        
        closestHumanToShade = {}
        alreadyMovesShades = set()
        
        for shade in self.myShades:
            closestHuman, closestMyTombstone, closestEnemyTombstone = scan_map(self, shade.position, blocked, world)
            
            if closestHuman != None:
                closestHumanToShade[shade] = closestHuman
            
            # priradim shade k ich najblizsim myTombstone
            if closestMyTombstone != None:
                if closestMyTombstone not in shadeToClosestMyTombstone:
                    shadeToClosestMyTombstone[closestMyTombstone] = set()
                
                shadeToClosestMyTombstone[closestMyTombstone].add(shade)
                
            # priradim shade k ich najblizsim enemyTombstone
            if closestEnemyTombstone != None:
                if closestEnemyTombstone not in shadeToClosestEnemyTombstone:
                    shadeToClosestEnemyTombstone[closestEnemyTombstone] = set()
                    
                shadeToClosestEnemyTombstone[closestEnemyTombstone].add(shade)
                
                    
                    
        group_attack_threshold = 7
        
        for tombstone, shades in enumerate(shadeToClosestEnemyTombstone):
            if len(shades) < group_attack_threshold:
                continue
            
            for shade in shades:
                newPosition = move_to(self, shade.position, tombstone.position, blocked)
                if newPosition != None:
                    moves.append(Move(shade.id, newPosition))
                    blocked.add(newPosition)
                    alreadyMovesShades.add(shade)
            
                
            
        for shade in self.myShades:
            if shade in alreadyMovesShades:
                continue
            
            if shade in closestHumanToShade:
                closestHuman = closestHumanToShade[shade]
                moves.append(Move(shade.id, closestHuman))
                blocked.add(closestHuman)
                if closestHuman == shade.position:
                    self.log("problem")
            else:
                blocked.add(shade.position)    
                
                
        
        # rozhodneme sa co ideme robit
        if len(self.myShades) >= attach_treshold:
            
            averageDist = 0
            for shade in self.myShades:
                dist2 = shade.position.dist2()
                
            
                
            # nech sa vsetci regroupnu na jedno miesto
            
        else:
            # farmi viac ludi
            # kazdy sa posunie alebo zje najblizsieho cloveka
                
            for shade in self.myShades:
                closestHuman, closestMyTombstone, closestEnemyTombstone = scan_map(self, shade.position, blocked, world)
                if closestHuman != None:
                    moves.append(Move(shade.id, closestHuman))
                    blocked.add(closestHuman)
                    if closestHuman == shade.position:
                        self.log("problem")
                else:
                    blocked.add(shade.position)
            
        
        
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