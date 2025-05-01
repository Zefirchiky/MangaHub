from .entity import Entity


class NPC(Entity):
    npc_number = 0

    def __init__(self, name: str = "NPC"):
        if name == "NPC":
            name = f"NPC_{NPC.npc_number}"
            NPC.npc_number += 1
        super().__init__(name)
