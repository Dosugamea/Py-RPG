import random

'''
 クエスト名:
    [X]で固定値 [X,Y]で X～Y表記

 開始要求アイテム Req
　　[アイテムID,個数]
 
　ウェーブ数:
    Mapsをlen()してもわからんのでここで指定
    [X]で固定値 [X,Y]で X～Y表記

　マップ(ルーム)一覧:
    "識別ID": {イベントデータ},
    "識別ID": {イベントデータ or None}
    
 モンスター(編成一覧):
    識別ID:{
        "モンスター1":["最低レベル","最高レベル"]
    }
    
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
'''
quest_data = {
    "デバッグクエスト":{
        "Waves": [6],
        "Start": [1],
        "Map":{
            1: {"Type":1,"Message":"奥へと続いている..."},
            2: {"Type":2,"Message":"石が転がってきた","Param":["5%","10%"]},
            3: {"Type":3,"Message":"回復の泉だ","Param":["100%"]},
            4: {"Type":5,"Message":"何かが動いている!","Param":[1]},
            5: {"Type":6,"Message":"まだまだ奥へと続いている...","Param":[7]},
            6: {"Type":1,"Message":"このメッセージが見れるのはおかしいよ"},
            7: {"Type":7,"Message":"分かれ道だ","Param":[["左へ進む",8],["そのまま進む",10],["右へ進む",12]]},
            8: {"Type":1,"Message":"何もないようだ"},
            9: {"Type":6,"Param":[14]},
            10: {"Type":4,"Message":"宝箱を見つけた","Param":[[1,1,100],10]},
            11: {"Type":6,"Param":[14]},
            12: {"Type":5,"Message":"何かがくねくねしている!","Param":[2]},
            13: {"Type":4,"Message":"宝箱を見つけた","Param":[[1,5,100],100]},
            14: {"Type":9,"Message":"行き止まりのようだ。\n帰ることにした。"}
        },
        "Monsters":{
            1:{ "NicoNico":[1,1] },
            2:{ "NicoNico":[5,10] }
        }
    }
}

hiragana = [chr(i) for i in range(12353, 12436)]

#プレイヤー/敵/NPC関係なく必ずこれらのデータを持っている
class Entity(object):
    name = "UNKNOWN"
    LV = 1
    HP = MAX_HP = 50
    MP = MAX_MP = 10
    ATK = MAT = 10
    MDF = DEF = 10
    LUK = 10
    Skills = None

#プレイヤー型 (後にユーザーデータから取るように変更する)
class Player(Entity):
    def __init__(self, name, LV, Skills, pos=1):
        self.name = name
        self.LV = LV
        self.TYPE = 0
        self.MAX_HP = self.HP = 50 + int(LV*0.2)
        self.MAX_MP = self.MP = 30 + int(LV*0.2)
        self.ATK = 10 + int(LV*0.15)
        self.MAT = 10 + int(LV*0.1)
        self.DEF = 1 + int(LV*0.1)
        self.Skills = Skills

#探索システムメイン
class Dungeon():
    #CurrentPosition
    cp = 1
    def __init__(self,dungeon_data):
        self.dungeon = dungeon_data
        print("Dungeon Initialized")
        
    def Text(self,data):
        print(data["Message"])
        
    def Damage(self,data):
        '''
        2: ダメージ Param["最低値","最大値"]
        '''
        dmg = data["Param"]
        dmg = random.choice(dmg)
        if isinstance(dmg, str): dmg = int(self.user.MAX_HP * (int(dmg[:dmg.find("%")])/100))
        self.user.HP -= dmg
        print("%sは%sのダメージを受けた"%(self.user.name,dmg))
        if self.user.HP <= 0:
            print("%sは倒れた"%(self.user.name))
            self.game_check()
        
    def Heal(self,data):
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
        
    def Get_Item(self,itemlist):
        '''
        4 8 9: アイテム入手 Param[[[アイテムID,個数,入手確率],[アイテムID,個数,入手確率]...]]
        '''
        print("引数: %s"%(itemlist))
        
    def Treasure(self,data):
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
        
    def Battle(self,data):
        '''
        5: 戦闘 Param[編成ID,編成Wave2,編成Wave3...]
        '''
        print("引数: %s"%(data))
    
    def Jump(self,data):
        '''
        6: ジャンプ Param[ジャンプ先ID,ランダムジャンプ先ID,ランダムジャンプ先ID...]
        '''
        self.cp = random.choice(data["Param"]) -1
    
    def Switch(self,data):
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

    def Stop(self,data):
        '''
        8: 行き止まり Param[ドロップアイテムデータ,ドロップアイテムデータ...]
        '''
        #強制終了フラグを立てる
        self.cp = -2
        if "Param" in data: self.Get_Item(data["Param"])
        
    def Goal(self,data):
        '''
        9: ゴール Param[ドロップアイテムデータ,ドロップアイテムデータ...]
        '''
        self.cp = -1
        if "Param" in data: self.Get_Item(data["Param"])
        
    def GO(self):
        data = self.dungeon["Map"][self.cp]
        if "Message" in data: self.Text(data)
        if data["Type"] == 2: self.Damage(data)
        elif data["Type"] == 3: self.Heal(data)
        elif data["Type"] == 4: self.Treasure(data)
        elif data["Type"] == 5: self.Battle(data)
        elif data["Type"] == 6: self.Jump(data)
        elif data["Type"] == 7: self.Switch(data)
        elif data["Type"] == 8: self.Stop(data)
        elif data["Type"] == 9: self.Goal(data)
        self.cp += 1
    
        
#探索を進めるのに使うコマンド一覧
class Commands():
    def rest(self):
        pass
    def go(self):
        self.GO()
    def item(self):
        pass
    def leave(self):
        print("帰還するとここまでのアイテムは入手できませんが\nよろしいですか?")
        print("よろしければ ok と入力してください")
    def ok(self):
        pass
    def back(self):
        pass
    def map(self):
        pass
    def help(self):
        print(self.cmd_dict.keys())
#探索システム と コマンド一覧と プレイヤー型を継承する 
class Search(Dungeon,Commands,Player):
    user = Player("Domao",5,{})
    #stub
    inventory = {}

    def __init__(self):
        super().__init__(quest_data["デバッグクエスト"])
        self.cmd_dict = {
            "go": self.go,
            "rest": self.rest,
            "item": self.item,
            "leave": self.leave,
            "ok": self.ok,
            "back": self.back,
            "map": self.map,
            "help": self.help
        }
        print("Search Initialized")
        
    def show_stat(self):
        print("[%s] %s/%s %s/%s CP:%s"%(self.user.name,self.user.HP,self.user.MAX_HP,self.user.MP,self.user.MAX_MP,self.cp))

    def start(self):
        print("<<<デバッグクエスト>>>")
        while True:
            print("")
            self.show_stat()
            line = input("Command? > ")
            print("")
            for c in self.cmd_dict.keys():
                if line == c:
                    self.cmd_dict[c]()
                    break
sr = Search()
sr.start()