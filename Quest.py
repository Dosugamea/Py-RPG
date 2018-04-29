import json,random
from datetime import datetime
from copy import deepcopy
from collections import OrderedDict

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

#クエスト進行 ユーティリティ
class Q_Utility(object):
    #使わないだろうけど...
    def ls2txt(self,ls):
        if len(ls) == 1: return str(ls[0])
        else: return "%s～%s"%(ls[0],ls[1])
    '''
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
    '''

    def new_quest(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        stat["Current_Quest"] = self.questdata[stat["Quest_Name"]]
        stat["Current_Position"] = random.choice(self.questdata[stat["Quest_Name"]]["Start"]) -1
        stat["Current_Floor"] = 0
        pdata = self.new_entity(1,mid=msg._from)
        stat["Player"] = OrderedDict()
        stat["Player"]["HP"] = pdata["HP"]
        stat["Player"]["MAX_HP"] = pdata["MAX_HP"]
        stat["Player"]["MP"] = pdata["MP"]
        stat["Player"]["MAX_MP"] = pdata["MAX_MP"]
        stat["Player"]["Name"] = pdata["Name"]
        self.rpgdata[msg._from]["Stamina"] -= stat["Current_Quest"]["Stamina"]
        self.add_log("<<< %s に出発します >>>\n"%(stat["Quest_Name"]),msg)
        self.process_go(msg)
        
    def log_q_status(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        self.add_log("",msg)
        self.add_log("[フロア%s  HP: %s/%s MP: %s/%s]"%(stat["Current_Floor"],stat["Player"]["HP"],stat["Player"]["MAX_HP"],stat["Player"]["MP"],stat["Player"]["MAX_MP"]),msg)
        self.add_log("%sはどうする?"%(self.rpgdata[msg._from]["Name"]),msg)
        self.add_log(' あ : 進む\n い : 休む\n う : アイテム\n え : マップ\n お : 撤退',msg)
        
        
#クエスト進行 処理本体
class Q_Process(object):
    #関数を本体に追加
    def addExecFunction(self,Name,Func):
        self.ExecDatas[Name] = Func

    #コマンド:進む
    def process_go(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        data = stat["Current_Quest"]["Map"][stat["Current_Position"]]
        if "Message" in data: self.add_log(data["Message"],msg)
        if "Exec" in data: self.ExecDatas[data["Exec"]]()
        if data["Type"] == 2: self.Damage(data,msg)
        elif data["Type"] == 3: self.Heal(data,msg)
        elif data["Type"] == 4:
            #Treasure
            stat["Current_Choices"] = data
            stat["Selecting"] = True
        elif data["Type"] == 5: self.Battle(data,msg)
        elif data["Type"] == 6: self.Jump(data,msg)
        elif data["Type"] == 7:
            #Jump
            stat["Current_Choices"] = data
            stat["Selecting"] = True
        elif data["Type"] == 8: self.Stop(data,msg)
        elif data["Type"] == 9: self.Goal(data,msg)
        stat["Current_Position"] += 1
        stat["Current_Floor"] += 1
        #見た目を弄る
        if stat["Selecting"]:
            if stat["Current_Choices"]["Type"] == 4:
                self.add_log(self.combine(self.choice_text(["開ける","開けない"])),msg)
            elif stat["Current_Choices"]["Type"] == 7:
                self.add_log(self.combine(self.choice_text([d[0] for d in stat["Current_Choices"]["Param"]])),msg)
            else:
                raise ValueError
        elif "NoMenu" in data:
            self.add_log("\n"+self.choice_text(["次へ"])[0],msg)
        elif "Message" not in data:
            #メッセージがなければスルーして次へ(Jump)
            self.process_go(msg)
        elif data["Type"] not in [8,9,5]:
            self.log_q_status(msg)
        if data["Type"] not in [5] and stat["Questing"]:
            self.send_log(msg)
    
    #コマンド:休む
    def process_rest(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        
        
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
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        '''
        3: 回復 Param["最低値","最大値"]
        '''
        hel = data["Param"]
        if len(hel) == 1:
            if isinstance(hel[0], str):
                hel = int(stat["Player"]["MAX_HP"] * (int(hel[0][:hel[0].find("%")])/100))
            else:
                hel = hel[0]
        elif len(hel) == 2:
            if isinstance(hel[0], str): st = int(stat["Player"]["HP"] * (int(hel[0][:hel[0].find("%")])/100))
            else: st = hel[0]
            if isinstance(hel[1], str): ed = int(stat["Player"]["HP"] * (int(hel[1][:hel[1].find("%")])/100))
            else: ed = hel[1]
            hel = random.randint(st,ed)
        stat["Player"]["HP"] += hel
        self.add_log("%sは%s 回復した"%(stat["Player"]["Name"],hel),msg)
        if stat["Player"]["HP"] > stat["Player"]["MAX_HP"]:
            stat["Player"]["HP"] = stat["Player"]["MAX_HP"]
        
    def Get_Item(self,itemlist,msg):
        '''
        4 8 9: アイテム入手 Param[[[アイテムID,個数,入手確率],[アイテムID,個数,入手確率]...]]
        '''
        print("引数: %s"%(itemlist))
        
    def Treasure(self,choice,msg):
        data = self.rpgdata[msg._from]["Stats"]["Quest"]["Current_Choices"]
        '''
        4: 宝箱 Param[[ドロップアイテムリスト],本物である確率,[偽物である場合の編成リスト]]
        '''
        if choice == "開く":
            if len(data["Param"]) == 1:
                self.Get_Item(data["Param"][0],msg)
            elif len(data["Param"]) == 2:
                per = random.randint(1,100)
                if per <= data["Param"][1]:
                    self.Get_Item(data["Param"][0],msg)
                else:
                    self.add_log("中身は空だった...",msg)
            else:
                per = random.randint(1,100)
                if per <= data["Param"][1]:
                    self.Get_Item(data["Param"][0],msg)
                else:
                    self.add_log("!? これは宝箱じゃないぞ!",msg)
                    self.Battle(random.choice(data["Param"][2]))
        else:
            self.add_log("罠かもしれない。 開けないことにした...",msg)
        self.rpgdata[msg._from]["Stats"]["Quest"]["Selecting"] = False
        self.process_go(msg)
        
    def Battle(self,data,msg):
        '''
        5: 戦闘 Param[編成ID,編成Wave2,編成Wave3...]
        '''
        q = self.rpgdata[msg._from]["Stats"]["Quest"]["Current_Quest"]
        #print(q)
        self.rpgdata[msg._from]["Stats"]["Screen"] = "battle"
        self.new_battle(q,1,1,msg)
    
    def Jump(self,data,msg):
        '''
        6: ジャンプ Param[ジャンプ先ID,ランダムジャンプ先ID,ランダムジャンプ先ID...]
        '''
        self.rpgdata[msg._from]["Stats"]["Quest"]["Current_Position"] = random.choice(data["Param"])-2
    
    def Switch(self,choice,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        '''
        7: 分かれ道 Param[[選択肢名,ジャンプ先ID],[選択肢名,ジャンプ先ID]...]
        '''
        for c in stat["Current_Choices"]["Param"]:
            if c[0] == choice:
                stat["Current_Position"] = c[1] - 1
                stat["Selecting"] = False
                self.process_go(msg)

    def Stop(self,data,msg):
        '''
        8: 行き止まり Param[ドロップアイテムデータ,ドロップアイテムデータ...]
        '''
        #強制終了フラグを立てる
        print("STOP")
        if "Param" in data: self.Get_Item(data["Param"])
        self.send_log(msg)
        self.End_Quest("Stop",msg)
        
    def Goal(self,data,msg):
        '''
        9: ゴール Param[ドロップアイテムデータ,ドロップアイテムデータ...]
        '''
        print("GOAL")
        if "Param" in data: self.Get_Item(data["Param"])
        self.send_log(msg)
        self.rpgdata[msg._from]["Stats"]["Quest"]["Questing"] = False
        self.End_Quest("Goal",msg)
    
    def level_calc(self,exp,msg):
        data = self.rpgdata[msg._from]
        data["EXP"] += exp
        old_lv = deepcopy(self.rpgdata[msg._from]["Level"])
        ret = False
        while True:
            if data["EXP"] >= self.leveldata[str(data["Level"]+1)]["EXP"]:
                data["Level"] += 1
                ret = True
            else:
                break
        return ret,old_lv
    
    def End_Quest(self,result,msg):
        data = self.rpgdata[msg._from]["Stats"]["Quest"]
        gexp = random.choice(data["Current_Quest"]["Exp"][result])
        self.add_log("<リザルト>",msg)
        self.add_log("\n[ランク]",msg)
        if result == "Goal":
            self.add_log("　　クリア",msg)
            self.add_log("[報酬]",msg)
            if "Reward" in data["Current_Quest"]:
                rw = self.iper2igot(data["Current_Quest"]["Reward"])
                if len(rw) == 0:self.add_log("　なし",msg)
                else:
                    self.igot2data(rw,msg)
                    self.add_log(self.igot2itext(rw),msg)
            else:
                self.add_log("　なし",msg)
        elif result == "Stop":
            self.add_log(" 帰還",msg)
            self.add_log("[報酬]",msg)
            self.add_log("None",msg)
        elif result == "Dead":
            self.add_log(" 撤退",msg)
            self.add_log("[報酬]",msg)
            self.add_log("　なし",msg)
        lvup = self.level_calc(gexp,msg)
        self.add_log("[経験値]",msg)
        self.add_log(" +%s"%(gexp),msg)
        self.send_log(msg)
        if lvup[0]:
            self.add_log("<レベルアップ>",msg)
            self.add_log(" %s -> %s"%(lvup[1],self.rpgdata[msg._from]["Level"]),msg)
            self.send_log(msg)
        self.rpgdata[msg._from]["Stats"]["Screen"] = "menu"
        self.rpgdata[msg._from]["Stats"]["Menu"]["MenuID"] = 0
        self.rpgdata[msg._from]["Stats"]["Menu"]["Quest_MID"] = 0
        self.rpgdata[msg._from]["Stats"]["Menu"]["Setting_ID"] = 0
        self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
        self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
        self.process_rpg(msg)

class Quest(Q_Process,Q_Utility):
    def process_quest(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Quest"]
        if stat["Questing"]:
            if stat["Selecting"]:
                #マップタイプによる選択肢
                if stat["Current_Choices"]["Type"] == 4:
                    choice = self.choicer(msg.text,["開く","開かない"])
                    self.Treasure(choice,msg)
                #マップタイプ: 分かれ道
                elif stat["Current_Choices"]["Type"] == 7:
                    choice = self.choicer(msg.text,[d[0] for d in stat["Current_Choices"]["Param"]])
                    self.Switch(choice,msg)
                else:
                    raise ValueError
            else:
                #デフォルトの進行選択肢
                choice = self.choicer(msg.text,["進む","休む","アイテム","マップ","撤退","はい","いいえ"])
                #はい と いいえ はめんどくさいので妥協
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