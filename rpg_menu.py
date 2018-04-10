import json,random
from collections import OrderedDict
from datetime import datetime

class Message(object):
    def __init__(self,_from="User",to="User",toType=0,text=""):
        self._from = _from
        self.to = to
        self.toType = 0
        self.text = text
class Client(object):
    def __init__(self):
        self.reqId = 0
    def sendMessage(self,text):
        print("Req<%s>\n\n%s"%(self.reqId,text))
        self.reqId += 1
class Logger(object):
    def add_log(self,text,msg):
        self.rpgdata[msg._from]["Stats"]["Log"].append(text)
    def send_log(self,msg):
        text = self.combine(self.rpgdata[msg._from]["Stats"]["Log"])
        self.cl.sendMessage(text)
        self.rpgdata[msg._from]["Stats"]["Log"] = []
class Choicer(object):
    choice_dict = {
        1:"あ",2:"い",3:"う",4:"え",5:"お",
        6:"か",7:"き",8:"く",9:"け",10:"こ"
    }
    def choicer(self,text="あ",ls=["A","B","C"]):
        if text in ls: return text
        try:
            inp = int(text)
            if inp in self.choice_dict:
                return ls[inp-1]
        except:
            if text in self.choice_dict.values():
                for c in self.choice_dict:
                    if self.choice_dict[c] == text:
                        return ls[c-1]
    def choice_text(self,ls,kana=False):
        if kana: return [ " %s : %s"%(self.choice_dict[i+1],l) for i,l in enumerate(ls)]
        else: return [ " %s : %s"%(i+1,l) for i,l in enumerate(ls)]
    def combine(self,ls):
        text = ""
        for l in ls:
            text += l+"\n"
        text = text[:len(text)-1]
        return text
        
