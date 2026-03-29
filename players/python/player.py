#!/bin/env python
import sys
from typing import List
from data import World, Move, Person, World, Map, Shade, Tombstone, Point
from game import Game, PlayerInterface
from random import shuffle

# // C:/Users/vikis/AppData/Local/Programs/Python/Python38/python.exe

def scan_map(player, p: Point, blocked: set, world: World):   
    
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
                    if closestHuman == None and neighbour in player.peoplePositions:
                        player.log("found person")
                        
                        prev = neighbour
                        while explored[prev] != p:
                            prev = explored[prev]
                        
                        closestHuman = prev
                            
                    if closestMyTombstone == None and neighbour in player.myTombstones:
                        player.log("found my tombstone")
                        
                        prev = neighbour
                        while explored[prev] != p:
                            prev = explored[prev]
                        
                        closestMyTombstone = prev
                            
                    if closestEnemyTombstone == None and neighbour in player.enemyTombstones:
                        player.log("found enemy tombstone")
                        
                        prev = neighbour
                        while explored[prev] != p:
                            prev = explored[prev]
                        
                        closestEnemyTombstone = prev
                    
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
                        
                        prev = neighbour
                        while explored[prev] != start:
                            prev = explored[prev]
                        
                        return prev
                    
        current = new_current  

def scared(player, p: Point) -> bool:
    
    shade_positions = player.shadePositions
    
    finalFear = 0
    finalHappiness = 999
    
    for x in (-1, 1):
        for y in (-1, 1):
            
            pos = Point(x + p.x, y + p.y)
            
            fear = 0
            for pos in pos.get_visible():
                if pos in shade_positions:
                    if shade_positions[pos].owner != player.owner:
                        fear += 1
                    else:
                        happiness += 1
                    
            finalFear = max(fear, finalFear)
            finalHappiness = min(happiness, finalHappiness)
            
    if finalHappiness >= finalFear:
        return False
    else:
        return True
        
    

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
        self.peoplePositions: set[Point] = set()
        self.shadePosition: dict[Point, Shade] = {}
        
        for shade in world.alive_shades:
            self.shadePosition[shade.position] = shade
        
        for person in world.alive_people:
            self.peoplePositions.add(person.position)
        
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
                
        
        shadeToClosestMyTombstone = {}
        shadeToClosestEnemyTombstone = {}
        
        closestHumanToShade = {}
        alreadyMovedShades = set()
        
        for shade in self.myShades:
            closestHuman, closestMyTombstone, closestEnemyTombstone = scan_map(self, shade.position, blocked, world)
            
            if closestHuman != None and not scared(self, closestHuman):
                closestHumanToShade[shade] = closestHuman
            
            # # priradim shade k ich najblizsim myTombstone
            # if closestMyTombstone != None:
            #     if closestMyTombstone not in shadeToClosestMyTombstone:
            #         shadeToClosestMyTombstone[closestMyTombstone] = set()
                
            #     shadeToClosestMyTombstone[closestMyTombstone].add(shade)
                
            # # priradim shade k ich najblizsim enemyTombstone
            # if closestEnemyTombstone != None:
            #     if closestEnemyTombstone not in shadeToClosestEnemyTombstone:
            #         shadeToClosestEnemyTombstone[closestEnemyTombstone] = set()
                    
            #     shadeToClosestEnemyTombstone[closestEnemyTombstone].add(shade)
                
                    
                    
        group_attack_threshold = 7
        
        for tombstone, shades in shadeToClosestEnemyTombstone.items():
            if len(shades) < group_attack_threshold:
                continue
            
            for shade in shades:
                newPosition = move_to(self, shade.position, tombstone.position, blocked)
                if newPosition != None:
                    moves.append(Move(shade.id, newPosition))
                    blocked.add(newPosition)
                    alreadyMovedShades.add(shade)
            
                
            
        for shade in self.myShades:
            if shade in alreadyMovedShades:
                continue
            
            if shade in closestHumanToShade:
                closestHuman = closestHumanToShade[shade]
                moves.append(Move(shade.id, closestHuman))
                blocked.add(closestHuman)  
    
        return moves

if __name__ == "__main__":
    game = Game(Player())
    game.run()