from __future__ import annotations

import json
import sys
from typing import Any, FrozenSet, Iterable, Iterator, List, Mapping, Optional, Protocol
from data import Point, Tombstone, Person, Shade, Move, World, Map

DELIM = "."

class PlayerInterface(Protocol):
    def init(self, world: World) -> None:
       ...

    def get_turn(self, world: World) -> List[Move]:
        ...

class Game:
    def __init__(self, player: PlayerInterface):
        self.player: PlayerInterface = player
        self.world: Optional[World] = None

    def run(self):
        chunks = read_chunks(sys.stdin)
        self.init_world(next(chunks))

        assert self.world is not None

        self.player.init(self.world)
        sys.stdout.write(DELIM + "\n")
        sys.stdout.flush()

        for turn_json in chunks:
            self.update_world(turn_json)
            print(f"STARTING TURN: {self.world.turn}", file=sys.stderr)
            send_moves(self.player.get_turn(self.world))
            print("", file=sys.stderr)
        return 0

    def init_world(self, init_json: str) -> None:
        data = json.loads(init_json) if init_json.strip() else {}
        self.world = World(int(data["my_id"]), _parse_map(data["map"]))
        self.world.alive_tombstones = {_parse_hill(h) for h in data.get("spawn_positions", [])}

    def update_world(self, turn_json: str) -> None:
        data = json.loads(turn_json) if turn_json.strip() else {}

        assert self.world is not None

        self.world.converted_count = int(data["food_count"])
        self.world.turn = int(data["turn_num"])

        alive_ants_obj: Mapping[str, Any] = data.get("alive_ants", {})
        self.world.alive_shades = {int(k): _parse_ant(v) for k, v in alive_ants_obj.items()}

        self.world.alive_tombstones = {_parse_hill(h) for h in data.get("alive_hills", [])}
        self.world.alive_people = {_parse_food(f) for f in data.get("alive_food", [])}


def read_chunks(stdin: Iterable[str]) -> Iterator[str]:
    lines: List[str] = []
    for raw in stdin:
        line = raw.rstrip("\n")
        if line == DELIM:
            yield "\n".join(lines)
            lines.clear()
            continue
        lines.append(line)

    if lines:
        raise RuntimeError("Unexpected EOF while reading chunk")


def _parse_point(obj: Mapping[str, Any]) -> Point:
    return Point(int(obj["x"]), int(obj["y"]))


def _parse_point_set(items: Iterable[Mapping[str, Any]]) -> FrozenSet[Point]:
    return frozenset(_parse_point(p) for p in items)


def _parse_hill(obj: Mapping[str, Any]) -> Tombstone:
    return Tombstone(position=_parse_point(obj["position"]), owner=int(obj["owner"]), id=int(obj["id"]))


def _parse_food(obj: Mapping[str, Any]) -> Person:
    return Person(position=_parse_point(obj["position"]), id=int(obj["id"]))


def _parse_ant(obj: Mapping[str, Any]) -> Shade:
    return Shade(
        position=_parse_point(obj["position"]),
        owner=int(obj["owner"]),
        id=int(obj["id"]),
    )

def _parse_map(obj: Mapping[str, Any]) -> Map:
    return Map(
        width = int(obj["width"]),
        height = int(obj["height"]),
        water_tiles = _parse_point_set(obj.get("water_tiles", [])),
        tombstone_positions = _parse_point_set(obj.get("tombstone_positions", [])),
    )


def serialize_moves(moves: List[Move]) -> str:
    payload = {
        "data": [
            {"id": int(m.id), "target": {"x": int(m.target.x), "y": int(m.target.y)}}
            for m in moves
        ]
    }
    return json.dumps(payload, separators=(",", ":"))


def send_moves(moves: List[Move]) -> None:
    sys.stdout.write(serialize_moves(moves) + "\n")
    sys.stdout.write(DELIM + "\n")
    sys.stdout.flush()
