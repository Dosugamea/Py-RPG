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
        "CHARGE": 7,
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
                1:{
                    "Name":"月額540円",
                    "Entire": True
                },
                2:{
                    "Name":"GINZA",
                    "Entire": True
                },
                3:{
                    "Name":"原宿",
                    "Entire": True  
                }
            },
            "Specials":{
                "Auto":True,
                10:{
                    "Entire": False,
                    "Name":"いいじゃないココが盛り上がっていれば",
                    "About":"それは遅刻の言い訳にならない。",
                    "MAT":5,
                    "HIT":100,
                    "TYPE":0
                },
                20:{
                    "Entire": False,
                    "Name":"デクレッシェンド",
                    "About":"独自の最先端機能を搭載する予定。",
                    "MAT":5,
                    "HIT":100,
                    "TYPE":0
                },
                100:{
                    "Entire": False,
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
                        "Entire": True,
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

#ユーザースキル辞書(サンプル プレイヤー毎に変えることももちろん可)
user_skill_dict = {
    "Fire":{
        "Name":"ファイアボール!",
        "About": "炎を纏ったボールを放つ、2回ぐらい跳ねそう",
        "Entire": False,
        "TYPE": 2,
        "MAT": 3,
        "HIT": 90,
        "Cost": 5
    },
    "Freeze":{
        "Name":"カチカチ!",
        "About": "氷を纏ったボールを放つ、2回ぐらい跳ねそう",
        "Entire": False,
        "TYPE": 1,
        "MAT": 3,
        "HIT":90,
        "Cost": 5
    },
    "DirtyHack":{
        "Name":"クラッキング!",
        "About": "けがれた魔法",
        "Entire": False,
        "TYPE": 4,
        "MAT": 2,
        "HIT":95,
        "Cost": 10
    }
}

#数字タイプ -> タイプ文字の変換
type_dict = {
    0:"ノーマル",
    1:"水",
    2:"炎",
    3:"風",
    4:"土",
    5:"闇",
    6:"光"
}
#ヘルプ辞書
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
#エネミー型
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
            self.CHG = 0
            self.MAX_CHG = enemy_dict[name]["CHARGE"]
            self.Charges = enemy_dict[name]["Skills"]["Charge"]
            self.Percents = enemy_dict[name]["Percents"]
            self.Skills = enemy_dict[name]["Skills"]
        #レベルに合わせてATKを弄る
        self.HP = self.MAX_HP = int(self.HP*(1+((level/5))))
        self.ATK = self.ATK*(1+(random.randint(0,3)/10))*(1+((level/5)))
#戦闘処理
class Battle(object):
    #選択肢を数字かひらがなで選べるようにする(最大47個まで選べる)
    kanas = ['あ', 'い', 'う', 'え', 'お',
        'か', 'き', 'く', 'け', 'こ',
        'さ', 'し', 'す', 'せ', 'そ',
        'た', 'ち', 'つ', 'て', 'と',
        'な', 'に', 'ぬ', 'ね', 'の',
        'は', 'ひ', 'ふ', 'へ', 'ほ',
        'ま', 'み', 'む', 'め', 'も',
        'や', 'ゆ', 'よ',
        'ら', 'り', 'る', 'れ', 'ろ',
        'わ', 'を', 'ん']
    nums = [str(i) for i in range(1,48)]

    #プレイヤーに見えるターン数
    turn = 1
    #内部ターンID(1ターンが終わったら0に戻る)
    i_turn = 0
    #敵かプレイヤーの処理が終わるとこれを返す(予定)
    log_text = ""
    
    #敵一覧/プレイヤー一覧を呼ぶ
    def gen_enemys(self):
        return [e for e in self.entities if type(e) == Enemy]
    def gen_players(self):
        return [e for e in self.entities if type(e) == Player]
    #スピード計算機(スキル等で変わる可能性があるのでここに置く)
    def gen_entities_list(self,entities):
        speed_list = sorted(entities,reverse=True,key=lambda entity: entity.SPD)
        self.entities = speed_list
        cnt = [1,1]
        for entity in self.entities:
            if type(entity) == Enemy:
                entity.ID = "e"+str(cnt[0])
                cnt[0] += 1
            elif type(entity) == Player:
                entity.ID = "p"+str(cnt[1])
                cnt[1] += 1
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
    #敵の処理 (プレイヤーに対して攻撃する)
    def process_enemy(self,enemy):
        enemy.CHG += 1
        if enemy.CHG <= enemy.MAX_CHG:
            enemy.CHG = 0
        player = random.choice(self.gen_players())
        #スキルを選ぶ
        if enemy.CHG not in enemy.Charges:
            pick = self.pick_by_dict_per(enemy.Percents)
            skill_dic = enemy.Percents[pick]
            pick = self.pick_by_dict_per(enemy.Skills[skill_dic])
            skill = enemy.Skills[skill_dic][pick]
            skill["S_Type"] = skill_dic
        else:
            skill = random.choice(enemy.Charges[enemy.CHG])
        if "MAT" in skill: skill["MAT"] += enemy.MAT
        if "ATK" in skill: skill["ATK"] += enemy.ATK
        if "LUK" in skill: skill["LUK"] += enemy.LUK
        if enemy.CHG not in enemy.Charges:
            if skill["S_Type"] == "Defaults":
                if skill["Entire"]:
                    self.attack_all(enemy,Player)
                else:
                    self.attack(enemy,player,skill)
            elif skill["S_Type"] == "Specials":
                if skill["Entire"]:
                    self.magic_attack_all(enemy,skill,Player)
                else:
                    self.magic_attack(enemy,player,skill)
        else:
            if skill["Entire"]:
                self.magic_attack_all(enemy,skill,Player)
            else:
                self.magic_attack(enemy,player,skill)
            
            
    #プレイヤーの処理(コマンドを入力させて実行する)
    def process_player(self,player):
        self.show_status()
        print("%sはどうする?"%(player.name))
        bye = False
        while True:
            if bye: break
            line = input("< ")
            for c in cmd_dict.keys():
                if line == c:
                    cmd_dict[c](gm,player)
                    bye = True
                    break
            for s in player.Skills:
                if line == s:
                    if player.MP >= player.Skills[s]["Cost"]:
                        player.MP -= player.Skills[s]["Cost"]
                        self.magic_attack(player,self.teki,player.Skills[s])
                    else:
                        print("MPが足りません")
                    bye = True
                    break
    #攻撃先を選ぶ (entityを返す)
    def process_select_to(self):
        ens = self.gen_enemys()
        cnt = len(ens)
        if cnt > 1:
            print("To?")
            i = 1
            for entity in self.entities:
                if entity.ID[0] == "e":
                    print(" %s: [Lv%s] %s"%(i,entity.LV,entity.name))
                i += 1
            while True:
                to = input('>>')
                try:
                    if int(to) < cnt+1:
                        id = 0
                        for entity in self.entities:
                            if entity.ID[0] == "e" and entity.ID[1:] == to:
                                e = entity
                                bye = True
                                break
                    if bye: break
                except:
                    pass
            return e
        else:
            return ens[0]
    #IDからentityを消す(未使用)
    def remove_entity(self,ID):
        for i,entity in enumerate(self.entities):
            if entity.ID[0] == ID[0] and int(entity.ID[1:]) == int(ID[1:]):
                self.entities.pop(i)
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
            damage = int(damage*1+(random.randint(2,3)/10))
            print(" クリティカル！")
        #Type= 0/無属性 1/水 2/炎 3/風 4/土 5/闇 6/光
        #相性が良ければ 1.3~1.5倍のダメージ
        if (Skill["TYPE"] == 1 and to.TYPE == 2
        or Skill["TYPE"] == 2 and to.TYPE == 3
        or Skill["TYPE"] == 3 and to.TYPE == 4
        or Skill["TYPE"] == 4 and to.TYPE == 1
        or Skill["TYPE"] == 5 and to.TYPE == 6
        or Skill["TYPE"] == 6 and to.TYPE == 5):
            damage = int(damage * (1+(random.randint(4,5)/10)))
            print(" あいしょうはばつぐんだ！")
        #相性が悪ければ 0.4~0.6倍のダメージ
        if (Skill["TYPE"] == 1 and to.TYPE == 4
        or Skill["TYPE"] == 4 and to.TYPE == 3
        or Skill["TYPE"] == 3 and to.TYPE == 2
        or Skill["TYPE"] == 2 and to.TYPE == 1):
            damage = int(damage * (random.randint(4,6)/10))
            print(" こうかはいまひとつのようだ...")
        return damage
    #ダメージを受ける
    def get_damage(self,to,damage):
        if damage <= 0: damage = 0
        to.HP -= damage
        print("%sは%sのダメージを受けた"%(to.name,damage))
        if to.HP <= 0:
            print("%sは倒れた"%(to.name))
            self.game_check()
    #敵の攻撃/自分の攻撃共通で下記i攻撃処理を通す
    def attack(self,_from,to,sn=None):
        print("%sの攻撃"%(_from.name))
        if sn != None:
            print("<通常> %s"%(sn["Name"]))
        else:
            print("<通常> %sの剣"%(_from.name))
        #ダメージ計算して、ダメージを受ける
        damage = self.gen_damage(_from,to,0)
        self.get_damage(to,damage)
    #指定されたタイプ全てに通常攻撃をする
    def attack_all(self,_from,toType=Player):
        print("%sの攻撃"%(_from.name))
        for entity in self.entities:
            if type(entity) == toType:
                damage = self.gen_damage(_from,entity,0)
                self.get_damage(entity,damage)        
    #魔法攻撃
    def magic_attack(self,_from,to,Skill):
        print("%sの攻撃"%(_from.name))
        print("<スキル> %s"%(Skill["Name"]))
        #命中率的な設定
        if random.randint(1,100) < Skill["HIT"]:
            #ダメージ計算して♡
            damage = self.gen_damage(_from,to,1,Skill)
            self.get_damage(to,damage)
        else:
            print("%sの攻撃は外れた"%(_from.name))
    #指定されたタイプ全てにダメージを与える
    def magic_attack_all(self,_from,Skill,toType=Player):
        print("%sの攻撃"%(_from.name))
        print("<スキル> %s"%(Skill["Name"]))
        if random.randint(1,100) < Skill["HIT"]:
            for entity in self.entities:
                if type(entity) == toType:
                    damage = self.gen_damage(_from,entity,1,Skill)
                    self.get_damage(entity,damage)
        else:
            print(" %sの攻撃は外れた"%(_from.name))
    #防御
    def defense(self):
        user = self.entities[self.i_turn]
        user.DEF += 10
        user.MDF += 10
        self.i_turn += 1
        if self.i_turn >= len(self.entities):
            self.i_turn = 0
            self.turn += 1
        tn = int(self.turn)
        while True:
            self.process_turn()
            if tn > self.turn:
                break
        user.DEF -= 10
        user.MDF -= 10
    #状態を見る 
    def show_status(self):
        print("")
        texts = ["/// 味方 ///"]
        for entity in self.entities:
            if type(entity) == Player:
                texts.append("  [Lv%s] %s %s/%s %s/%s"%(entity.LV,entity.name,entity.HP,entity.MAX_HP,entity.MP,entity.MAX_MP))
        texts.append("/// 敵 ///")
        for entity in self.entities:
            if type(entity) == Enemy:
                texts.append("  [Lv%s] %s %s/%s"%(entity.LV,entity.name,entity.HP,entity.MAX_HP))
        for t in texts:
            print(t)

#ユーザーの入力に応じてコマンドを実行する
class Commands(Battle):
    def help(self,player):
        print (cmd_dict.keys())
    def kougeki(self,player):
        at_to = self.process_select_to()
        self.attack(player,at_to)
    def skill(self,skill,player):
        if user_skill_dict[skill]["Entire"]:
            self.magic_attack_all(player,skill,Enemy)
        else:
            at_to = self.process_select_to()
            self.magic_attack(player,at_to,player.Skills[skill])
    def bougyo(self,player):
        self.defense(player)
    def info(self,player):
        teki = self.process_select_to()
        print("[LV:%s %s]\nHP:%s\nMP:%s"%(teki.LV,teki.name,teki.MAX_HP,teki.MAX_MP))
        print("Attribute: %s"%(type_dict[teki.TYPE]))
        if teki.name in enemy_dict:
            print("Description: %s"%(enemy_dict[teki.name]["About"]))
        else:
            print("Description: No Info")
    def show_items(self,player):
        pass
    def show_skills(self,player):
        print("[Skills]")
        for skill in player.Skills:
            print("%s : COST %s TYPE:%s\n %s"%(skill,player.Skills[skill]["Cost"],type_dict[player.Skills[skill]["TYPE"]],player.Skills[skill]["About"]))
        print("backで戻る")
        bye = False
        while True:
            if bye: break
            line = input("> ")
            for s in player.Skills:
                if line == s:
                    if player.MP >= player.Skills[s]["Cost"]:
                        player.MP -= player.Skills[s]["Cost"]
                        self.skill(s,player)
                        bye = True
                    else:
                        print("MPが足りません")
                    break
                if line == "back":
                    bye = True
                    break

#コマンド一覧
cmd_dict = {
    "help": Commands.help,
    "attack": Commands.kougeki,
    "spell": Commands.show_skills,
    "defense": Commands.bougyo,
    "info": Commands.info
}

#ゲーム本体     
class Game(Commands):
    #ゲーム初期化
    def __init__(self):
        print("Game Initialized")
        entities = []
        entities.append(Player("Domao",5,user_skill_dict))
        entities.append(Enemy("NicoNico",random.randint(5,11)))
        self.gen_entities_list(entities)
    #ゲーム終了確認
    def game_check(self):
        #HP0のエンティティを削除する
        self.entities = [e for e in self.entities if e.HP > 0]
        #敵がいなくなったら勝ち
        if len(self.gen_enemys()) == 0:
            print("GAME CLEAR")
            line = input("> ")
            sys.exit()
        #プレイヤーがいなくなったら負け
        elif len(self.gen_players()) == 0:
            print("GAME OVER")
            line = input("> ")
            sys.exit()
    #ゲーム開始
    def start(self):
        for entity in self.entities:
            if type(entity) == Enemy:
                print("[Lv%s] %sが現れた!"%(entity.LV,entity.name))
        while True:
            self.game_check()
            self.process_turn()
gm = Game()
gm.start()