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
                    "Selecting":False
                },
                "Quest":{
                }
            }
        }
    }
    
    quest_sel_dict = {
        0:["Main","Sub","Event","Modoru"],
        1:["Story_1","Story_2","Story_3","Modoru"],
        2:["Quest1","Quest2","Quest3","Modoru"],
        3:["Quest1","Quest2","Quest3","Modoru"]
    }
    
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
        print("Called Shop")
        print(self.rpgdata[msg._from]["Stats"])
    
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
                self.add_log("[Shop]\nWhich Shop to go?",msg)
                self.add_log(self.combine(self.choice_text(["A","B","C","Modoru"])),msg)
            elif stat["MenuID"] == 4:
                if stat["Setting_ID"] == 0:
                    self.add_log("[Setting]\nWhich Setting to ?",msg)
                    self.add_log(self.combine(self.choice_text(["Inventory","Equipment","Skill","Use_Announce","Use_Kana","Modoru"])),msg)
                elif stat["Setting_ID"] == 1:
                    self.add_log("[Inventory]\n<Now You have>",msg)
                    self.add_log(self.combine(self.choice_text(self.rpgdata[msg._from]["Inventory"].keys())),msg)
                    self.add_log("<Storage>",msg)
                    self.add_log(self.combine(self.choice_text(self.rpgdata[msg._from]["Items"].keys())),msg)
            self.send_log(msg)
            self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = True
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
                choice = self.choicer(msg.text,["A","B","C","Modoru"])
                if choice != None:
                    if choice == "":
                        pass
                    elif choice == "Modoru":
                        stat["MenuID"] = 0
                    self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                    self.process_menu(msg)
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