class RPG(Logger,Choicer):
    cl = Client()
    rpgdata = {
        "User":{
            "Stone": 100,
            "Money": 100,
            "Inventory":{},
            "Items":{},
            "Stats":{
                "Log":[],
                "Screen":"menu",
                "Menu":{
                    "MenuID":0,
                    "Quest_MID":0,
                    "Setting_ID":0,
                    "Selecting":False
                },
                "Quest":{},
                "Shop":{
                    "ShopID":0,
                    "StepID":0,
                    "Selecting":False,
                    "Current_Shop":{},
                    "ShopName":{
                        "Bought":{
                            "0":0,
                            "1":0
                        },
                        "Sold":{
                            "0":0,
                            "1":0
                        }
                    }
                }
            }
        }
    }
    
    with open("ShopData.json",encoding="utf-8_sig") as f:
        shopdata = json.loads(f.read(), object_pairs_hook=OrderedDict)
        
    with open("ItemData.json",encoding="utf-8_sig") as f:
        itemdata = json.loads(f.read(), object_pairs_hook=OrderedDict)
    
    quest_sel_dict = {
        0:["Main","Sub","Event","Modoru"],
        1:["Story_1","Story_2","Story_3","Modoru"],
        2:["Quest1","Quest2","Quest3","Modoru"],
        3:["Quest1","Quest2","Quest3","Modoru"]
    }
    
    yobi = ["月","火","水","木","金","土","日"]
    
    def process_rpg(self,msg):
        if self.rpgdata[msg._from]["Stats"]["Screen"] == "menu": self.process_menu(msg)
        elif self.rpgdata[msg._from]["Stats"]["Screen"] == "quest": self.process_quest(msg)
        elif self.rpgdata[msg._from]["Stats"]["Screen"] == "work": self.process_work(msg)
        elif self.rpgdata[msg._from]["Stats"]["Screen"] == "shop": self.process_shop(msg)
    
    def process_quest(self,msg):
        print("Called Quest")
        print(self.rpgdata[msg._from]["Stats"])
        
    def process_work(self,msg):
        print("Called Work")
        print(self.rpgdata[msg._from]["Stats"])
        
    def process_shop(self,msg):
        #deepcopyではないため直接呼ばれるが問題はないと思われる？
        stat = self.rpgdata[msg._from]["Stats"]["Shop"]
        #表示部
        if stat["Selecting"] == False:
            #ショップ未選択_選択直後
            if stat["StepID"] == 0:
                if stat["ShopID"] == 0:
                    self.add_log("[Shop]\nWhere to go?",msg)
                    choices = list(stat["List"].keys())
                    choices.append("戻る")
                    self.add_log(self.combine(self.choice_text(choices)),msg)
                elif stat["ShopID"] in stat["List"].keys():
                    stat["Current_Shop"] = stat["List"][stat["ShopID"]]
                    self.add_log("[ %s ]"%(stat["ShopID"]),msg)
                    if "Welcome" in stat["Current_Shop"]["Messages"] and "Clerk" in stat["Current_Shop"]["Messages"]:
                        self.add_log("<%s> : %s"%(stat["Current_Shop"]["Messages"]["Clerk"],stat["Current_Shop"]["Messages"]["Welcome"]),msg)
                    self.add_log("",msg)
                    actions = []
                    if "Talk" in stat["Current_Shop"]: actions.append("会話")
                    #TODO: 互いのインポート処理をここに書こう
                    if "Buy" in stat["Current_Shop"] and "Deny" not in stat["Current_Shop"]["Buy"]: actions.append("買う")
                    if "Sell" in stat["Current_Shop"] and "Deny" not in stat["Current_Shop"]["Sell"]: actions.append("売る")
                    if len(actions) == 0: raise ValueError
                    actions.append("戻る")
                    stat["Current_Shop"]["Actions"] = actions
                    self.add_log(self.combine(self.choice_text(actions)),msg)
            #会話
            elif stat["StepID"] == 1:
                msi = str(random.choice(list(stat["Current_Shop"]["Talk"].keys())))
                if "Clerk" in stat["Current_Shop"]["Messages"]:
                    self.add_log("<%s> : %s"%(stat["Current_Shop"]["Messages"]["Clerk"],stat["Current_Shop"]["Talk"][msi]),msg)
                else:
                    self.add_log(stat["Current_Shop"]["Talk"][msi],msg)
                self.add_log("",msg)
                self.add_log(self.combine(self.choice_text(stat["Current_Shop"]["Actions"])),msg)
                stat["StepID"] = 0
            #"プレイヤーが"買う           
            elif stat["StepID"] == 2:
                self.add_log("< 商品リスト >",msg)
                if "Import_Buy" in stat["Current_Shop"]["Sell"]:
                    items = stat["Current_Shop"]["Buy"]["Items"]
                else:
                    items = stat["Current_Shop"]["Sell"]["Items"]
                for item in items:
                    im = self.itemdata[str(item["ID"])]
                    self.add_log("[%s] %s個 %sコイン"%(im["Name"],item["Cnt"],item["Price"]),msg)
            #"プレイヤーが"売る
            elif stat["StepID"] == 3:
                self.add_log("< 買取リスト >",msg)
                if "Import_Sell" in stat["Current_Shop"]["Buy"]:
                    items = stat["Current_Shop"]["Sell"]["Items"]
                else:
                    items = stat["Current_Shop"]["Item"]["Items"]
                for item in items:
                    im = self.itemdata[str(item["ID"])]
                    self.add_log("[%s] %s個 %sコイン"%(im["Name"],item["Cnt"],item["Price"]),msg)
            self.send_log(msg)
            stat["Selecting"] = True
        #入力受付部
        else:
            #ショップ未選択
            if stat["ShopID"] == 0:
                choices = list(stat["List"].keys())
                choices.append("戻る")
                choice = self.choicer(msg.text,choices)
                if choice != None:
                    stat["Selecting"] = False
                    if choice == "戻る":
                        self.rpgdata[msg._from]["Stats"]["Menu"]["MenuID"] = 0
                        self.rpgdata[msg._from]["Stats"]["Screen"] = "menu"
                        self.process_menu(msg)
                    else:
                        stat["ShopID"] = choice
                        self.process_shop(msg)
            else:
                #ショップ内動作選択
                if stat["StepID"] == 0:
                    choice = self.choicer(msg.text,stat["Current_Shop"]["Actions"])
                    if choice != None:
                        stat["Selecting"] = False
                        if choice == "戻る": stat["ShopID"] = 0
                        elif choice == "会話": stat["StepID"] = 1
                        elif choice == "買う": stat["StepID"] = 2
                        elif choice == "売る": stat["StepID"] = 3
                        self.process_shop(msg)
                #ショップ内購入選択処理
                elif stat["StepID"] == 2:
                    pass
                #ショップ内販売選択処理
                elif stat["StepID"] == 3:
                    pass
                    
                    
    
    #曜日指定、期間指定でショップを作る
    def gen_global_shop(self):
        shops = self.shopdata
        cdate = datetime.now()
        #ショップ一覧の作成
        ret_ls = {}
        #日付が有効なリスト
        for s in shops:
            if "Limit" not in shops[s]:
                ret_ls[s] = shops[s]
            elif "Day" in shops[s]["Limit"]:
                if shops[s]["Limit"]["Day"][cdate.weekday()] == 1:
                    ret_ls[s] = shops[s]
            elif "Date" in shops[s]["Limit"]:
                _from = datetime.strptime(shops[s]["Limit"]["Date"][0],'%Y-%m-%d %H:%M:%S')
                to = datetime.strptime(shops[s]["Limit"]["Date"][1],'%Y-%m-%d %H:%M:%S')
                if cdate > _from and cdate < to:
                    ret_ls[s] = shops[s]
            else:
                ret_ls[s] = shops[s]
        self.available_shops = ret_ls
    
    #個数制限_グローバル個数制限 Deny 等に基づき 個々のユーザー用のショップリストを作る
    def gen_private_shop(self,msg):
        shops = self.available_shops
        return shops
            
        
    def process_menu(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Menu"]
        if stat["Selecting"] == False:
            #表示するだけー
            if stat["MenuID"] == 0:
                self.add_log("[Home]\nWhere to go?",msg)
                self.add_log(self.combine(self.choice_text(["Quest","Work","Shop","Setting"])),msg)
            elif stat["MenuID"] == 1:
                if stat["Quest_MID"] == 0:
                    self.add_log("[Quest]\nWhich Quest to go?",msg)
                elif stat["Quest_MID"] == 1:
                    self.add_log("[MainQuest]\nWhich Quest to go?",msg)
                elif stat["Quest_MID"] == 2:
                    self.add_log("[SubQuest]\nWhich Quest to go?",msg)
                elif stat["Quest_MID"] == 3:
                    self.add_log("[EventQuest]\nWhich Quest to go?",msg)
                self.add_log(self.combine(self.choice_text(self.quest_sel_dict[stat["Quest_MID"]])),msg)
            elif stat["MenuID"] == 2:
                self.add_log("[Work]\nWhich Work to go?",msg)
                self.add_log(self.combine(self.choice_text(["看板もち","交通量調査","警備員","パン工場","窓そうじ","工事現場","Modoru"])),msg)
            elif stat["MenuID"] == 3:
                self.gen_global_shop()
                self.rpgdata[msg._from]["Stats"]["Shop"]["List"] = self.gen_private_shop(msg)
                self.rpgdata[msg._from]["Stats"]["Screen"] = "shop"
            elif stat["MenuID"] == 4:
                if stat["Setting_ID"] == 0:
                    self.add_log("[Setting]\nWhich Setting to ?",msg)
                    self.add_log(self.combine(self.choice_text(["Inventory","Equipment","Skill","Use_Announce","Use_Kana","Modoru"])),msg)
                elif stat["Setting_ID"] == 1:
                    self.add_log("[Inventory]\n<Now You have>",msg)
                    self.add_log(self.combine(self.choice_text(self.rpgdata[msg._from]["Inventory"].keys())),msg)
                    self.add_log("<Storage>",msg)
                    self.add_log(self.combine(self.choice_text(self.rpgdata[msg._from]["Items"].keys())),msg)
            if stat["MenuID"] != 3:
                self.send_log(msg)
                self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = True
            else:
                self.process_shop(msg)
        else:
            #選択肢に応じて処理―
            #メインメニュー
            if stat["MenuID"] == 0:
                choice = self.choicer(msg.text,["Quest","Work","Shop","Setting"])
                if choice != None:
                    if choice == "Quest":
                        stat["MenuID"] = 1
                        stat["Quest_MID"] = 0
                    elif choice == "Work":
                        stat["MenuID"] = 2
                        stat["Work_MID"] = 0
                    elif choice == "Shop":
                        stat["MenuID"] = 3
                    elif choice == "Setting":
                        stat["MenuID"] = 4
                        stat["Setting_ID"] = 0
                    self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                    self.process_menu(msg)
            #クエストメニュー
            elif stat["MenuID"] == 1:
                choice = self.choicer(msg.text,self.quest_sel_dict[stat["Quest_MID"]])
                if choice != None:
                    if stat["Quest_MID"] == 0:
                            if choice == "Main": stat["Quest_MID"] = 1
                            elif choice == "Sub": stat["Quest_MID"] = 2
                            elif choice == "Event": stat["Quest_MID"] = 3
                            elif choice == "Modoru": stat["MenuID"] = 0
                            self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                            self.process_menu(msg)
                    else:
                            if choice != "Modoru": self.rpgdata[msg._from]["Stats"]["Quest"]["Quest_Name"] = choice
                            elif choice == "Modoru": stat["Quest_MID"] = 0
                            self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                            if choice != "Modoru":
                                self.rpgdata[msg._from]["Stats"]["Screen"] = "quest"
                                self.process_quest(msg)
                            else:
                                self.process_menu(msg)
            #ワークメニュー
            elif stat["MenuID"] == 2:
                choice = self.choicer(msg.text,["看板もち","交通量調査","警備員","パン工場","窓そうじ","工事現場","Modoru"])
                if choice != None:
                    if choice == "看板持ち":
                        pass
                    elif choice == "Modoru":
                        stat["MenuID"] = 0
                    self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                    self.process_menu(msg)
            #ショップメニュー
            elif stat["MenuID"] == 3:
                pass
                # choice = self.choicer(msg.text,["A","B","C","Modoru"])
                # if choice != None:
                    # if choice == "":
                        # pass
                    # elif choice == "Modoru":
                        # stat["MenuID"] = 0
                    # self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                    # self.process_menu(msg)
            #設定メニュー
            elif stat["MenuID"] == 4:
                choice = self.choicer(msg.text,["Inventory","Equipment","Skill","Use_Announce","Use_Kana","Modoru"])
                if choice != None:
                    if choice == "Inventory":
                        stat["Setting_ID"] = 1
                    elif choice == "Modoru":
                        stat["MenuID"] = 0
                    self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                    self.process_menu(msg)

RPGer = RPG()
RPGer.process_rpg(Message())

while True:
    inp = input(">>")
    RPGer.process_rpg(Message(text=inp))