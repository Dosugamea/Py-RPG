'''
 クエスト名:
    [X]で固定値 [X,Y]で X～Y表記

　ウェーブ数:
    Mapsをlen()してもわからんのでここで指定
    [X]で固定値 [X,Y]で X～Y表記

　マップ(ルーム)一覧:
    "識別ID": {イベントデータ or None},
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
        "Waves":　[6],   
        "Start": [1],
        "Maps":{
            1: {"Type":1,"Message":"奥へと続いている..."},
            2: {"Type":2,"Message":"石が転がってきた","Param":["5%","10%"]},
            3: {"Type":3,"Message":"回復の泉だ","Param":["100%"]},
            4: {"Type":5,"Message":"何かが動いている!","Param":[1]},
            5: {"Type":6,"Message":"まだまだ奥へと続いている...","Param":[7]},
            6: {"Type":1,"Message":"このメッセージが見れるのはおかしいよ"},
            7: {"Type":7,"Message":"分かれ道だ","Param":[["左へ進む",8],["そのまま進む",10],["右へ進む",12]]}
            8: {"Type":1,"Message":"何もないようだ"},
            9: {"Type":6,"Param":[14]},
            10: {"Type":4,"Message":"宝箱を見つけた","Param":[[1,1,100],100]},
            11: {"Type":6,"Param":[14]},
            12: {"Type":5,"Message":"何かがくねくねしている!","Param":[2]},
            13: {"Type":4,"Message":"宝箱を見つけた","Param":[[1,5,100],100]},
            14: {"Type":9,"Message":"行き止まりのようだ。\n引き返して帰ることにした。"}
        },
        "Monsters":{
            1:{ "NicoNico":[1,1] },
            2:{ "NicoNico":[5,10] }
        }
    }
}

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
    cp = 0
    def show_text():
        pass
        
    
        
#探索を進めるのに使うコマンド一覧
class Commands():
    def rest():
        pass

#探索システム と コマンド一覧と プレイヤー型を継承する 
class Search(Dungeon,Commands,Player):
    user = Player("Domao",5,{})
    cmd_dict = {
        "rest": rest
    }

    def __init__(self):
        print("Search Initialized")

    def start():
        while True:
            line = input("Command? > ")
            for c in self.cmd_dict.keys():
                if line == c:
                    self.cmd_dict[c]()
                    break

sr = Search()
sr.start()