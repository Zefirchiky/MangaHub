from system import Attack, Damage, Defense, Skill, System
from system.entities import FML, MC, NPC, Antagonist, Entity
from system.utils.enums import DamageTypes

Entity.base_hp = 200

punch_skill = Skill('Punch', Damage(10, type=DamageTypes.PERCENTAGE | DamageTypes.NORMAL)).add_damage(Damage(14, DamageTypes.PERCENTAGE))
mc = MC('John', System('Primordial Something System')).add_skill(punch_skill)

amc = Antagonist('Not John').add_defense(Defense(10)).add_defense(Defense(5, type=DamageTypes.PERCENTAGE))

mc.attack(amc, Attack(mc.skills['Punch'])).attack(amc, Attack(mc.skills['Punch']))
Attack(mc.skills['Punch'], attacker=mc, target=amc).attack()
Attack(mc.skills['Punch']).attack(mc, amc)

print(mc)
print(amc)