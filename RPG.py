import random,sys,time
import ujson as json
from collections import OrderedDict

'''
<属性>
Type = 0/無属性 1/水 2/炎 3/風 4/土 5/闇 6/光

<EType>
1 = プレイヤー
2 = エネミー

<Entity型>
new_entityに移動

<Battle型>
BattleField.txtに移動

<処理のつなぎ方>
Entity型か Battle型 を 投げ回す

余計な処理はしないはずだから
self.rpgdata[msg._from]["Stats"]["Battle"]
をそのまま投げてOK
'''

#メッセージ型のダミー
class Message(object):
    def __init__(self,_from,to,text):
        self.to = "個チャ"
        self._from = "ユーザー"
        self.text = text
        self.toType = 0
#クライアント型のダミー
class Client(object):
    def sendMessage(self,to,text):
        print("%s > %s"%(to,text))

#RPGクラス内でのみ使う(可読性確保)
class B_Entity(object):
    #新規Entityの作成
    def new_entity(self,type=0,name="NicoNico",level=1,drops=None,mid=None):
        #敵型
        if type == 2:
            if name in enemy_dict:
                e = enemy_dict[name]
                e["EType"] = 2
                if "Effects" not in e: e["Effects"] = []
                if "Deny" not in e: e["Deny"] = []
                if "CHG" not in e: e["CHG"] = 1 
                if "MAX_CHG" not in e: e["MAX_CHG"] = 1
                if "Charges" not in e: e["Charges"] = {}
                if "Skills" not in e: raise ValueError
                if "Percents" not in e: raise ValueError
                e["HP"] = e["MAX_HP"] = int(e["HP"]*(1+((level/5))))
                e["ATK"] = int(e["ATK"]*(1+(random.randint(1,1)/10))*(1+((level/5))))
                if drops != None: e["Drops"] = drops
            else:
                raise NameError
        #プレイヤー型
        elif type == 1:
            e = {
                "Name":"UNKNOWN",
                "LV":1,
                "TYPE":0,
                "HP":50,
                "MAX_HP":50,
                "MP":30,
                "MAX_MP":30,
                "ATK":10,
                "MAT":10,
                "DEF":10,
                "MDF":10,
                "LUK":10,
                "SPD":20,
                "Skills":{},
                "Deny":[],
                "Effects":[]
            }
            if name in rpgdata:
                e["EType"] = 1
                lv = rpgdata[mid][name]["LV"]
                e["HP"] = e["MAX_HP"] =  int(50 + lv*0.75)
                e["MP"] = e["MAX_MP"] =  int(30 + lv*0.5)
                e["ATK"] = int(10 + lv*0.2)
                e["MAT"] = int(10 + lv*0.15)
                e["SPD"] = int(20 + lv*0.1)
                e["Skills"] = rpgdata[mid][name]["Skills"]
                e["Deny"] = rpgdata[mid][name]["Deny"]
        return e
    #エンティティにIDを付け直す
    def reid_entities(self,battle):
        es = battle["Entities"]
        #0=その他 1=プレイヤー 2=敵
        ns = [0,1,1]
        battle["Entities"] = OrderedDict()
        for e in es:
            if e["EType"] == 1:
                battle["Entities"]["p"+str(ns[1])] = e
                ns[1] += 1
            elif e["EType"] == 2:
                battle["Entities"]["e"+str(ns[2])] = e
                ns[2] += 1
            else:
                battle["Entities"]["o"+str(ns[0])] = e
                ns[0] += 1
        return battle
    #エンティティをスピードでソートする
    def sort_entities(self,battle):
        battle["Entities"] = sorted(battle["Entities"],reverse=True,key=lambda entity: entity["SPD"])
        return battle
    #ATK等の初期化(チャージや現在HPは弄らない)
    def reset_entity(self,ID,battle):
        if ID not in battle["Entities"]: raise ValueError
        entity = battle["Entities"][ID]
        if entity["EType"] == 2:
            dic = enemy_dict[entity["Name"]]
            entity["MAX_HP"] = dic["HP"]
            entity["MAX_MP"] = dic["MP"]
            entity["TYPE"] = dic["TYPE"]
            entity["ATK"] = dic["ATK"]
            entity["MAT"] = dic["MAT"]
            entity["DEF"] = dic["DEF"]
            entity["MDF"] = dic["MDF"]
            entity["SPD"] = dic["SPD"]
            entity["LUK"] = dic["LUK"]
            #レベルに合わせてATKを弄る
            entity["MAX_HP"] = int(dic["HP"]*(1+((entity["LV"]/5))))
            entity["ATK"] = int(entity["ATK"]*(1+(random.randint(1,1)/10))*(1+((entity["LV"]/5))))
        elif entity["EType"] == 1:
            #ユーザーデータが確立したら修正すること!
            entity["MAX_HP"] = 50 + int(entity["LV"]*0.5)
            entity["MAX_MP"] = 30 + int(entity["LV"]*0.5)
            entity["ATK"] = 10 + int(entity["LV"]*0.15)
            entity["MAT"] = 10 + int(entity["LV"]*0.1)
            entity["DEF"] = 1 + int(entity["LV"]*0.1)
            entity["SPD"] = 20 + int(entity["LV"]*0.01)
        else:
            raise ValueError
        battle["Entities"][ID] = entity
        return battle
    #効果を適用する
    def reset_entity_effect(self,ID,msg):
        battle = self.rpgdata[msg._from]["Stats"]["Battle"]
        e = battle["Entities"][ID]
        for i,s in enumerate(e["Effects"]):
            #攻昇
            if s["TYPE"] == 0:
                battle["Entities"][ID]["ATK"] += int((e["ATK"]*0.1)*s["Power"])
            #攻少
            elif s["TYPE"] == 1:
                battle["Entities"][ID]["ATK"] -= int((e["ATK"]*0.1)*s["Power"])
            #魔昇
            elif s["TYPE"] == 2:
                battle["Entities"][ID]["MAT"] += int((e["MAT"]*0.1)*s["Power"])
            #魔少
            elif s["TYPE"] == 3:
                battle["Entities"][ID]["MAT"] -= int((e["MAT"]*0.1)*s["Power"])
            #防昇
            elif s["TYPE"] == 4:
                battle["Entities"][ID]["DEF"] += int((e["DEF"]*0.1)*s["Power"])
                battle["Entities"][ID]["MDF"] += int((e["MDF"]*0.1)*s["Power"])
            #防少
            elif s["TYPE"] == 5:
                battle["Entities"][ID]["DEF"] -= int((e["DEF"]*0.1)*s["Power"])
                battle["Entities"][ID]["MDF"] -= int((e["MDF"]*0.1)*s["Power"])
            #運昇
            elif s["TYPE"] == 6:
                battle["Entities"][ID]["LUK"] += int((e["LUK"]*0.1)*s["Power"])
            #運少
            elif s["TYPE"] == 7:
                battle["Entities"][ID]["LUK"] -= int((e["LUK"]*0.1)*s["Power"])
            #俊足
            elif s["TYPE"] == 8:
                battle["Entities"][ID]["SPD"] += int((e["SPD"]*0.1)*s["Power"])
            #鈍足
            elif s["TYPE"] == 9:
                battle["Entities"][ID]["SPD"] -= int((e["SPD"]*0.1)*s["Power"])
            #回復
            elif s["TYPE"] == 10:
                battle["Entities"][ID]["HP"] += int((e["HP"]*0.2)*s["Power"])
                print("%sは%s回復した"%(battle["Entities"][ID]["Name"],int((e["HP"]*0.2)*s["Power"])))
            #気合
            elif s["TYPE"] == 11:
                battle["Entities"][ID]["Effects"][i]["Turn"] = 2
                battle["Entities"][ID]["MAT"] += int((e["MAT"]*0.2)*s["Power"])
                battle["Entities"][ID]["ATK"] += int((e["ATK"]*0.2)*s["Power"])
            #瀕死
            elif s["TYPE"] == 12:
                battle["Entities"][ID]["LUK"] = 100
                battle["Entities"][ID]["ATK"] += int(e["ATK"]*0.3)
                battle["Entities"][ID]["DEF"] = 0
            elif s["TYPE"] == 13:
                pass
            elif s["TYPE"] == 14:
                pass
            elif s["TYPE"] == 15:
                pass
            elif s["TYPE"] == 16:
                pass
            elif s["TYPE"] == 17:
                pass
            elif s["TYPE"] == 18:
                pass
            elif s["TYPE"] == 19:
                pass
            elif s["TYPE"] == 20:
                pass
            else:
                print("未実装のエフェクトが呼ばれました")
        self.rpgdata[msg._from]["Stats"]["Battle"] = battle
    #エンティティをIDで取る
    def get_entity(self,ID,battle):
        if ID not in battle["Entities"]: raise ValueError
        return battle["Entities"][ID]
    #エンティティをIDから消す
    def remove_entity(self,ID,battle):
        if ID not in battle["Entities"]: raise ValueError
        del battle["Entites"][ID]
        reid_entities(battle)
        sort_entities(battle)
        return battle
    #エンティティ一覧を取る
    def gen_enemys(self,battle):
        return [e for e in battle["Entities"] if e["EType"] == 2]
    def gen_players(self,battle):
        return [e for e in battle["Entities"] if e["EType"] == 1]    
