from ..mangahub.features.system import System, MC, FML, Antagonist, Entity, Skill

Entity.base_hp = 101

mc = MC('John', System('Primordial Something System'))

amc = Antagonist('Not John')

mc.attack(amc, Skill('Punch', 10))

print(mc)
print(amc)