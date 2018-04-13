from collections import OrderedDict
from copy import deepcopy
import json,random

#RPGクラス内でのみ使う(可読性確保)
class B_Entity(object):
    #新規Entityの作成
    def new_entity(self,type=0,name="NicoNico",level=1,drops=[],mid=None):
        #敵型
        if type == 2:
            if name in self.enemy_dict:
                e = deepcopy(self.enemy_dict[name])
                e["Name"] = name
                e["EType"] = 2
                if "Effects" not in e: e["Effects"] = []
                if "Deny" not in e: e["Deny"] = []
                if "CHG" not in e: e["CHG"] = 1 
                if "MAX_CHG" not in e: e["MAX_CHG"] = 1
                if "Charges" not in e: e["Charges"] = {}
                if "Skills" not in e: raise ValueError
                if "Percents" not in e: raise ValueError
                if len(level) == 1:
                    level = level[0]
                else:
                    level = random.randint(level[0],level[1])
                e["LV"] = level
                e["HP"] = e["MAX_HP"] = int(e["HP"]*(1+((level/5))))
                e["ATK"] = int(e["ATK"]*(1+(random.randint(1,1)/10))*(1+((level/5))))
                e["Drops"] = drops
            else:
                raise NameError
        #プレイヤー型
        elif type == 1:
            e = OrderedDict({
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
            })
            e["EType"] = 1
            data = self.rpgdata[mid]
            lv = data["Level"]
            e["Name"] = data["Name"]
            e["HP"] = e["MAX_HP"] =  int(50 + lv*0.75)
            e["MP"] = e["MAX_MP"] =  int(30 + lv*0.5)
            e["ATK"] = int(10 + lv*0.2)
            e["MAT"] = int(10 + lv*0.15)
            e["SPD"] = int(20 + lv*0.1)
            e["Skills"] = self.rpgdata[mid]["Skills"]
            #e["Deny"] = RPG.rpgdata[mid]["Deny"]
        return e
    #エンティティにIDを付け直す
    def reid_entities(self,battle):
        es = deepcopy(battle["Entities"])
        #0=その他 1=プレイヤー 2=敵
        ns = [0,1,1]
        for e in es:
            if es[e]["EType"] == 1:
                battle["Entities"]["p"+str(ns[1])] = es[e]
                ns[1] += 1
            elif es[e]["EType"] == 2:
                battle["Entities"]["e"+str(ns[2])] = es[e]
                ns[2] += 1
            else:
                battle["Entities"]["o"+str(ns[0])] = es[e]
                ns[0] += 1
        return battle
    #エンティティをスピードでソートする
    def sort_entities(self,battle):
        b = deepcopy(battle["Entities"])
        battle["Entities"] = OrderedDict()
        add = sorted(b,reverse=True,key=lambda e: b[e]["SPD"])
        for a in add:
            battle["Entities"][a] = b[a]
        return battle
    #ATK等の初期化(チャージや現在HPは弄らない)
    def reset_entity(self,entity):
        if entity["EType"] == 2:
            dic = self.enemy_dict[entity["Name"]]
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
            entity["MAX_HP"] = 50 + int(entity["LV"]*0.5)
            entity["MAX_MP"] = 30 + int(entity["LV"]*0.5)
            entity["ATK"] = 10 + int(entity["LV"]*0.15)
            entity["MAT"] = 10 + int(entity["LV"]*0.1)
            entity["DEF"] = 1 + int(entity["LV"]*0.1)
            entity["SPD"] = 20 + int(entity["LV"]*0.01)
        else:
            raise ValueError
        return entity
    #効果を適用する
    def reset_entity_effect(self,entity,msg=None):
        e = deepcopy(entity)
        for i,s in enumerate(e["Effects"]):
            #攻昇
            if s["TYPE"] == 0:
                entity["ATK"] += int((e["ATK"]*0.1)*s["Power"])
            #攻少
            elif s["TYPE"] == 1:
                entity["ATK"] -= int((e["ATK"]*0.1)*s["Power"])
            #魔昇
            elif s["TYPE"] == 2:
                entity["MAT"] += int((e["MAT"]*0.1)*s["Power"])
            #魔少
            elif s["TYPE"] == 3:
                entity["MAT"] -= int((e["MAT"]*0.1)*s["Power"])
            #防昇
            elif s["TYPE"] == 4:
                entity["DEF"] += int((e["DEF"]*0.1)*s["Power"])
                entity["MDF"] += int((e["MDF"]*0.1)*s["Power"])
            #防少
            elif s["TYPE"] == 5:
                entity["DEF"] -= int((e["DEF"]*0.1)*s["Power"])
                entity["MDF"] -= int((e["MDF"]*0.1)*s["Power"])
            #運昇
            elif s["TYPE"] == 6:
                entity["LUK"] += int((e["LUK"]*0.1)*s["Power"])
            #運少
            elif s["TYPE"] == 7:
                entity["LUK"] -= int((e["LUK"]*0.1)*s["Power"])
            #俊足
            elif s["TYPE"] == 8:
                entity["SPD"] += int((e["SPD"]*0.1)*s["Power"])
            #鈍足
            elif s["TYPE"] == 9:
                entity["SPD"] -= int((e["SPD"]*0.1)*s["Power"])
            #回復
            elif s["TYPE"] == 10:
                entity["HP"] += int((e["HP"]*0.2)*s["Power"])
                log("%sは%s回復した"%(entity["Name"],int((e["HP"]*0.2)*s["Power"])),msg)
            #気合
            elif s["TYPE"] == 11:
                entity["Effects"][s]["Turn"] = 2
                entity["MAT"] += int((e["MAT"]*0.2)*s["Power"])
                entity["ATK"] += int((e["ATK"]*0.2)*s["Power"])
            #瀕死
            elif s["TYPE"] == 12:
                entity["LUK"] = 100
                entity["ATK"] += int(e["ATK"]*0.3)
                entity["DEF"] = 0
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
        return entity
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
    def gen_enemys(self,msg):
        ens = self.rpgdata[msg._from]["Stats"]["Battle"]["Entities"]
        return [ens[e] for e in ens if ens[e]["EType"] == 2]
    def gen_players(self,msg):
        ens = self.rpgdata[msg._from]["Stats"]["Battle"]["Entities"]
        return [ens[e] for e in ens if ens[e]["EType"] == 1]