class B_Utility(object):
    #ひらがなか数字を使いリストから選ぶ(choice_dictは事前に準備)
    def choicer(self,text="1",ls=["A","B","C"]):
        vl = choice_dict.values()
        vls = [str(i) for i in vls]
        #あ～ん なら 数値を返す
        if text in choice_dict:
            if len(ls) >= choice_dict[text]-1:
                return ls[choice_dict[text]-1]
        #数字が入ってるなら
        elif text in vls:
            if len(ls) >= int(text)-1:
                return ls[int(text)-1]
        #項目自体なら
        elif text in ls:
            return text
        return None
    #選択肢一覧を表示する
    def choice_list(self,ls=["A","B","C"],kana=True):
        if kana:
            kanas = list(choice_dict.keys())
            return ["%s : %s"%(kanas[i],t) for i,t in enumerate(ls)]
        else:
            return ["%s : %s"%(i+1,t) for i,t in enumerate(ls)]
    #状態異常一覧を返す
    def effect_list(self,entity):
        return [effect_dict[e["TYPE"]] for e in entity["Effects"]]
    #状態を返す
    def status_list(self,battle):
        entities = battle["Entities"]
        #0=プレイヤー 1=敵
        texts = [[],[]]
        for entity in entities:
            if entity["EType"] == 1:
                texts[0].append("  [Lv%s] %s %s/%s %s/%s %s"%(entity["LV"],entity["Name"],entity["HP"],entity["MAX_HP"],entity["MP"],entity["MAX_MP"],"["+" ".join(self.effect_list(entity))+" ]"))
            elif entity["EType"] == 2:
                texts[1].append("  [Lv%s] %s %s/%s %s"%(entity["LV"],entity["Name"],entity["HP"],entity["MAX_HP"],"["+" ".join(self.effect_list(entity))+" ]"))
        return texts
    #辞書からランダムに選んで要素を返す
    def pick_by_per(self,dic):
        if "Auto" in dic:
            ls = list(dic.keys())
            ls.remove("Auto")
            return dic[random.choice(ls)]
        else:
            num = random.randint(1,100)
            for key in dic:
                if num <= key: return dic[key]
            raise ValueError 
