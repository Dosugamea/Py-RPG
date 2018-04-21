from collections import OrderedDict
from copy import deepcopy
import json,random

class Gacha(object):
    def __init__(self):
        with open("GachaData.json",encoding="utf-8_sig") as f:
            self.gachadata = json.loads(f.read(), object_pairs_hook=OrderedDict)

    def roll_gacha(self,gname,force3=False,force4=False,force5=False):
        if force3: return [random.choice(self.gachadata[gname]["Drop"]["3"]),3]
        elif force4: return [random.choice(self.gachadata[gname]["Drop"]["4"]),4]
        elif force5: return [random.choice(self.gachadata[gname]["Drop"]["5"]),5]
        num = random.randint(1,100)
        if num <= 2: return [random.choice(self.gachadata[gname]["Drop"]["5"]),5]
        elif num <= 16: return [random.choice(self.gachadata[gname]["Drop"]["4"]),4]
        else: return [random.choice(self.gachadata[gname]["Drop"]["3"]),3]
            
    def process_10g(self,gname):
        grs = [self.roll_gacha(gname) for i in range(10)]
        rs = [g[1] for g in grs]
        if 5 not in rs and 4 not in rs: grs[9] = self.roll_gacha(gname,force4=True)
        return grs
    
    def first_10g(self,gname,msg):
        #self.rpgdata[msg._from]["Stone"] -= 300
        grs = self.process_10g(gname)
        for g in grs:
            if g[1] == 5: print("☆5")
            elif g[1] == 4: print("☆4")
            elif g[1] == 3: print("☆3")
    def normal_10g(self,gname,msg):
        #self.rpgdata[msg._from]["Stone"] -= 400
        grs = self.process_10g(gname)
        for g in grs:
            if g[1] == 5: print("☆5")
            elif g[1] == 4: print("☆4")
            elif g[1] == 3: print("☆3")
    def oha_1g(self,gname,msg):
        #self.rpgdata[msg._from]["Stone"] -= 10
        print(self.roll_gacha(gname,msg))
    def normal_1g(self,gname,msg):
        #self.rpgdata[msg._from]["Stone"] -= 10
        print(self.roll_gacha(gname,msg))
    
    
gcgc = Gacha()
gcgc.first_10g("ガチャ名","")