class B_Utility(object):
    #状態をログする
    def log_status(self,msg):
        entities = self.rpgdata[msg._from]["Stats"]["Battle"]["Entities"]
        #0=プレイヤー 1=敵
        texts = [[],[]]
        for entity in entities:
            entity = entities[entity]
            if entity["EType"] == 1:
                texts[0].append("  [Lv%s] %s %s/%s %s/%s %s"%(entity["LV"],entity["Name"],entity["HP"],entity["MAX_HP"],entity["MP"],entity["MAX_MP"],"["+" ".join(self.effect_list(entity))+" ]"))
            elif entity["EType"] == 2:
                texts[1].append("  [Lv%s] %s %s/%s %s"%(entity["LV"],entity["Name"],entity["HP"],entity["MAX_HP"],"["+" ".join(self.effect_list(entity))+" ]"))
        self.add_log("\nあなた\n"+"\n".join(texts[0])+"\n敵\n"+"\n".join(texts[1])+"\n",msg)
        self.add_log("%sはどうする?"%(entities["p1"]["Name"]),msg)
        self.add_log(' あ : 攻撃\n い : 魔法\n う : 防御\n え : アイテム\n お : 逃走',msg)

    def key_by_num(self,dict,num):
        ks = dict.keys()
        for i,k in enumerate(ks):
            if i == num: 
                return k
    #状態異常一覧を返す
    def effect_list(self,entity):
        return [self.effect_dict[e["TYPE"]] for e in entity["Effects"]]
    #辞書からランダムに選んで要素を返す
    def pick_by_per(self,dic):
        if "Auto" in dic:
            ls = list(dic.keys())
            ls.remove("Auto")
            return dic[random.choice(ls)]
        else:
            num = random.randint(1,100)
            for key in dic:
                if num <= int(key): return dic[key]
            raise ValueError 