class B_Process(object):
    #新規バトルの作成
    def new_battle(self,wave,quest,player):
        b = OrderedDict()
        b["Turn"] = 1
        b["I_Turn"] = 0
        b["Got"] = {1:0,2:0,3:0}
        b["Entities"] = OrderedDict()
        i = [1,1]
        for m in quest["Waves"][wave]:
            e = new_entity(2,m["Name"],m["LV"],drops=m["Drops"])
            e["EType"] = 2
            b["Entities"]["e"+str(i[0])] = e
            i[0] += 1
        for p in player:
            e = new_entity(1,p["Name"],p["LV"],mid=p["mid"])
            e["EType"] = 1
            b["Entities"]["p"+str(i[1])] = e
            i[1] += 1
        return b
    #ターン処理
    def process_turn(self,battle):
        entity = battle["Entities"][battle["I_Turn"]]
        if entity["EType"] == 2:
            entity = self.process_enemy(entity)
        elif entity["EType"] == 1:
            entity = self.process_player(entity)
        entity = self.process_effects_after(entity)
        battle["Entities"][battle["I_Turn"]] = entity
        battle["I_Turn"] += 1
        if battle["I_Turn"] >= len(battle["Entities"]):
            battle["I_Turn"] = 0
            battle["Turn"] += 1
        return battle
    #敵の処理 (プレイヤーに対して攻撃する)
    def process_enemy(self,enemy,battle):
        enemy = self.process_effects_before(enemy)
        enemy["CHG"] += 1
        #攻撃先は完全ランダム
        player = random.choice(self.gen_players())
        #スキルを選ぶ
        if enemy["CHG"] not in enemy["Charges"]:
            skill_dic = self.pick_by_per(enemy.Percents)
            skill = enemy.Skills[skill_dic][self.pick_by_per(enemy.Skills[skill_dic])]
            skill["S_Type"] = skill_dic
        else:
            skill = enemy["Charges"][enemy["CHG"]][random.choice(list(enemy["Charges"][enemy.CHG].keys()))]
        #スキルは敵の通常データ+スキルの固有データ
        if "MAT" in skill: skill["MAT"] += enemy["MAT"]
        if "ATK" in skill: skill["ATK"] += enemy["ATK"]
        if enemy["CHG"] not in enemy["Charges"]:
            #要修正 battleはここで使う
            if skill["S_Type"] == "Defaults":
                if skill["Entire"]: self.attack_all(enemy,Player)
                else: self.attack(enemy,player,skill)
            elif skill["S_Type"] == "Specials":
                if skill["Entire"]: self.magic_attack_all(enemy,skill,Player)
                else: self.magic_attack(enemy,player,skill)
        else:
            #要修正
            if skill["Entire"]: self.magic_attack_all(enemy,skill,Player)
            else: self.magic_attack(enemy,player,skill)
        if enemy["CHG"] > enemy["MAX_CHG"]: enemy["CHG"] = 0
        return enemy
    #プレイヤーの処理(コマンドを入力させて実行する)
    def process_player(self,player):
        self.show_status()
        self.cl.sendMessage("%sはどうする?"%(player.name))
    #攻撃先を選ぶ (entityを返す) かーきーなーおーせー
    def process_select_to(self,type):
        pass
    #状態効果によるアップ/ダウン (攻撃前の処理)(未使用)
    def process_effects_before(self,entity):
        if entity.Effects != {}:
            for s in entity.Effects:
                pass
        return entity
    #状態効果によるアップ/ダウン (攻撃後の処理)
    def process_effects_after(self,entity):
        if entity.Effects != {}:
            for s in entity.Effects:
                s["Turn"] -= 1
                if s["Turn"] < 1:
                    print("%sの効果が切れたようだ"%(effect_dict[s["TYPE"]]))
                    entity = entity.Effects.remove(s)
                    entity = self.reset_entity(entity)
                    entity = self.effect(entity)
        return entity
    #フィールドを整える
    def process_field(self,battle):
        #HP0のエンティティを削除する
        ens = battle["Entities"]
        battle["Entities"] = [e for e in ens if e["HP"] > 0]
        battle = self.reid_entities(self.sort_entities(battle))
        return battle
    #勝敗判定
    def process_check(self,battle):
        #敵がいなくなったら勝ち
        if len(self.gen_enemys(battle)) == 0:
            print("GAME CLEAR")
            return 1
        #プレイヤーがいなくなったら負け
        elif len(self.gen_players(battle)) == 0:
            print("GAME OVER")
            return -1
        return 0
            
