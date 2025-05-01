from pydantic import BaseModel


class Config(BaseModel):
    true_defense_over_true_damage: bool = (
        False  # If true defense should block true damage
    )
    true_defense_over_percentage_damage: bool = (
        False  # If true defense should block percentage damage
    )
    percentage_defense_over_true_damage: bool = (
        False  # If percentage defense should block true damage
    )
    percentage_defense_over_percentage_damage: bool = (
        False  # If percentage defense should block percentage damage
    )
