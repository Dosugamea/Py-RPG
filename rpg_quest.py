import json,random
from collections import OrderedDict
from datetime import datetime

'''
    クエスト名:
    [X]で固定値 [X,Y]で X～Y表記

    開始要求アイテム Req
    　　[アイテムID,個数]

    　ウェーブ数:
    Mapsをlen()してもわからんのでここで指定
    [X]で固定値 [X,Y]で X～Y表記

    　マップ(ルーム)一覧:
    {イベントデータ},
    {イベントデータ or None}

    モンスター(編成一覧):
    (編成ID)[
        (ウェーブ)
        [
            (チーム)
            [
                {"敵データ"},
                {"敵データ"},
                {"敵データ"}
            ]
        ]
    ]

    ドロップアイテム
    　アイテムID 個数 入手確率

    イベントID:
    1: テキスト表示 Param なし
    2: ダメージ Param["最低値","最大値"]
    3: 回復 Param["最低値","最大値"]
    4: 宝箱 Param[[ドロップアイテムリスト],本物である確率]
    5: 戦闘 Param[編成ID,編成Wave2,編成Wave3...]
    6: ジャンプ Param[ジャンプ先ID,ランダムジャンプ先ID,ランダムジャンプ先ID...]
    7: 分かれ道 Param[[選択肢名,ジャンプ先ID],[選択肢名,ジャンプ先ID]...]
    8: 行き止まり Param[ドロップアイテムデータ,ドロップアイテムデータ...]
    9: ゴール Param[ドロップアイテムデータ,ドロップアイテムデータ...]

    コマンド
    rest
    go
    item
    leave
    map
'''
#てんぷれっ!
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