#戦闘処理
class Battle(object):
    #アイテムコマンドが飛んできた
    def Item(self,ID,msg):
        pass
    #スキルコマンドが飛んできた
    def Skill(self,skill,player):
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
        return battle
    #防御コマンドが飛んできた
    def Defense(self):
        #エフェクトを使うように書き直す
        pass
    #ダメージ計算
    def gen_damage(self,_from,to,type=1,Skill=None): 
        if Skill == None: Skill = {"TYPE":_from["TYPE"]}
        if type == 1:
            if "MAT" in Skill:
                damage = int(((_from["MAT"]+Skill["MAT"])*(1+(random.randint(0,3)/10))) - (to["MDF"] * (random.randint(3,6)/10)))
            else:
                damage = int(((_from["ATK"]+Skill["ATK"])*(1+(random.randint(0,3)/10))) - (to["DEF"] * (random.randint(3,6)/10)))
        else:
            damage = int((_from["ATK"]*(1+(random.randint(0,3)/10))) - (to["DEF"] * (random.randint(3,6)/10)))
        #クリティカル(通常30%)が出たら 1.2~1.3倍のダメージ
        if random.randint(1,100) < _from["LUK"] + 20:
            damage = int(damage*1+(random.randint(2,3)/10))
            print(" クリティカル！")
        #Type= 0/無属性 1/水 2/炎 3/風 4/土 5/闇 6/光
        #相性が良ければ 1.3~1.5倍のダメージ
        if (Skill["TYPE"] == 1 and to["TYPE"] == 2
        or Skill["TYPE"] == 2 and to["TYPE"] == 3
        or Skill["TYPE"] == 3 and to["TYPE"] == 4
        or Skill["TYPE"] == 4 and to["TYPE"] == 1
        or Skill["TYPE"] == 5 and to["TYPE"] == 6
        or Skill["TYPE"] == 6 and to["TYPE"] == 5):
            damage = int(damage * (1+(random.randint(4,5)/10)))
            print(" あいしょうはばつぐんだ！")
        #相性が悪ければ 0.4~0.6倍のダメージ
        if (Skill["TYPE"] == 1 and to["TYPE"] == 4
        or Skill["TYPE"] == 4 and to["TYPE"] == 3
        or Skill["TYPE"] == 3 and to["TYPE"] == 2
        or Skill["TYPE"] == 2 and to["TYPE"] == 1):
            damage = int(damage * (random.randint(4,6)/10))
            print(" こうかはいまひとつのようだ...")
        return damage
    def get_damage(self,ID,damage,battle):
        to = battle["Entities"][ID]
        if damage <= 0: damage = 0
        to["HP"] -= damage
        print("%sは%sのダメージを受けた"%(to["Name"],damage))
        if to["HP"] <= 0:
            chk = [e for e in to["Effects"] if e["TYPE"] == 11]
            if chk != []:
                to.HP = 1
            else:
                print("%sは倒れた"%(to["name"]))
                #self.game_check()
        elif to.HP < 5:
            chk = [e["TYPE"] for e in to["Effects"] if e["TYPE"] == 12]
            if chk != [12]:
                to["Effects"].append({"TYPE":12,"Power":100,"Turn":10})
                to = self.reset_entity(to)
                to = self.effect(ID,battle)
                print("%sは瀕死状態になった"%(to["Name"]))
        return battle
    #通常攻撃(プレイヤーも敵も通る)
    def attack(self,_from,to):
        print("%sの攻撃"%(_from["Name"]))
        print("<通常> %sの剣"%(_from["Name"]))
        #ダメージ計算して、ダメージを受ける
        damage = self.gen_damage(_from,to,0)
        battle = self.get_damage(to,damage)
        return battle
    def attack_all(self,_from,toType=1):
        print("%sの攻撃"%(_from.name))
        for entity in battle["Entities"]:
            if type(entity) == toType:
                damage = self.gen_damage(_from,entity,0)
                battle = self.get_damage(entity,damage,battle)
        return battle
    #効果攻撃(プレイヤーも敵も通る)
    def effect_attack(self,_from,to,Skill)
        print("%sの攻撃"%(_from.name))
        print("<スキル> %s"%(Skill["Name"]))
        if Skill["TYPE"] not in to.Deny:
            if random.randint(1,100) < Skill["HIT"]:
                data = {"TYPE":Skill["TYPE"],"Turn":Skill["Power"]+2,"Power":Skill["Power"]}
                to["Effects"].append(data)
                to = self.entity_reset(to)
                to = self.effect(to)
                print("%sは%s状態になった"%(to.name,effect_dict[Skill["TYPE"]]))
            else:
                print("%sの攻撃は外れた"%(_from.name))
        else:
            print("%sには効果がないようだ..."%(to.name))
    def effect_attack_all(self,_from,Skill,toType=1):
        print("%sの攻撃"%(_from.name))
        print("<スキル> %s"%(Skill["Name"]))
        ens = battle["Entities"]
        for en in ens:
            if ens[en]["EType"] == toType:
                if Skill["TYPE"] not in en["Deny"]:
                    if random.randint(1,100) < Skill["HIT"]:
                        data = {"TYPE":Skill["TYPE"],"Turn":Skill["Power"]+random.randint(2,4),"Power":Skill["Power"]}
                        ens[en]["Effects"].append(data)
                        en = self.entity_reset(en)
                        en = self.effect(en)
                        print("%sは%s状態になった"%(en["Name"],effect_dict[Skill["TYPE"]]))
                        battle["Entities"][en] = en
                    else:
                        print("%sの攻撃は外れた"%(_from["Name"]))
                else:
                    print("%sには効果がないようだ..."%(en["Name"]))
        return battle
    #魔法攻撃(プレイヤーも敵も通る)
    def magic_attack(self,_from,to,Skill,battle):
        print("%sの攻撃"%(_from["Name"]))
        print("<スキル> %s"%(Skill["Name"]))
        #命中率的な設定
        if random.randint(1,100) < Skill["HIT"]:
            #ダメージ計算して♡
            damage = self.gen_damage(_from,to,1,Skill)
            battle = self.get_damage(to,damage,battle)
        else:
            print("%sの攻撃は外れた"%(_from.name))
        return battle
    def magic_attack_all(self,_from,Skill,toType=1,battle):
        print("%sの攻撃"%(_from.name))
        print("<スキル> %s"%(Skill["Name"]))
        if random.randint(1,100) < Skill["HIT"]:
            for entity in self.entities:
                if type(entity) == toType:
                    damage = self.gen_damage(_from,entity,1,Skill)
                    battle = self.get_damage(entity,damage,battle)
        else:
            print(" %sの攻撃は外れた"%(_from["Name"]))
        return battle

