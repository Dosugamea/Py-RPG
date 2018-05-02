from datetime import datetime
from datetime import timedelta

class Stamina(object):
    #足りていればTrue 足りていなければFalseを返す
    def use_stamina(self,user,stv):
        if self.rpgdata[user]["Stamina"] - stv >= 0:
            self.rpgdata[user]["Stamina"] -= stv
            return True
        else:
            return False
    
    #スタミナを時間経過で回復させる
    def update_stamina(self,user):
        data = self.rpgdata[user]
        n_time = datetime.now()
        sa_time = n_time - datetime.strptime(data["Stats"]["Stm_chk"], '%Y-%m-%d %H:%M:%S')
        heal_point = int(sa_time.total_seconds()/300)
        heal_max = self.leveldata[str(self.rpgdata[user]["Level"])]["Stamina"]
        if data["Stamina"] + heal_point > heal_max:
            data["Stamina"] = heal_max
        else:
            data["Stamina"] += heal_point
        data["Stats"]["Stm_chk"] = n_time.strftime('%Y-%m-%d %H:%M:%S')
        return True
        
        
if __name__ == '__main__':
    import json
    from collections import OrderedDict
    RPGer = Stamina()
    with open("SaveData.json",encoding="utf-8_sig") as f:
        RPGer.rpgdata = json.loads(f.read(), object_pairs_hook=OrderedDict)
    with open("LevelData.json",encoding="utf-8_sig") as f:
        RPGer.leveldata = json.loads(f.read(), object_pairs_hook=OrderedDict)
    print(RPGer.use_stamina("User",10))
    print(RPGer.update_stamina("User"))