class B_Process(object):
    #新規バトルの作成
    def new_battle(self,quest,team,wave,msg):
        b = OrderedDict()
        b["Turn"] = 1
        b["I_Turn"] = 0
        b["Process_Turn"] = True
        b["Selecting"] = False
        b["MenuID"] = 0
        b["Got"] = {1:0,2:0,3:0}
        b["Entities"] = OrderedDict()
        b["Log"] = []
        i = 1
        for m in quest["Monsters"][str(team)][wave-1]:
            e = self.new_entity(2,m["Name"],m["LV"],drops=m["Drops"])
            e["EType"] = 2
            b["Entities"]["e"+str(i)] = e
            i += 1
        #ここをforで回せばプレイヤーが複数人になるはずだがデータがない
        e = self.new_entity(1,mid=msg._from)
        e["EType"] = 1
        b["Entities"]["p1"] = e
        b = self.sort_entities(b)
        for key in b["Entities"]:
            b["Entities"][key] = self.reset_entity_effect(b["Entities"][key])
        self.rpgdata[msg._from]["Stats"]["Battle"] = b
        texts = [e["Name"] for e in self.gen_enemys(msg)]
        self.add_log("\n".join(texts)+"\nが現れた!",msg)
        self.send_log(msg)
        self.process_battle(msg)
    #ターン処理(ここを中心に戦闘を回す)
    def process_turn(self,msg):
        print("Called Process_Turn")
        battle = self.rpgdata[msg._from]["Stats"]["Battle"]
        entity = battle["Entities"][self.key_by_num(battle["Entities"],battle["I_Turn"])]
        if entity["EType"] == 2:
            entity = self.process_enemy(entity,msg)
        elif entity["EType"] == 1:
            return True
        self.process_effects_after(entity,msg)
        #battle["Entities"][self.key_by_num(battle["Entities"],battle["I_Turn"])] = entity
        battle["I_Turn"] += 1
        if battle["I_Turn"] >= len(battle["Entities"]):
            battle["I_Turn"] = 0
            battle["Turn"] += 1
        #print(battle["Turn"])
        self.rpgdata[msg._from]["Stats"]["Battle"] = battle
    #敵の処理 (プレイヤーに対して攻撃する)
    def process_enemy(self,enemy,msg):
        print("Called Process_Enemy")
        enemy = self.process_effects_before(enemy)
        enemy["CHG"] += 1
        #攻撃先は完全ランダム
        player = random.choice(self.gen_players(msg))
        #スキルを選ぶ
        if enemy["CHG"] not in enemy["Charges"]:
            skill_dic = self.pick_by_per(enemy["Percents"])
            skill = deepcopy(self.pick_by_per(enemy["Skills"][skill_dic]))
            skill["S_Type"] = skill_dic
        else:
            skill = enemy["Charges"][enemy["CHG"]][random.choice(list(enemy["Charges"][enemy["CHG"]].keys()))]
        #スキルは敵の通常データ+スキルの固有データ
        if "MAT" in skill: skill["MAT"] += enemy["MAT"]
        if "ATK" in skill: skill["ATK"] += enemy["ATK"]
        if enemy["CHG"] not in enemy["Charges"]:
            if skill["S_Type"] == "Defaults":
                if skill["Entire"]: self.attack_all(enemy,1,msg)
                else: self.attack(enemy,player,skill,msg)
            elif skill["S_Type"] == "Specials":
                if skill["Entire"]: self.magic_attack_all(enemy,skill,1,msg)
                else: self.magic_attack(enemy,player,skill,msg)
        else:
            if skill["Entire"]: self.magic_attack_all(enemy,skill,2,msg)
            else: self.magic_attack(enemy,player,skill,msg)
        if enemy["CHG"] > enemy["MAX_CHG"]: enemy["CHG"] = 0
        return enemy
    #プレイヤーの処理(メッセージ入力がここに飛んでくる)
    def process_player(self,msg):
        print("Called Process_Player")
        battle = self.rpgdata[msg._from]["Stats"]["Battle"]
        #攻撃先の選択
        if battle["Selecting"]:
            #攻撃
            if battle["MenuID"] == 0:
                self.rpgdata[msg._from]["Stats"]["Battle"]["Selecting"] = False
            #魔法
            elif battle["MenuID"] == 1:
                self.rpgdata[msg._from]["Stats"]["Battle"]["Selecting"] = False
        else:
            #コマンドの選択
            if battle["MenuID"] == 0:
                #有効なコマンドか確認
                choice = self.choicer(msg.text,self.commands)
                if choice != None:
                    if choice == "攻撃":
                        self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 0
                        enemys = self.gen_enemys(msg)
                        if len(enemys) == 1:
                            self.attack(battle["Entities"]["p1"],battle["Entities"]["e1"],msg,"e1")
                            battle["Process_Turn"] = True
                            battle["I_Turn"] += 1
                            if battle["I_Turn"] >= len(battle["Entities"]):
                                battle["I_Turn"] = 0
                                battle["Turn"] += 1
                            self.process_battle(msg)
                        else:
                            self.cl.sendMessage("攻撃先は?"+"\n".join(self.choice_list(enemys))+"\n も : 戻る")
                            self.rpgdata[msg._from]["Stats"]["Battle"]["Selecting"] = True
                    elif choice == "魔法":
                        self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 1
                        self.cl.sendMessage("どれを使用しますか?"+"\n".join(self.choice_list(battle["Entities"]["p1"]["Skills"]))+"\n も : 戻る")
                    elif choice == "防御":
                        self.defense(battle)
                    elif choice == "アイテム":
                        self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 1
                        self.cl.sendMessage("どれを使用しますか?"+"\n".join(self.choice_list(battle["Entities"]["p1"]["Skills"]))+"\n も : 戻る")
                    elif choice == "逃走":
                        self.escape(battle)
                elif msg.toType == 0:
                    self.cl.sendMessage("コマンドが正しくありません")
            #スキルの選択
            elif battle["MenuID"] == 1:
                #も は 戻る固定
                if msg.text != "も":
                    #有効なスキル名か確認
                    choice = self.choicer(msg.text,list(self.rpgdata[msg._from]["Skills"].keys()))
                    if choice != None:
                        self.rpgdata[msg._from]["Stats"]["Battle"] = self.Skill(choice,battle)
                else:
                    self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 0
                    self.add_log("%sはどうする?"%(battle["Entities"]["p1"]["Name"]),msg)
                    self.add_log(' あ : 攻撃\n い : 魔法\n う : 防御\n え : アイテム\n お : 逃走',msg)
                    self.send_log(msg)
            #アイテムの選択
            elif battle["MenuID"] == 2:
                #も は 戻る固定
                if msg.text != "も":
                    #有効なアイテムか確認
                    choice = self.choicer(list(self.rpgdata[msg._from]["Inventory"].keys()))
                    if choice != None:
                        self.Item(choice,battle)
                else:
                    self.rpgdata[msg._from]["Stats"]["Battle"]["MenuID"] = 0
                    self.add_log("%sはどうする?"%(battle["Entities"]["p1"]["Name"]),msg)
                    self.add_log(' あ : 攻撃\n い : 魔法\n う : 防御\n え : アイテム\n お : 逃走',msg)
                    self.send_log(msg)
            #IDが謎
            else:
                raise ValueError
    #攻撃先を選ぶ (entityを返す) かーきーなーおーせー
    def process_select_to(self,msg):
        pass
    #状態効果によるアップ/ダウン (攻撃前の処理)(未使用)
    def process_effects_before(self,entity):
        if entity["Effects"] != {}:
            for s in entity["Effects"]:
                pass
        return entity
    #状態効果によるアップ/ダウン (攻撃後の処理)
    def process_effects_after(self,entity,msg):
        if entity["Effects"] != {}:
            for s in entity["Effects"]:
                s["Turn"] -= 1
                if s["Turn"] < 1:
                    self.add_log("%sの効果が切れたようだ"%(self.effect_dict[s["TYPE"]]),msg)
                    entity = entity["Effects"].remove(s)
                    entity = self.reset_entity(entity)
                    entity = self.effect(entity)
    #フィールドを整える
    def process_field(self,msg):
        battle = self.rpgdata[msg._from]["Stats"]["Battle"]
        #HP0のエンティティを削除する
        ens = deepcopy(battle["Entities"])
        keep_alive = [e for e in ens if battle["Entities"][e]["HP"] > 0]
        battle["Entities"] = OrderedDict()
        for a in keep_alive:
            battle["Entities"][a] = ens[a]
        self.reid_entities(self.sort_entities(battle))
        self.rpgdata[msg._from]["Stats"]["Battle"] = battle
    #勝敗判定
    def process_check(self,msg):
        #敵がいなくなったら勝ち
        if len(self.gen_enemys(msg)) == 0:
            self.add_log("GAME CLEAR",msg)
            self.send_log(msg)
            msg.text = "中断"
            self.process_rpg(msg)
        #プレイヤーがいなくなったら負け
        elif len(self.gen_players(msg)) == 0:
            self.add_log("GAME OVER",msg)
            self.send_log(msg)
            
