from collections import OrderedDict
from copy import deepcopy
import json,random

class Gacha(object):
    def __init__(self):
        with open("GachaData.json",encoding="utf-8_sig") as f:
            self.gachadata = json.loads(f.read(), object_pairs_hook=OrderedDict)
        self.rality = {
            5:2,
            4:12,
            3:86
        }

    def roll_gacha(self,name,msg,force4=False):
        if force4: random.choice(self.gachadata[name]["Drop"]["4"])
        num = random.randint(1,100)
        if num <= 2:
            return random.choice(self.gachadata[name]["Drop"]["5"])
        elif num <= 16:
            return random.choice(self.gachadata[name]["Drop"]["4"])
        else:
            return random.choice(self.gachadata[name]["Drop"]["3"])
            
    def first_10g(self,name,msg):
        #self.rpgdata[msg._from]["Stone"] -= 300
        for i in range(10):
            print(self.roll_gacha(name,msg))
    def normal_10g(self,msg):
        #self.rpgdata[msg._from]["Stone"] -= 400
        for i in range(10):
            print(self.roll_gacha(name,msg))
    def oha_1g(self,msg):
        #self.rpgdata[msg._from]["Stone"] -= 10
        print(self.roll_gacha(name,msg))
    def normal_1g(self,msg):
        #self.rpgdata[msg._from]["Stone"] -= 10
        print(self.roll_gacha(name,msg))
    
    
gcgc = Gacha()