#クエスト進行 ユーティリティ
class Q_Utility(object):
    #使わないだろうけど...
    def ls2txt(self,ls):
        if len(ls) == 1: return str(ls[0])
        else: return "%s～%s"%(ls[0],ls[1])
    
    #仮置き。 Battleのを引っ張ってくると動かないからTODO
    def game_check(self,msg):
        pass
    
    #仮置き。 BattleのNewEntityを引っ張ってくる。
    def new_entity(self,type,msg):
        p = {
            "Name":"Domao",
            "HP":30,
            "MAX_HP":30,
            "MP":20,
            "MAX_MP":20,
        }
        return p

    def new_quest(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        stat["Current_Quest"] = self.questdata[stat["Quest_Name"]]
        stat["Current_Position"] = 0
        stat["Player"] = self.new_entity(1,"MID")
        self.rpgdata[msg._from]["Stamina"] -= stat["Current_Quest"]["Stamina"]
        self.add_log("<<< %s に出発します >>>\n"%(stat["Quest_Name"]),msg)
        self.log_q_status(msg)
        self.send_log(msg)
        
    def log_q_status(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        self.add_log("",msg)
        self.add_log("[フロア%s  HP: %s/%s MP: %s/%s]"%(stat["Current_Position"]+1,stat["Player"]["HP"],stat["Player"]["MAX_HP"],stat["Player"]["MP"],stat["Player"]["MAX_MP"]),msg)
        self.add_log("%sはどうする?"%(self.rpgdata[msg._from]["Name"]),msg)
        self.add_log(' あ : 進む\n い : 休む\n う : アイテム\n え : マップ\n お : 撤退',msg)
        
        
#クエスト進行 処理本体
class Q_Process(object):
    #コマンド:進む
    def process_go(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        data = stat["Current_Quest"]["Map"][stat["Current_Position"]]
        if "Message" in data: self.add_log(data["Message"],msg)
        if data["Type"] == 2: self.Damage(data,msg)
        elif data["Type"] == 3: self.Heal(data,msg)
        elif data["Type"] == 4: self.Treasure(data,msg)
        elif data["Type"] == 5: self.Battle(data,msg)
        elif data["Type"] == 6: self.Jump(data,msg)
        elif data["Type"] == 7: self.Switch(data,msg)
        elif data["Type"] == 8: self.Stop(data,msg)
        elif data["Type"] == 9: self.Goal(data,msg)
        stat["Current_Position"] += 1
        self.log_q_status(msg)
        self.send_log(msg)
    
    #コマンド:休む
    def process_rest(self,msg):
        pass
        
    def Damage(self,data,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        '''
        2: ダメージ Param["最低値","最大値"]
        '''
        dmg = data["Param"]
        if len(dmg) == 1:
            if isinstance(dmg[0], str):
                dmg = int(stat["Player"]["HP"] * (int(dmg[0][:dmg[0].find("%")])/100))
            else:
                dmg = dmg[0]
        else:
            if isinstance(dmg[0], str): st = int(stat["Player"]["HP"] * (int(dmg[0][:dmg[0].find("%")])/100))
            else: st = dmg[0]
            if isinstance(dmg[1], str): ed = int(stat["Player"]["HP"] * (int(dmg[1][:dmg[1].find("%")])/100))
            else: ed = dmg[1]
            dmg = random.randint(st,ed)
        stat["Player"]["HP"] -= dmg
        self.add_log("%sは%sのダメージを受けた"%(stat["Player"]["Name"],dmg),msg)
        if stat["Player"]["HP"] <= 0:
            self.add_log("%sは倒れた"%(stat["Player"]["Name"]),msg)
            self.game_check(msg)
        
    def Heal(self,data,msg):
        '''
        3: 回復 Param["最低値","最大値"]
        '''
        hel = data["Param"]
        if len(hel) == 1:
            if isinstance(hel[0], str): hel = int(self.user.MAX_HP * (int(hel[0][:hel[0].find("%")])/100))
        elif len(hel) == 2:
            hel = []
            if isinstance(hel[0], str): hel[0] = int(self.user.MAX_HP * (int(hel[0][:hel[0].find("%")])/100))
            if isinstance(hel[1], str): hel[1] = int(self.user.MAX_HP * (int(hel[1][:hel[1].find("%")])/100))
            hel = random.randint(hel[0],hel[1])
        self.user.HP += hel
        print("%sは%s 回復した"%(self.user.name,hel))
        if self.user.HP > self.user.MAX_HP: self.user.HP = self.user.MAX_HP
        
    def Get_Item(self,itemlist,msg):
        '''
        4 8 9: アイテム入手 Param[[[アイテムID,個数,入手確率],[アイテムID,個数,入手確率]...]]
        '''
        print("引数: %s"%(itemlist))
        
    def Treasure(self,data,msg):
        '''
        4: 宝箱 Param[[ドロップアイテムリスト],本物である確率,[偽物である場合の編成リスト]]
        '''
        while True:
            inp = input("開けますか? >>")
            if inp == "y":
                #ドロップアイテムリストだけなら リストをGetに投げる
                if len(data["Param"]) == 1:
                    self.Get_Item(data["Param"][0])
                elif len(data["Param"]) == 2:
                    per = random.randint(1,100)
                    if per <= data["Param"][1]:
                        self.Get_Item(data["Param"][0])
                    else:
                        print("中身は空だった...")
                else:
                    per = random.randint(1,100)
                    if per <= data["Param"][1]:
                        self.Get_Item(data["Param"][0])
                    else:
                        print("!? これは宝箱じゃないぞ!")
                        self.Battle(random.choice(self.data["Param"][2]))
                break
            elif inp == "n":
                print("罠かもしれない。 開けないことにした...")
                break
        
    def Battle(self,data,msg):
        '''
        5: 戦闘 Param[編成ID,編成Wave2,編成Wave3...]
        '''
        print("引数: %s"%(data))
    
    def Jump(self,data,msg):
        '''
        6: ジャンプ Param[ジャンプ先ID,ランダムジャンプ先ID,ランダムジャンプ先ID...]
        '''
        self.cp = random.choice(data["Param"]) -1
    
    def Switch(self,data,msg):
        '''
        7: 分かれ道 Param[[選択肢名,ジャンプ先ID],[選択肢名,ジャンプ先ID]...]
        '''
        jumped = False
        for choice in data["Param"]:
            print("->%s"%(choice[0]))
        while True:
            if jumped: break
            inp = input('どこに進む? >>')
            for choice in data["Param"]:
                if inp == choice[0]:
                    self.cp = choice[1]
                    self.GO()
                    jumped = True
                    break

    def Stop(self,data,msg):
        '''
        8: 行き止まり Param[ドロップアイテムデータ,ドロップアイテムデータ...]
        '''
        #強制終了フラグを立てる
        self.cp = -2
        if "Param" in data: self.Get_Item(data["Param"])
        
    def Goal(self,data,msg):
        '''
        9: ゴール Param[ドロップアイテムデータ,ドロップアイテムデータ...]
        '''
        self.cp = -1
        if "Param" in data: self.Get_Item(data["Param"])
    


class RPG(Logger,Choicer,Q_Process,Q_Utility):
    cl = Client()
    rpgdata = {
        "User":{
            "Name":"Domao",
            "Stamina": 20,
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
                "Quest":{
                    "Quest_Name":"デバッグクエスト",
                    "Current_Position":0,
                    "Current_Quest":{},
                    "Questing": True
                },
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
    with open("QuestData.json",encoding="utf-8_sig") as f:
        questdata = json.loads(f.read(), object_pairs_hook=OrderedDict)
        
    def process_rpg(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]
        if stat["Quest"]["Questing"]: self.process_quest(msg)
    
    def process_quest(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        choice = self.choicer(msg.text,["進む","休む","アイテム","マップ","撤退","はい","いいえ"])
        if choice == "進む":
            self.process_go(msg)
        elif choice == "休む":
            self.process_rest(msg)
        elif choice == "アイテム":
            pass
        elif choice == "マップ":
            #画像を送るかMap -> Text 関数を使うか
            pass
        elif choice == "撤退":
            self.add_log("撤退するとクエスト失敗になりますが\nよろしいですか?",msg)
            self.add_log(" か: はい\n き: いいえ",msg)
            self.send_log(msg)
        elif choice == "はい":
            pass
        elif choice == "いいえ":
            pass


RPGer = RPG()
RPGer.new_quest(Message())

while True:
    inp = input(">>")
    RPGer.process_rpg(Message(text=inp))