#戦闘処理
class Battle(B_Entity,B_Process,B_Utility):
    commands = ["攻撃","魔法","防御","アイテム","逃走"]
    effect_dict = {
        0:"攻昇",1:"攻少",2:"魔昇",3:"魔少",4:"防昇",
        5:"防少",6:"運昇",7:"運少",8:"俊足",9:"鈍足",
        10:"回復",11:"気合",12:"瀕死",13:"運極",14:"不幸",
        15:"飢餓",16:"空腹",17:"火傷",18:"毒",19:"猛毒",
        20:"病気",21:"重病",22:"麻痺",23:"エロ",24:"魅了",
        25:"睡眠",26:"凍結",27:"盲目",28:"疲労",29:"混乱",
        30:"憂鬱",31:"呪い",32:"恐怖",33:"中毒",34:"沈黙",
        35:"弱気",36:"憎悪",37:"ドM",38:"興奮",39:"ドS",40:"発情",
        41:"運極",42:"暴走",43:"属昇",44:"属少",45:"全昇",
        46:"全少"
    }
    
    def process_battle(self,msg):
        battle = self.rpgdata[msg._from]["Stats"]["Battle"]
        #戦闘を回すかどうか
        if battle["Process_Turn"]:
            #プレイヤーのターンになるまで回す
            while True:
                flag = self.process_turn(msg)
                if flag: break
            #プレイヤーのターンが回ってきたら表示する
            self.log_status(msg)
            self.send_log(msg)
            #戦闘回してない
            self.rpgdata[msg._from]["Stats"]["Battle"]["Process_Turn"] = False
        else:
            self.process_player(msg)

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
    def gen_damage(self,_from,to,type,msg,Skill=None): 
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
            self.add_log(" クリティカル！",msg)
        #Type= 0/無属性 1/水 2/炎 3/風 4/土 5/闇 6/光
        #相性が良ければ 1.3~1.5倍のダメージ
        if (Skill["TYPE"] == 1 and to["TYPE"] == 2
        or Skill["TYPE"] == 2 and to["TYPE"] == 3
        or Skill["TYPE"] == 3 and to["TYPE"] == 4
        or Skill["TYPE"] == 4 and to["TYPE"] == 1
        or Skill["TYPE"] == 5 and to["TYPE"] == 6
        or Skill["TYPE"] == 6 and to["TYPE"] == 5):
            damage = int(damage * (1+(random.randint(4,5)/10)))
            self.add_log(" あいしょうはばつぐんだ！")
        #相性が悪ければ 0.4~0.6倍のダメージ
        if (Skill["TYPE"] == 1 and to["TYPE"] == 4
        or Skill["TYPE"] == 4 and to["TYPE"] == 3
        or Skill["TYPE"] == 3 and to["TYPE"] == 2
        or Skill["TYPE"] == 2 and to["TYPE"] == 1):
            damage = int(damage * (random.randint(4,6)/10))
            self.add_log(" こうかはいまひとつのようだ...")
        return damage
    def get_damage(self,to,damage,msg):
        if damage <= 0: damage = 0
        to["HP"] -= damage
        self.add_log("%sは%sのダメージを受けた"%(to["Name"],damage),msg)
        if to["HP"] <= 0:
            chk = [e for e in to["Effects"] if e["TYPE"] == 11]
            if chk != []:
                to.HP = 1
            else:
                self.add_log("%sは倒れた"%(to["Name"]),msg)
                self.process_field(msg)
                self.process_check(msg)
                raise ValueError
        elif to["HP"] < 5:
            chk = [e["TYPE"] for e in to["Effects"] if e["TYPE"] == 12]
            if chk != [12]:
                to["Effects"].append({"TYPE":12,"Power":100,"Turn":10})
                to = self.reset_entity(to)
                to = self.reset_entity_effect(to)
                self.add_log("%sは瀕死状態になった"%(to["Name"]),msg)
        return to
    #通常攻撃(プレイヤーも敵も通る)
    def attack(self,_from,to,msg,set_to):
        print("Called attack")
        self.add_log("%sの攻撃"%(_from["Name"]),msg)
        self.add_log("<通常> %sの剣"%(_from["Name"]),msg)
        #ダメージ計算して、ダメージを受ける
        damage = self.gen_damage(_from,to,0,msg)
        self.get_damage(to,damage,msg)
    def attack_all(self,_from,toType,msg):
        print("Called attack_all")
        self.add_log("%sの攻撃"%(_from["Name"]),msg)
        battle = self.rpgdata[msg._from]["Stats"]["Battle"]
        for entity in battle["Entities"]:
            entity = battle["Entities"][entity]
            if entity["EType"] == toType:
                damage = self.gen_damage(_from,entity,0,msg)
                self.get_damage(entity,damage,msg)
                #battle["Entities"][self.key_by_num(battle,battle["I_Turn"])] = self.get_damage(entity,damage,msg)
    #効果攻撃(プレイヤーも敵も通る)
    def effect_attack(self,_from,to,Skill,msg):
        print("%sの攻撃"%(_from.name))
        print("<スキル> %s"%(Skill["Name"]))
        if Skill["TYPE"] not in to.Deny:
            if random.randint(1,100) < Skill["HIT"]:
                data = {"TYPE":Skill["TYPE"],"Turn":Skill["Power"]+2,"Power":Skill["Power"]}
                to["Effects"].append(data)
                to = self.entity_reset(to)
                to = self.effect(to)
                print("%sは%s状態になった"%(to.name,self.effect_dict[Skill["TYPE"]]))
            else:
                print("%sの攻撃は外れた"%(_from.name))
        else:
            print("%sには効果がないようだ..."%(to.name))
    def effect_attack_all(self,_from,Skill,toType,msg):
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
                        print("%sは%s状態になった"%(en["Name"],self.effect_dict[Skill["TYPE"]]))
                        battle["Entities"][en] = en
                    else:
                        print("%sの攻撃は外れた"%(_from["Name"]))
                else:
                    print("%sには効果がないようだ..."%(en["Name"]))
    #魔法攻撃(プレイヤーも敵も通る)
    def magic_attack(self,_from,to,Skill,msg):
        print("Called magic_attack")
        self.add_log("%sの攻撃"%(_from["Name"]),msg)
        self.add_log("<スキル> %s"%(Skill["Name"]),msg)
        #命中率的な設定
        if random.randint(1,100) < Skill["HIT"]:
            #ダメージ計算して♡
            damage = self.gen_damage(_from,to,1,msg,Skill)
            to = self.get_damage(to,damage,msg)
        else:
            self.add_log("%sの攻撃は外れた"%(_from["Name"]),msg)
        return to
    def magic_attack_all(self,_from,Skill,toType,msg):
        print("Called magic_attack_all")
        self.add_log("%sの攻撃"%(_from.name),msg)
        self.add_log("<スキル> %s"%(Skill["Name"]),msg)
        if random.randint(1,100) < Skill["HIT"]:
            for entity in self.entities:
                if type(entity) == toType:
                    damage = self.gen_damage(_from,entity,1,msg,Skill)
                    self.get_damage(entity,damage,battle)
        else:
            self.add_log(" %sの攻撃は外れた"%(_from["Name"]),msg)

'''
#とりあえず戦闘を直接呼ぶ
quest = game.quest_dict["デバッグクエスト"]
#クエストからバトルを作りrpgdataに入れる
game.new_battle(quest,1,1,Message())
'''