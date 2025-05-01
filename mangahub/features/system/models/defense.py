from __future__ import annotations

from system.config import Config

from ..utils.enums import DamageTypes, DefenseTypes


class Defense:
    def __init__(self, defense: int = 0, type: DefenseTypes = DefenseTypes.NORMAL):
        self.defense = defense
        self.type = type

    def add_type(self, type: DefenseTypes) -> "Defense":
        self.type |= type
        return self

    def get_damage(
        self, damage: int, damage_type: DamageTypes = DamageTypes.NORMAL
    ) -> int:
        damage = damage
        if DamageTypes.NORMAL in damage_type:
            damage -= (
                self.defense
                if not self.type == DefenseTypes.PERCENTAGE
                else damage / 100 * self.defense
            )

        if DamageTypes.TRUE in damage_type:
            if self.type == DefenseTypes.TRUE and Config.true_defense_over_true_damage:
                damage -= self.defense
            if (
                self.type == DefenseTypes.PERCENTAGE
                and Config.percentage_defense_over_true_damage
            ):
                damage -= damage / 100 * self.defense

        if DamageTypes.PERCENTAGE in damage_type:
            if (
                self.type == DefenseTypes.TRUE
                and Config.true_defense_over_percentage_damage
            ):
                damage -= self.defense
            if (
                self.type == DefenseTypes.PERCENTAGE
                and Config.percentage_defense_over_percentage_damage
            ):
                damage -= damage / 100 * self.defense

        return damage

    def __add__(self, other: int | Defense | DefenseTypes) -> "Defense":
        if isinstance(other, int):
            self.defense += other
        elif isinstance(other, Defense):
            self.defense += other.defense
            self.type |= other.type
        elif isinstance(other, DefenseTypes):
            self.type |= other
        return self

    def __repr__(self) -> str:
        return f"{self.defense} ({self.type.name})"
