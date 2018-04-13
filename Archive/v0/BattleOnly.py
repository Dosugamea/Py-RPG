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
                    1:{
                        "Entire": True,
                        "Name":"ニコニコ本社が池袋に誕生",
                        "About": "世界一爆発され、喜ばれた建物",
                        "ATK":18,
                        "HIT": 85,
                        "TYPE":2
                    }
                }
            }
        },
        "Deny":[]
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
    },
    "ふにゃふにゃ":{
        "Name":"やわらか戦車!",
        "About":"やわらかくなる",
        "Entire": True,
        "Effect": True,
        "TYPE": 1,
        "Power": 1,
        "HIT":95,
        "Cost": 10
    },
    "本気":{
        "Name":"もっと熱くなれよ!",
        "About":"修造のごとく熱くなる",
        "Entire": False,
        "Effect": True,
        "TYPE": 11,
        "Power": 1,
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

#数字効果タイプ -> タイプ文字の変換
effect_dict = {
    0:"攻昇",
    1:"攻少",
    2:"魔昇",
    3:"魔少",
    4:"防昇",
    5:"防少",
    6:"運昇",
    7:"運少",
    8:"俊足",
    9:"鈍足",
    10:"回復",
    11:"気合",
    12:"瀕死",
    13:"運極",
    14:"不幸",
    15:"飢餓",
    16:"空腹",
    17:"火傷",
    18:"毒",
    19:"猛毒",
    20:"病気",
    21:"重病",
    22:"麻痺",
    23:"エロ",
    24:"魅了",
    25:"睡眠",
    26:"凍結",
    27:"盲目",
    28:"疲労",
    29:"混乱",
    30:"憂鬱",
    31:"呪い",
    32:"恐怖",
    33:"中毒",
    34:"沈黙",
    35:"弱気",
    36:"憎悪",
    37:"ドM",
    38:"興奮",
    39:"ドS",
    40:"発情",
    41:"運極",
    42:"暴走",
    43:"属昇",
    44:"属少",
    45:"全昇",
    46:"全少"
}
#ヘルプ辞書
help_dict = {
    "help": "このヘルプを表示する",
    "attack": "攻撃する",
    "defense": "防御する",
    "info": "敵の情報を調べる"
}

#OrderedDictを使えば 効果の重ね順に計算することもできる
#プレイヤー/敵/NPC関係なく必ずこれらのデータを持っている
class Entity(object):
    def __init__(self):
        self.name = "UNKNOWN"
        self.LV = 1
        self.HP = self.MAX_HP = 50
        self.MP = self.MAX_MP = 10
        self.ATK = self.MAT = 10
        self.MDF = self.DEF = 10
        self.LUK = 10
        self.SPD = 10
        self.Skills = None
        self.Deny = [] 
        self.Effects = []
#プレイヤー型 (後にユーザーデータから取るように変更する)
class Player(Entity):
    def __init__(self, name, LV, Skills):
        super().__init__()
        self.name = name
        self.LV = LV
        self.TYPE = 0
        self.MAX_HP = self.HP = 50 + int(LV*0.5)
        self.MAX_MP = self.MP = 30 + int(LV*0.5)
        self.ATK = 10 + int(LV*0.15)
        self.MAT = 10 + int(LV*0.1)
        self.DEF = 1 + int(LV*0.1)
        self.SPD = 20 + int(LV*0.01)
        self.Skills = Skills
        self.Deny = []
#エネミー型
class Enemy(Entity):
    def __init__(self, name, level,HP=None,MP=None,SPD=None,ATK=None,DEF=None):
        super().__init__()
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
            self.Deny = enemy_dict[name]["Deny"]
        #レベルに合わせてATKを弄る
        self.HP = self.MAX_HP = int(self.HP*(1+((level/5))))
        self.ATK = int(self.ATK*(1+(random.randint(1,1)/10))*(1+((level/5))))
#戦闘処理
class Battle(object):
    #選択肢を数字かひらがなで選べるようにする(最大46個まで選べる)
    choices = {'あ':1, 'い':2, 'う':3, 'え':4, 'お':5,
        'か':6, 'き':7, 'く':8, 'け':9, 'こ':10,
        'さ':11, 'し':12, 'す':13, 'せ':14, 'そ':15,
        'た':16, 'ち':17, 'つ':18, 'て':19, 'と':20,
        'な':21, 'に':22, 'ぬ':23, 'ね':24, 'の':25,
        'は':26, 'ひ':27, 'ふ':28, 'へ':29, 'ほ':30,
        'ま':31, 'み':32, 'む':33, 'め':34, 'も':35,
        'や':36, 'ゆ':37, 'よ':38,
        'ら':39, 'り':40, 'る':41, 'れ':42, 'ろ':43,
        'わ':44, 'を':45, 'ん':46}

    #EntityをBattleにぶち込む
    def __init__(self,entities):
        self.turn = 1
        self.i_turn = 0
        self.log_text = ""
        self.entities = entities
        self.sort_by_speed()
        self.gen_IDs()
        print("Battle Initialized")
    #IDからentityを取る
    def get_entity(self,ID,ret_ent=False):
        for i,entity in enumerate(self.entities):
            if entity.ID[0] == ID[0] and int(entity.ID[1:]) == int(ID[1:]):
                if ret_ent: return entity
                else: return i
        return 0
    #IDからentityを消す(デバッグ)
    def remove_entity(self,ID):
        self.entities.pop(self.get_entity(ID))
    #IDからentityを表示(デバッグ)
    def info_entity(self,ID):
        print(self.entities[self.get_entity(ID)].__dict__)
    #敵一覧/プレイヤー一覧を呼ぶ
    def gen_enemys(self):
        return [e for e in self.entities if type(e) == Enemy]
    def gen_players(self):
        return [e for e in self.entities if type(e) == Player]
    #ひらがなか数字を使いリストから選ぶ
    def choicer(self,text="1",ls=["A","B","C"]):
        #あ～ん なら 数値を返す
        if text in Battle.choices:
            if len(ls) >= Battle.choices[text]-1:
                return ls[Battle.choices[text]-1]
            else:
                return False
        elif text in [str(i) for i in Battle.choices.values()]:
            if len(ls) >= int(text)-1:
                return ls[int(text)-1]
            else:
                return False
        else:
            return False
    #選択肢一覧表示
    def show_choices(self,ls=["スキルA","スキルB","スキルC"],kana=True):
        if kana:
            for i,t in enumerate(ls):
                print("%s: %s"%(list(Battle.choices.keys())[i],t))
        else:
            for i,t in enumerate(ls):
                print("%s: %s"%(list(Battle.choices.values())[i],t))
    
    #スピード計算機(スキル等で変わる可能性があるのでここに置く)
    def sort_by_speed(self):
        self.entities = sorted(self.entities,reverse=True,key=lambda entity: entity.SPD)
    #IDを付け直す(死んだら変わるからここに)
    def gen_IDs(self):
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
        self.process_effects_after(entity)
        self.i_turn += 1
        if self.i_turn >= len(self.entities):
            self.i_turn = 0
            self.turn += 1
    #敵の処理 (プレイヤーに対して攻撃する)
    def process_enemy(self,enemy):
        self.process_effects_before(enemy)
        enemy.CHG += 1
        player = random.choice(self.gen_players())
        #スキルを選ぶ
        if enemy.CHG not in enemy.Charges:
            pick = self.pick_by_dict_per(enemy.Percents)
            skill_dic = enemy.Percents[pick]
            pick = self.pick_by_dict_per(enemy.Skills[skill_dic])
            skill = enemy.Skills[skill_dic][pick]
            skill["S_Type"] = skill_dic
        else:
            skill = enemy.Charges[enemy.CHG][random.choice(list(enemy.Charges[enemy.CHG].keys()))]
        #スキルは敵の通常データ+スキルの固有データ
        if "MAT" in skill: skill["MAT"] += enemy.MAT
        if "ATK" in skill: skill["ATK"] += enemy.ATK
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
        if enemy.CHG > enemy.MAX_CHG:
            enemy.CHG = 0     
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
    def process_select_to(self,type):
        if type == Enemy:
            ens = self.gen_enemys()
            st_sw = "e"
        else:
            ens = self.gen_players()
            st_sw = "p"
        cnt = len(ens)
        if cnt > 1:
            print("To?")
            i = 1
            for entity in self.entities:
                if entity.ID[0] == st_sw:
                    print(" %s: [Lv%s] %s"%(i,entity.LV,entity.name))
                i += 1
            while True:
                to = input('>>')
                try:
                    if int(to) < cnt+1:
                        id = 0
                        for entity in self.entities:
                            if entity.ID[0] == st_sw and entity.ID[1:] == to:
                                e = entity
                                bye = True
                                break
                    if bye: break
                except:
                    pass
            return e
        else:
            return ens[0]
    #ATK等の初期化(チャージや現在HPは弄らない)
    def recalc(self,entity):
        if type(entity) == Enemy:
            name = entity.name
            #辞書にあれば辞書から取る
            entity.MAX_HP = enemy_dict[name]["HP"]
            entity.MAX_MP = enemy_dict[name]["MP"]
            entity.TYPE = enemy_dict[name]["TYPE"]
            entity.ATK = enemy_dict[name]["ATK"]
            entity.MAT = enemy_dict[name]["MAT"]
            entity.DEF = enemy_dict[name]["DEF"]
            entity.MDF = enemy_dict[name]["MDF"]
            entity.SPD = enemy_dict[name]["SPD"]
            entity.LUK = enemy_dict[name]["LUK"]
            #レベルに合わせてATKを弄る
            entity.MAX_HP = int(enemy_dict[name]["HP"]*(1+((entity.LV/5))))
            entity.ATK = int(entity.ATK*(1+(random.randint(1,1)/10))*(1+((entity.LV/5))))
        elif type(entity) == Player:
            entity.MAX_HP = 50 + int(entity.LV*0.5)
            entity.MAX_MP = 30 + int(entity.LV*0.5)
            entity.ATK = 10 + int(entity.LV*0.15)
            entity.MAT = 10 + int(entity.LV*0.1)
            entity.DEF = 1 + int(entity.LV*0.1)
            entity.SPD = 20 + int(entity.LV*0.01)
        else:
            print("ReCalc未対応")
    #状態効果の付与 エフェクトのターン経過は攻撃が終わった後
    def calc_effect(self,entity):
        #他のエフェクトと重複して効果がヤバいことにならないようにするため
        #事前にバックアップを取っておく
        entity_B = Entity()
        entity_B.ATK = entity.ATK
        entity_B.MAT = entity.MAT
        entity_B.DEF = entity.DEF
        entity_B.MDF = entity.MDF
        entity_B.LUK = entity.LUK
        entity_B.SPD = entity.SPD
        for i,Skill in enumerate(entity.Effects):
            #攻昇
            if Skill["TYPE"] == 0:
                entity.ATK += int((entity_B.ATK*0.1)*Skill["Power"])
            #攻少
            elif Skill["TYPE"] == 1:
                entity.ATK -= int((entity_B.ATK*0.1)*Skill["Power"])
            #魔昇
            elif Skill["TYPE"] == 2:
                entity.MAT += int((entity_B.MAT*0.1)*Skill["Power"])
            #魔少
            elif Skill["TYPE"] == 3:
                entity.MAT -= int((entity_B.MAT*0.1)*Skill["Power"])
            #防昇
            elif Skill["TYPE"] == 4:
                entity.DEF += int((entity_B.DEF*0.1)*Skill["Power"])
                entity.MDF += int((entity_B.MDF*0.1)*Skill["Power"])
            #防少
            elif Skill["TYPE"] == 5:
                entity.DEF -= int((entity_B.DEF*0.1)*Skill["Power"])
                entity.MDF -= int((entity_B.MDF*0.1)*Skill["Power"])
            #運昇
            elif Skill["TYPE"] == 6:
                entity.LUK += int((entity_B.LUK*0.1)*Skill["Power"])
            #運少
            elif Skill["TYPE"] == 7:
                entity.LUK -= int((entity_B.LUK*0.1)*Skill["Power"])
            #俊足
            elif Skill["TYPE"] == 8:
                entity.SPD += int((entity_B.SPD*0.1)*Skill["Power"])
            #鈍足
            elif Skill["TYPE"] == 9:
                entity.SPD -= int((entity_B.SPD*0.1)*Skill["Power"])
            #回復
            elif Skill["TYPE"] == 10:
                entity.HP += int((entity_B.HP*0.2)*Skill["Power"])
                print("%sは%s回復した"%(entity.name,int((entity_B.HP*0.2)*Skill["Power"])))
            #気合
            elif Skill["TYPE"] == 11:
                entity.Effects[i]["Turn"] = 2
                entity.MAT += int((entity_B.MAT*0.2)*Skill["Power"])
                entity.ATK += int((entity_B.ATK*0.2)*Skill["Power"])
            #瀕死
            elif Skill["TYPE"] == 12:
                entity.LUK = 100
                entity.ATK += int(entity_B.ATK*0.3)
                entity.DEF = 0
            elif Skill["TYPE"] == 13:
                pass
            elif Skill["TYPE"] == 14:
                pass
            elif Skill["TYPE"] == 15:
                pass
            elif Skill["TYPE"] == 16:
                pass
            elif Skill["TYPE"] == 17:
                pass
            elif Skill["TYPE"] == 18:
                pass
            elif Skill["TYPE"] == 19:
                pass
            elif Skill["TYPE"] == 20:
                pass
            else:
                print("未実装のエフェクトが呼ばれました")
        
    #状態効果によるアップ/ダウン (攻撃前の処理)(未使用)
    def process_effects_before(self,entity):
        if entity.Effects != {}:
            for s in entity.Effects:
                pass
    #状態効果によるアップ/ダウン (攻撃後の処理)
    def process_effects_after(self,entity):
        if entity.Effects != {}:
            for s in entity.Effects:
                s["Turn"] -= 1
                if s["Turn"] < 1:
                    print("%sの効果が切れたようだ"%(effect_dict[s["TYPE"]]))
                    entity.Effects.remove(s)
                    self.recalc(entity)
                    self.calc_effect(entity)
    #スキル処理
    def skill(self,skill,player):
        if "Effect" in user_skill_dict[skill]:
            if user_skill_dict[skill]["Entire"]:
                if user_skill_dict[skill]["TYPE"] not in [11]:
                    self.effect_attack(player,to=Enemy,Skill=user_skill_dict[skill],All=True)
                else:
                    self.effect_attack(player,to=Player,Skill=user_skill_dict[skill],All=True)
            else:
                if user_skill_dict[skill]["TYPE"] not in [11]:
                    self.effect_attack(player,Skill=user_skill_dict[skill],All=False)
                else:
                    self.effect_attack(player,to=player,Skill=user_skill_dict[skill],All=False)
        else:
            if user_skill_dict[skill]["Entire"]:
                self.magic_attack_all(player,skill,Enemy)
            else:
                at_to = self.process_select_to(Enemy)
                self.magic_attack(player,at_to,player.Skills[skill])
    #ダメージ計算機
    def gen_damage(self,_from,to,type=1,Skill=None): 
        if Skill == None: Skill = {"TYPE":_from.TYPE}
        if type == 1:
            if "MAT" in Skill:
                damage = int(((_from.MAT+Skill["MAT"])*(1+(random.randint(0,3)/10))) - (to.MDF * (random.randint(3,6)/10)))
            else:
                damage = int(((_from.ATK+Skill["ATK"])*(1+(random.randint(0,3)/10))) - (to.DEF * (random.randint(3,6)/10)))
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
            stop = False
            for data in to.Effects:
                if data["TYPE"] == 11:
                    stop = True
                    break
            if stop:
                to.HP = 1
            else:
                print("%sは倒れた"%(to.name))
                self.game_check()
        elif to.HP < 5:
            Noskip = True
            for e in to.Effects:
                if e["TYPE"] == 12:
                    Noskip = False
                    break
            if Noskip:
                to.Effects.append({"TYPE":12,"Power":100,"Turn":10})
                self.recalc(to)
                self.calc_effect(to)
                print("%sは瀕死状態になった"%(to.name))
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
    #エフェクトを追加する
    def effect_attack(self,_from,to=None,Skill=None,All=False):
        print("%sの攻撃"%(_from.name))
        print("<スキル> %s"%(Skill["Name"]))
        if All:
            for en in self.entities:
                if type(en) == to:
                    if Skill["TYPE"] not in en.Deny:
                        if random.randint(1,100) < Skill["HIT"]:
                            data = {"TYPE":Skill["TYPE"],"Turn":Skill["Power"]+random.randint(2,4),"Power":Skill["Power"]}
                            en.Effects.append(data)
                            self.recalc(en)
                            self.calc_effect(en)
                            print("%sは%s状態になった"%(en.name,effect_dict[Skill["TYPE"]]))
                        else:
                            print("%sの攻撃は外れた"%(_from.name))
                    else:
                        print("%sには効果がないようだ..."%(en.name))
        else:
            if Skill["TYPE"] not in to.Deny:
                if random.randint(1,100) < Skill["HIT"]:
                    data = {"TYPE":Skill["TYPE"],"Turn":Skill["Power"]+2,"Power":Skill["Power"]}
                    to.Effects.append(data)
                    self.recalc(to)
                    self.calc_effect(to)
                    print("%sは%s状態になった"%(to.name,effect_dict[Skill["TYPE"]]))
                else:
                    print("%sの攻撃は外れた"%(_from.name))
            else:
                print("%sには効果がないようだ..."%(to.name))
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
    #状態異常一覧を返す
    def gen_effects_ls(self,entity):
        text = "["
        for effect in entity.Effects:
            text += effect_dict[effect["TYPE"]] + " "
        text = text[:len(text)-1] +"]"
        if text == "]": text = "[ ]"
        return text
    #状態を見る 
    def show_status(self):
        print("")
        texts = ["/// 味方 ///"]
        for entity in self.entities:
            if type(entity) == Player:
                status_bar = self.gen_effects_ls(entity)
                texts.append("  [Lv%s] %s %s/%s %s/%s %s"%(entity.LV,entity.name,entity.HP,entity.MAX_HP,entity.MP,entity.MAX_MP,status_bar))
        texts.append("/// 敵 ///")
        for entity in self.entities:
            if type(entity) == Enemy:
                status_bar = self.gen_effects_ls(entity)
                texts.append("  [Lv%s] %s %s/%s %s"%(entity.LV,entity.name,entity.HP,entity.MAX_HP,status_bar))
        for t in texts:
            print(t)

#ユーザーの入力に応じてコマンドを実行する
class Commands(Battle):
    def help(self,player):
        print (cmd_dict.keys())
    def kougeki(self,player):
        at_to = self.process_select_to(Enemy)
        self.attack(player,at_to)
    def bougyo(self,player):
        self.defense()
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
            if "Effect" not in player.Skills[skill]:
                print("%s : COST %s TYPE:%s\n %s"%(skill,player.Skills[skill]["Cost"],type_dict[player.Skills[skill]["TYPE"]],player.Skills[skill]["About"]))
            else:
                print("%s : COST %s TYPE:特殊\n %s"%(skill,player.Skills[skill]["Cost"],player.Skills[skill]["About"]))
        print("backで戻る")
        bye = False
        while True:
            if bye: break
            line = input("> ")
            cc = self.choicer(line,list(player.Skills.keys()))
            if line == "back":
                bye = True
                break
            if cc != False:
                if player.MP >= player.Skills[cc]["Cost"]:
                    player.MP -= player.Skills[cc]["Cost"]
                    self.skill(cc,player)
                    bye = True
                else:
                    print("MPが足りません")
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
        entities.append(Player("Domao",20,user_skill_dict))
        entities.append(Enemy("NicoNico",random.randint(10,21)))
        super().__init__(entities)
    #ゲーム終了確認
    def game_check(self):
        #HP0のエンティティを削除する
        self.entities = [e for e in self.entities if e.HP > 0]
        self.sort_by_speed()
        self.gen_IDs()
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