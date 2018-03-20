import random,sys

#戦闘データ WAVE-MONSTER-DROP        
battle_data = {
    "1": {
        "1":{
            "MONSTER_ID": "NicoNico",
            "LV": 1,
            "DROP": {
                "1":{
                    "ITEM_ID":"Cookie",
                    "COUNT":10,
                    "PERCENT":100
                }
            }
        }
    }
}

#敵のデータ辞書  Type= 0/無属性 1/水 2/炎 3/風 4/土 5/闇 6/光
enemy_dict = {
    "NicoNico":{
        "About": "爆破しなきゃ(使命)",
        "TYPE": 3,
        "CHARGE":0,
        "CHARGE_BAR": 7,
        "HP": 20,
        "MP" : 10,
        "ATK": 2,
        "MAT": 2,
        "DEF": 5,
        "MDF": 10,
        "SPD": 100,
        "LUK": 10,
        "Percents":{
            75:"Defaults",
            100:"Specials"
        },
        "Skills": {
            "Defaults":{
                "Auto":True,
                1:{"Name":"月額540円"},
                2:{"Name":"GINZA"},
                3:{"Name":"原宿"}
            },
            "Specials":{
                "Auto":True,
                10:{
                    "Name":"いいじゃないココが盛り上がっていれば",
                    "About":"それは遅刻の言い訳にならない。",
                    "MAT":5,
                    "HIT":100,
                    "TYPE":0
                },
                20:{
                    "Name":"デクレッシェンド",
                    "About":"独自の最先端機能を搭載する予定。",
                    "MAT":5,
                    "HIT":100,
                    "TYPE":0
                },
                100:{
                    "Name":"みんな空気読め",
                    "About":"皆さんのコンテンツやコメントを消したいわけではないのです。",
                    "MAT":10,
                    "HIT": 65,
                    "TYPE":5
                }
            },
            "Charge":{
                7:{
                    "1":{
                        "Name":"ニコニコ本社が池袋に誕生",
                        "About": "世界一爆発され、喜ばれた建物",
                        "ATK":18,
                        "HIT": 85,
                        "TYPE":2
                    }
                }
            }
        }
    }
}

user_skill_dict = {
    "Fire":{
        "Name":"ファイアボール!",
        "About": "炎を纏ったボールを放つ、2回ぐらい跳ねそう",
        "TYPE": 2,
        "MAT": 3,
        "HIT": 90,
        "Cost": 5
    },
    "Freeze":{
        "Name":"カチカチ!",
        "About": "氷を纏ったボールを放つ、2回ぐらい跳ねそう",
        "TYPE": 1,
        "MAT": 3,
        "HIT":90,
        "Cost": 5
    },
    "DirtyHack":{
        "Name":"クラッキング!",
        "About": "けがれた魔法",
        "TYPE": 4,
        "MAT": 2,
        "HIT":95,
        "Cost": 10
    }
}

#Type= 0/無属性 1/水 2/炎 3/風 4/土 5/闇 6/光
type_dict = {
    0:"ノーマル",
    1:"水",
    2:"炎",
    3:"風",
    4:"土",
    5:"闇",
    6:"光"
}

