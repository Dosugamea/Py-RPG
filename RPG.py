import json,random,atexit
from collections import OrderedDict
from Utility import Logger,Choicer
from Utility import Client,Message
from Quest import Quest
from Menu import Menu
from Battle import Battle
import pdb

class RPG(Logger,Choicer,Quest,Menu,Battle):
    cl = Client()

    def __init__(self):
        with open("ShopData.json",encoding="utf-8_sig") as f:
            self.shopdata = json.loads(f.read(), object_pairs_hook=OrderedDict)
        with open("ItemData.json",encoding="utf-8_sig") as f:
            self.itemdata = json.loads(f.read(), object_pairs_hook=OrderedDict)
        with open("QuestData.json",encoding="utf-8_sig") as f:
            self.questdata = json.loads(f.read(), object_pairs_hook=OrderedDict)
        with open("QuestMenuData.json",encoding="utf-8_sig") as f:
            self.menudata = json.loads(f.read(), object_pairs_hook=OrderedDict)
        with open("EnemyData.json",encoding="utf-8_sig") as f:
            self.enemy_dict = json.loads(f.read(), object_pairs_hook=OrderedDict)
        with open("SkillData.json",encoding="utf-8_sig") as f:
            self.skill_dict = json.loads(f.read(), object_pairs_hook=OrderedDict)
        with open("SaveData.json",encoding="utf-8_sig") as f:
            self.rpgdata = json.loads(f.read(), object_pairs_hook=OrderedDict)
        self.userdata = {
            "User":{
                "State":{
                    "RPG":{
                        "Game":True,
                        "Step":0
                    }
                }
            }
        }
        print("RPG Created")
    
    '''
    def process_rpg(self,msg):
        if self.rpgdata[msg._from]["Stats"]["Screen"] == "menu": self.process_menu(msg)
        elif self.rpgdata[msg._from]["Stats"]["Screen"] == "quest": self.process_quest(msg)
        elif self.rpgdata[msg._from]["Stats"]["Screen"] == "battle": self.process_battle(msg)
        elif self.rpgdata[msg._from]["Stats"]["Screen"] == "shop": self.process_shop(msg)
        else:
            print(self.rpgdata[msg._from]["Stats"]["Screen"])
            raise ValueError
    '''     
    #状態で分岐
    def process_rpg(self,msg):
        if msg._from in self.rpgdata:
            if self.rpgdata[msg._from]["Pause"] == False:
                if msg.text == "中断":
                    self.rpgdata[msg._from]["Pause"] = True
                    self.userdata[msg._from]["State"]["RPG"]["Game"] = False
                    self.cl.sendMessage("～Thank you for playing!～\nまた来てくださいね! (*^-^*)")
                else:
                    stat = self.rpgdata[msg._from]["Stats"]
                    if self.rpgdata[msg._from]["Stats"]["Screen"] == "menu": self.process_menu(msg)
                    elif self.rpgdata[msg._from]["Stats"]["Screen"] == "quest": self.process_quest(msg)
                    elif self.rpgdata[msg._from]["Stats"]["Screen"] == "battle": self.process_battle(msg)
                    elif self.rpgdata[msg._from]["Stats"]["Screen"] == "shop": self.process_shop(msg)
                    else:
                        print(self.rpgdata[msg._from]["Stats"]["Screen"])
                        raise ValueError
            else:
                self.rpgdata[msg._from]["Pause"] = False
                self.cl.sendMessage("RPGへようこそ🌎")
                self.process_rpg(msg)
        else:
            self.cl.sendMessage("RPGへようこそ🌎")
            self.process_gate(msg)

    def process_gate(self,msg):
        if self.userdata[msg._from]["State"]["RPG"]["Step"] == 0:
            self.cl.sendMessage('アカウントがないみたいです!\n新規登録しても大丈夫でしょうか？\n\n"はい"で登録\n"いいえ"でキャンセルします\n※登録した時点で利用規約に同意したとみなします\n利用規約は"利用規約"で確認できます')
            self.userdata[msg._from]["State"]["RPG"]["Step"] += 1
        else:
            if msg.text == "はい":
                self.userdata[msg._from]["State"]["RPG"]["Step"] = 2
                self.cl.sendMessage("ありがとうございます！\nユーザー情報を登録します...")
                self.register_rpg(msg)
                self.cl.sendMessage("登録しました！\nようこそ RPGへ!")
            elif msg.text == "いいえ":
                self.userdata[msg._from]["State"]["RPG"]["Step"] = 0
                self.userdata[msg._from]["State"]["RPG"]["Game"] = False
                self.cl.sendMessage("気が変わったらまた来てください > <")
            elif msg.text == "利用規約":
                with open("Terms.txt",encoding="utf-8_sig") as f:
                    self.cl.sendMessage(f.read())

def atend():
    print("Saving")
    #with open("SaveData.json","w",encoding='utf8') as f:
    #    json.dump(RPGer.rpgdata, f, ens1ure_ascii=False, indent=4,separators=(',', ': '))
    print("BYE")
atexit.register(atend)

if __name__ == '__main__': 
    RPGer = RPG()
    RPGer.process_rpg(Message())
    #RPGer.auto_choice([1,1,1,1,1,1,1,1,1])
    while True:
        inp = input(">>")
        RPGer.process_rpg(Message(text=inp))