#ゲーム本体(Cmdからインポートで呼ぶ) 
class RPG():
    #本来は"継承先(cmd)"で読み込む
    cl = Client()
    with open("EnemyData.json") as f:
        enemy_dict = json.loads(f.read(), object_pairs_hook=OrderedDict)
    with open("SkillData.json") as f:
        skill_dict = json.loads(f.read(), object_pairs_hook=OrderedDict)
    with open("QuestData.json") as f:
        #Monsters -> 編成ID -> ウェーブID -> 敵一覧
        quest_dict = json.loads(f.read(), object_pairs_hook=OrderedDict)
    with open("SaveData.json") as f:
        rpgdata = json.loads(f.read(), object_pairs_hook=OrderedDict)     
    battle_commands = ["攻撃","魔法","防御","アイテム","逃走"]
    choice_dict = {
        'あ':1, 'い':2, 'う':3, 'え':4, 'お':5,
        'か':6, 'き':7, 'く':8, 'け':9, 'こ':10,
        'さ':11, 'し':12, 'す':13, 'せ':14, 'そ':15,
        'た':16, 'ち':17, 'つ':18, 'て':19, 'と':20,
        'な':21, 'に':22, 'ぬ':23, 'ね':24, 'の':25,
        'は':26, 'ひ':27, 'ふ':28, 'へ':29, 'ほ':30,
        'ま':31, 'み':32, 'む':33, 'め':34, 'も':35,
        'や':36, 'ゆ':37, 'よ':38,
        'ら':39, 'り':40, 'る':41, 'れ':42, 'ろ':43,
        'わ':44, 'を':45, 'ん':46
    }
    #状態で分岐
    def process_rpg(self,msg):
        if msg._from in self.rpgdata:
            if self.rpgdata[msg._from]["Pause"] == False:
                if msg.text == "中断":
                    self.rpgdata[msg._from]["Pause"] = True
                    self.userdata[msg._from]["State"]["InRPG"] = False
                    self.cl.sendMessage("～Thank you for playing!～\nまた来てくださいね! (*^-^*)")
                else:
                    data = rpgdata[msg._from]
                    stat = data["Stats"]
                    elif stat["Screen"] == "Home": self.process_home(msg,data,stat)
                    elif stat["Screen"] == "Shop": self.process_shop(msg,data,stat)
                    elif stat["Screen"] == "Dungeon": self.process_dungeon(msg,data,stat)
                    elif stat["Screen"] == "Battle": self.process_battle(msg,data,stat)
                    else: raise ValueError
            else:
                self.cl.sendMessage("社畜娘RPGへようこそ🌎")
                self.process_rpg(msg)
        else:
            self.cl.sendMessage("社畜娘RPGへようこそ🌎")
            self.process_gate(msg)
    def process_gate(msg):
        self.cl.sendMessage('アカウントがないみたいです!\n新規登録しても大丈夫でしょうか？\n\n"はい" または "あ"\nで登録\n"いいえ" または "い" でキャンセルします')
        self.choice_list(["はい","いいえ"])
        self.cl.sendMessage()
    def process_shop(msg,data,stat):
        pass
    def process_dungeon(msg,data,stat):
        pass
    def process_battle(self,msg,data,stat):
        #攻撃先の選択
        if stat["Battle"]["Selecting"]:
            #攻撃
            if stat["Battle"]["MenuID"] == 0:
                self.rpgdata[msg._from]["Stats"]["Battle"]["Selecting"] = False
            #魔法
            elif stat["Battle"]["MenuID"] == 1:
                self.rpgdata[msg._from]["Stats"]["Battle"]["Selecting"] = False
        else:
            #コマンドの選択
            if stat["Battle"]["MenuID"] == 0:
                #有効なコマンドか確認
                choice = self.choicer(msg.text,self.commands)
                if choice != None:
                    if choice == "攻撃":
                        self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 0
                        enemys = self.gen_enemys(stat["Battle"]["Entities"])
                        if len(enemys) == 1:
                            self.rpgdata[msg._from]["Stats"]["Battle"] = self.attack(stat["Battle"])
                        else:
                            self.cl.sendMessage("攻撃先は?"+"\n".join(choice_list(enemys))+"\n も : 戻る")
                            self.rpgdata[msg._from]["Stats"]["Battle"]["Selecting"] = True
                    elif choice == "魔法":
                        self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 1
                        self.cl.sendMessage("どれを使用しますか?"+"\n".join(choice_list(data["Skills"]))+"\n も : 戻る")
                    elif choice == "防御":
                        self.rpgdata[msg._from]["Battle"] = self.defense(stat["Battle"])
                    elif choice == "アイテム":
                        self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 1
                        self.cl.sendMessage("どれを使用しますか?"+"\n".join(choice_list(data["Skills"]))+"\n も : 戻る")
                    elif choice == "逃走":
                        self.rpgdata[msg._from]["Battle"] = self.escape(stat["Battle"])
                elif msg.toType == 0:
                    self.cl.sendMessage("コマンドが正しくありません")
            #スキルの選択
            elif stat["Battle"]["MenuID"] == 1:
                #も は 戻る固定
                if msg.text != "も":
                    #有効なスキル名か確認
                    choice = self.choicer(msg.text,list(self.rpgdata[msg._from]["Skills"].keys()))
                    if choice != None:
                        self.rpgdata[msg._from]["Stats"]["Battle"] = self.Skill(choice,stat["Battle"])
                else:
                    self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 0
                    #～はどうする？を表示
            #アイテムの選択
            elif stat["Battle"]["MenuID"] == 2:
                #も は 戻る固定
                if msg.text != "も":
                    #有効なアイテムか確認
                    choice = self.choicer(list(self.rpgdata[msg._from]["Inventory"].keys()))
                    if choice != None:
                        self.rpgdata[msg._from]["Stats"]["Battle"] = self.Item(choice,stat["Battle"])
                else:
                    self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 0
                    #～はどうする？を表示
            #IDが謎
            else:
                raise ValueError

game = RPG()
while True:
    game.process_rpg(Message(text=input('< ')))