help_dict = {
    "help": "このヘルプを表示する",
    "attack": "攻撃する",
    "defense": "防御する",
    "info": "敵の情報を調べる"
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
    SPD = 10
    Skills = None

#プレイヤー型 (後にユーザーデータから取るように変更する)
class Player(Entity):
    def __init__(self, name, LV, Skills):
        self.name = name
        self.LV = LV
        self.TYPE = 0
        self.MAX_HP = self.HP = 50 + int(LV*0.2)
        self.MAX_MP = self.MP = 30 + int(LV*0.2)
        self.ATK = 10 + int(LV*0.15)
        self.MAT = 10 + int(LV*0.1)
        self.DEF = 1 + int(LV*0.1)
        self.SPD = 20 + int(LV*0.01)
        self.Skills = Skills

#敵の情報
class Enemy(Entity):
    def __init__(self, name, level,HP=None,MP=None,SPD=None,ATK=None,DEF=None):
        self.name = name
        self.LV = level
        #辞書にあれば辞書から取る
        if name in enemy_dict:
            self.HP = self.MAX_HP = enemy_dict[name]["HP"]
            self.MP = self.MAX_MP = enemy_dict[name]["MP"]
            self.TYPE = enemy_dict[name]["TYPE"]
            self.ATK = enemy_dict[name]["ATK"]
            self.MAT = enemy_dict[name]["MAT"]
            self.DEF = enemy_dict[name]["DEF"]
            self.MDF = enemy_dict[name]["MDF"]
            self.SPD = enemy_dict[name]["SPD"]
            self.LUK = enemy_dict[name]["LUK"]
            self.Percents = enemy_dict[name]["Percents"]
            self.Skills = enemy_dict[name]["Skills"]
        #レベルに合わせてATKを弄る
        self.HP = self.MAX_HP = int(self.HP*(1+((level/5))))
        self.ATK = self.ATK*(1+(random.randint(0,3)/10))*(1+((level/5)))

class Battle(object):
    #プレイヤーに見えるターン数
    turn = 1
    #内部ターンID(1ターンが終わったら0に戻る)
    i_turn = 0
    #敵かプレイヤーの処理が終わるとこれを返す(予定)
    log_text = ""

    #スピード計算機(スキル等で変わる可能性があるのでここに置く)
    def gen_entities_list(self,entities):
        spls = []
        for entity in entities:
            spls.append((entity.SPD,entity))
        speed_list = sorted(spls,reverse=True)
        self.entities = [i[1] for i in speed_list]

    #ターン処理
    def process_turn(self):
        entity = self.entities[self.i_turn]
        if type(entity) == Enemy:
            self.process_enemy(entity)
        elif type(entity) == Player:
            self.process_player(entity)
        self.i_turn += 1
        if self.i_turn >= len(self.entities):
            self.i_turn = 0
            self.turn += 1
    
    #辞書から一覧を作りランダムに選んで返す
    def pick_by_dict_per(self,dic):
        if "Auto" in dic:
            ls = list(dic.keys())
            ls.remove("Auto")
            return random.choice(ls)
        num = random.randint(1,100)
        for key in dic:
            if num <= key:
                return key
    
    #敵の処理 (プレイヤーに対して攻撃する)
    def process_enemy(self,enemy):
        #スキルを選ぶ
        pick = self.pick_by_dict_per(enemy.Percents)
        skill_dic = enemy.Percents[pick]
        pick = self.pick_by_dict_per(enemy.Skills[skill_dic])
        skill = enemy.Skills[skill_dic][pick]
        skill["S_Type"] = skill_dic
        if skill["S_Type"] == "Defaults":
            print(skill["Name"])
            self.attack(enemy,self.user)
        elif skill["S_Type"] == "Specials":
            skill["MAT"] += enemy.MAT
            self.magic_attack(enemy,self.user,skill)
        
    #プレイヤーの処理
    def process_player(self,player):
        self.show_status(self.user,self.teki)
        print("%sはどうする?"%(self.user.name))
        bye = False
        while True:
            if bye: break
            line = input("< ")
            for c in cmd_dict.keys():
                if line == c:
                    cmd_dict[c](gm)
                    bye = True
                    break
            for s in self.user.Skills:
                if line == s:
                    if self.user.MP >= self.user.Skills[s]["Cost"]:
                        self.user.MP -= self.user.Skills[s]["Cost"]
                        self.magic_attack(self.user,self.teki,self.user.Skills[s])
                    else:
                        print("MPが足りません")
                    bye = True
                    break

    #ダメージ計算機
    def gen_damage(self,_from,to,type=1,Skill=None):
        if Skill == None: Skill = {"TYPE":_from.TYPE}
        if type == 1:
            damage = int(((_from.MAT+Skill["MAT"])*(1+(random.randint(0,3)/10))) - (to.MDF * (random.randint(3,6)/10)))
        else:
            damage = int((_from.ATK*(1+(random.randint(0,3)/10))) - (to.DEF * (random.randint(3,6)/10)))
        #クリティカル(通常30%)が出たら 1.2~1.3倍のダメージ
        if random.randint(1,100) < _from.LUK + 20:
            print("クリティカル！")
            damage = int(damage*1+(random.randint(2,3)/10))
        #Type= 0/無属性 1/水 2/炎 3/風 4/土 5/闇 6/光
        #相性が良ければ 1.3~1.5倍のダメージ
        if (Skill["TYPE"] == 1 and to.TYPE == 2
        or Skill["TYPE"] == 2 and to.TYPE == 3
        or Skill["TYPE"] == 3 and to.TYPE == 4
        or Skill["TYPE"] == 4 and to.TYPE == 1
        or Skill["TYPE"] == 5 and to.TYPE == 6
        or Skill["TYPE"] == 6 and to.TYPE == 5):
            damage = int(damage * (1+(random.randint(4,5)/10)))
            print("あいしょうはばつぐんだ！")
        #相性が悪ければ 0.4~0.6倍のダメージ
        if (Skill["TYPE"] == 1 and to.TYPE == 4
        or Skill["TYPE"] == 4 and to.TYPE == 3
        or Skill["TYPE"] == 3 and to.TYPE == 2
        or Skill["TYPE"] == 2 and to.TYPE == 1):
            damage = int(damage * (random.randint(4,6)/10))
            print("こうかはいまひとつのようだ...")
        return damage
        
    #ダメージを受けさせる
    def get_damage(self,to,damage):
        if damage <= 0: damage = 0
        to.HP -= damage
        print("%sは%sのダメージを受けた"%(to.name,damage))
        if to.HP <= 0:
            print("%sは倒れた"%(to.name))
            self.game_check()

    #敵の攻撃/自分の攻撃共通で下記攻撃処理を通す
    #物理攻撃
    def attack(self,_from,to):
        print("%sの攻撃"%(_from.name))
        #ダメージ計算して、ダメージを受ける
        damage = self.gen_damage(_from,to,0)
        self.get_damage(to,damage)
    #魔法攻撃
    def magic_attack(self,_from,to,Skill):
        print("%sの攻撃"%(_from.name))
        print(Skill["Name"])
        #命中率的な設定
        if random.randint(1,100) < Skill["HIT"]:
            #ダメージ計算して♡
            damage = self.gen_damage(_from,to,1,Skill)
            self.get_damage(to,damage)
        else:
            print("%sの攻撃は外れた"%(_from.name))
    #防御
    def defense(self,user,enemy):
        self.user.DEF += 10
        self.user.MDF += 10
        self.attack(enemy,user)
        self.user.DEF -= 10
        self.user.MDF -= 10

#ユーザーの入力に応じてコマンドを実行する
class Commands(Battle):
    def test(self):
        self.process_turn()
    def help(self):
        print (cmd_dict.keys())
    def kougeki(self):
        self.attack(self.user,self.teki)
    def bougyo(self):
        self.defense(self.user,self.teki)
    def info(self):
        print("[LV:%s %s]\nHP:%s\nMP:%s"%(self.teki.LV,self.teki.name,self.teki.MAX_HP,self.teki.MAX_MP))
        print("Attribute: %s"%(type_dict[self.teki.TYPE]))
        if self.teki.name in enemy_dict:
            print("Description: %s"%(enemy_dict[self.teki.name]["About"]))
        else:
            print("Description: No Info")
        self.attack(self.teki,self.user)
    def show_items(self,user):
        pass
    def show_skills(self):
        print("[Skills]")
        for skill in self.user.Skills:
            print("%s : COST %s TYPE:%s\n %s"%(skill,self.user.Skills[skill]["Cost"],type_dict[self.user.Skills[skill]["TYPE"]],self.user.Skills[skill]["About"]))
        print("backで戻る")
        bye = False
        while True:
            if bye: break
            line = input("> ")
            for s in self.user.Skills:
                if line == s:
                    if self.user.MP >= self.user.Skills[s]["Cost"]:
                        self.user.MP -= self.user.Skills[s]["Cost"]
                        self.magic_attack(self.user,self.teki,self.user.Skills[s])
                        bye = True
                    else:
                        print("MPが足りません")
                    break
                if line == "back":
                    bye = True
                    self.help()
                    break
    def show_status(self,user,enemy):
        print("\n/// You: %s/%s %s/%s Enemy: %s/%s ///"%(user.HP,user.MAX_HP,user.MP,user.MAX_MP,enemy.HP,enemy.MAX_HP))

        
cmd_dict = {
    "help": Commands.help,
    "attack": Commands.kougeki,
    "spell": Commands.show_skills,
    "defense": Commands.bougyo,
    "info": Commands.info,
    "test": Commands.test
}
        
class Game(Commands):
    user = Player("Domao",5,user_skill_dict)
    teki = Enemy("NicoNico",11)
    
    def __init__(self):
        print("Game Initialized")
        self.gen_entities_list([self.user,self.teki])
        print(self.entities)
    
    def game_check(self):
        if self.user.HP <= 0:
            print("GAME OVER")
            line = input("> ")
            sys.exit()
        if self.teki.HP <= 0:
            print("GAME CLEAR")
            line = input("> ")
            sys.exit()
    
    def start(self):
        print("%sが現れた!"%(self.teki.name))
        while True:
            self.game_check()
            self.process_turn()
gm = Game()
gm.start()