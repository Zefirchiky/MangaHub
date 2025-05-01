from ..utils.enums import CustomDamageType, DamageTypes
from .damage import Damage
from .defense import Defense


class Skill:
    DamageTypes = DamageTypes

    def __init__(
        self,
        name: str,
        damage: Damage = Damage(0),
        defense: Defense = Defense(0),
    ) -> None:
        # === Description ===
        self.name = name
        self.description = ""

        self.damage: list[Damage] = [damage]
        self.defense: list[Defense] = [defense]
        self.attributes = {}

    def add_attribute(self, name: str, value: int) -> "Skill":
        self._attributes[name] = value
        return self

    def add_damage(self, damage: Damage) -> "Skill":
        self.damage.append(damage)
        return self

    def add_defense(self, defense: Defense) -> "Skill":
        self.defense.append(defense)
        return self

    def attack(self, hp: int = 0) -> list[Damage]:
        return self.damage

    def defend(self, dmg: Damage):
        defense = 0
        for def_ in self.defense:
            defense += def_.defense

    @property
    def power(self) -> int:
        return sum(
            [dmg.damage for dmg in self.damage]
            + [def_.defense for def_ in self.defense]
        )
