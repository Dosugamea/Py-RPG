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
        "HP": 20,
        "MP" : 10,
        "ATK": 2,
        "MAT": 2,
        "DEF": 5,
        "MDF": 10,
        "SPD": 10,
        "Skills": {
            "TEST":{
                "About":"HOGEHOGE",
                "ATK":20,
                "HIT":90,
                "TYPE":1,
                "TURN": -1
            }
        }
    }
}

user_skill_dict = {
    "Fire":{
        "About": "炎を纏ったボールを放つ、2回ぐらい跳ねそう",
        "TYPE": 2,
        "MAT": 3,
        "HIT": 90,
        "Cost": 5
    },
    "Freeze":{
        "About": "氷を纏ったボールを放つ、2回ぐらい跳ねそう",
        "TYPE": 1,
        "MAT": 3,
        "HIT":90,
        "Cost": 5
    },
    "DirtyHack":{
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
            self.DEF = enemy_dict[name]["DEF"]
            self.LUK = 5
            self.Skills = enemy_dict[name]["Skills"]
        #レベルに合わせてATKを弄る
        self.HP = self.MAX_HP = int(self.HP*(1+((level/5))))
        self.ATK = self.ATK*(1+(random.randint(0,3)/10))*(1+((level/5)))

class Battle(object):
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

#ターンとか敵リスト管理とか？
class Field(object):
    def __init__(self,battle_data):
        pass

#ユーザーの入力に応じてコマンドを実行する
class Commands(Battle):
    def help(self):
        print (cmd_dict.keys())
    def kougeki(self):
        self.attack(self.user,self.teki)
        self.attack(self.teki,self.user)
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
                        self.attack(self.teki,self.user)
                    else:
                        print("MPが足りません")
                    bye = True
                    self.help()
                    break
                if line == "back":
                    bye = True
                    self.help()
                    break
    def show_status(self,user,enemy):
        print("/// You: %s/%s %s/%s Enemy: %s/%s ///"%(user.HP,user.MAX_HP,user.MP,user.MAX_MP,enemy.HP,enemy.MAX_HP))

        
cmd_dict = {
    "help": Commands.help,
    "attack": Commands.kougeki,
    "spell": Commands.show_skills,
    "defense": Commands.bougyo,
    "info": Commands.info
}
        
class Game(Commands):
    user = Player("Domao",5,user_skill_dict)
    teki = Enemy("NicoNico",11)
    
    def __init__(self):
        print("Game Initialized")
    
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
        print("%sはどうする?"%(self.user.name))
        self.help()
        while True:
            self.game_check()
            self.show_status(self.user,self.teki)
            line = input("Command? > ")
            for c in cmd_dict.keys():
                if line == c:
                    cmd_dict[c](gm)
                    break
            for s in self.user.Skills:
                if line == s:
                    if self.user.MP >= self.user.Skills[s]["Cost"]:
                        self.user.MP -= self.user.Skills[s]["Cost"]
                        self.magic_attack(self.user,self.teki,self.user.Skills[s])
                        self.attack(self.teki,self.user)
                    else:
                        print("MPが足りません")
                    break
gm = Game()
gm.start()
