import json,random
from collections import OrderedDict
from datetime import datetime

class M_Process(object):
    #上から メインクエスト(ストーリー) サブクエスト(曜日クエスト)　イベントクエスト 戻る 
    quest_sel_dict = {
        0:["メイン","サブ","イベント","戻る"],
        1:["デバッグクエスト","Story_2","Story_3","戻る"],
        2:["Quest1","Quest2","Quest3","戻る"],
        3:["Quest1","Quest2","Quest3","戻る"]
    }
    yobi = ["月","火","水","木","金","土","日"]

    #ユーザーファイルからテキストを作る
    def make_stat_user(self,msg):
        ls = []
        ls.append("Lv%s %s"%(self.rpgdata[msg._from]["Level"],self.rpgdata[msg._from]["Name"]))
        ls.append("Level: %s"%(self.rpgdata[msg._from]["Level"]))
        ls.append("ToNext: %s"%(self.leveldata[str(self.rpgdata[msg._from]["Level"]+1)]["EXP"]-self.rpgdata[msg._from]["EXP"]))
        ls.append("Stamina: %s"%(self.rpgdata[msg._from]["Stamina"]))
        ls.append("Coin: %s"%(self.rpgdata[msg._from]["Money"]))
        ls.append("Stone: %s"%(self.rpgdata[msg._from]["Stone"]))
        return ls
    
    #曜日指定、期間指定でショップを作る
    def gen_global_shop(self):
        shops = self.shopdata
        cdate = datetime.now()
        #ショップ一覧の作成
        ret_ls = {}
        #日付が有効なリスト
        for s in shops:
            if "Limit" not in shops[s]:
                ret_ls[s] = shops[s]
            elif "Day" in shops[s]["Limit"]:
                if shops[s]["Limit"]["Day"][cdate.weekday()] == 1:
                    ret_ls[s] = shops[s]
            elif "Date" in shops[s]["Limit"]:
                _from = datetime.strptime(shops[s]["Limit"]["Date"][0],'%Y-%m-%d %H:%M:%S')
                to = datetime.strptime(shops[s]["Limit"]["Date"][1],'%Y-%m-%d %H:%M:%S')
                if cdate > _from and cdate < to:
                    ret_ls[s] = shops[s]
            else:
                ret_ls[s] = shops[s]
        self.available_shops = ret_ls
    
    #個数制限_グローバル個数制限 Deny 等に基づき 個々のユーザー用のショップリストを作る
    def gen_private_shop(self,msg):
        shops = self.available_shops
        return shops

#メニュー表示の拡張機能(遊べるようになったら作ろう)
class Menu_Loader(object):
    #メニューデータをキーリストから取る
    def make_menu_ls(self,key=None):
        mdata = deepcopy(self.menudata)
        if key != None:
            for k in key:
                mdata = mdata[k]
        return mdata
    #有効なメニューだけを取る
    def chk_menu_ls(self,menus,msg):
        #選択肢一覧は返す
        #クエストのデータはStatに返す
        ls = []
        qmenus = {}
        cdate = datetime.now()
        #日付指定 or 挑戦回数指定があるものはリストから消す
        for m in menus:
            menu = menus[m]
            if "Day" in menu:
                if menu["Day"][cdate.weekday()] == 1:
                    qmenus[m] = menu
                    ls.append()
            elif "Date" in menu:
                _from = datetime.strptime(menu["Date"][0],'%Y-%m-%d %H:%M:%S')
                to = datetime.strptime(menu["Date"][1],'%Y-%m-%d %H:%M:%S')
                if cdate > _from and cdate < to:
                    qmenus[m] = menu
                    ls.append()
            else:
                qmenus[m] = menu
                ls.append(m)
        self.rpgdata[msg._from]["Stats"]["Menu"]["Current_Menus"] = qmenus
        return ls                
        
class Menu(M_Process):
    def process_menu(self,msg):
        stat = self.rpgdata[msg._from]["Stats"]["Menu"]
        if stat["Selecting"] == False:
            #表示するだけー
            if stat["MenuID"] == 0:
                self.add_log(str(self.make_stat_user(msg)),msg)
                self.add_log("[ホーム]\nどこに行きますか?",msg)
                self.add_log(self.combine(self.choice_text(["クエスト","バイト","ショップ","設定"])),msg)
            elif stat["MenuID"] == 1:
                if stat["Quest_MID"] == 0:
                    self.add_log("[クエスト]\nどのクエストに行きますか?",msg)
                elif stat["Quest_MID"] == 1:
                    self.add_log("[メインクエスト]\nどのクエストに行きますか?",msg)
                elif stat["Quest_MID"] == 2:
                    self.add_log("[サブクエスト]\nどのクエストに行きますか?",msg)
                elif stat["Quest_MID"] == 3:
                    self.add_log("[イベントクエスト]\nどのクエストに行きますか?",msg)
                self.add_log(self.combine(self.choice_text(self.quest_sel_dict[stat["Quest_MID"]])),msg)
            elif stat["MenuID"] == 2:
                self.add_log("[バイト]\nどのバイトをしますか?",msg)
                self.add_log(self.combine(self.choice_text(["看板もち","交通量調査","警備員","パン工場","窓そうじ","工事現場","自宅警備員","戻る"])),msg)
            elif stat["MenuID"] == 3:
                self.gen_global_shop()
                self.rpgdata[msg._from]["Stats"]["Shop"]["List"] = self.gen_private_shop(msg)
                self.rpgdata[msg._from]["Stats"]["Screen"] = "shop"
            elif stat["MenuID"] == 4:
                if stat["Setting_ID"] == 0:
                    self.add_log("[設定]\n何を変更しますか?",msg)
                    self.add_log(self.combine(self.choice_text(["インベントリ","装備変更","スキル構成","アナウンス使用","メニューかな表記","戻る"])),msg)
                elif stat["Setting_ID"] == 1:
                    self.add_log("[インベントリ]\n<所持アイテム>",msg)
                    self.add_log(self.combine(self.choice_text(self.rpgdata[msg._from]["Inventory"].keys())),msg)
                    self.add_log("<倉庫内のアイテム>",msg)
                    self.add_log(self.combine(self.choice_text(self.rpgdata[msg._from]["Items"].keys())),msg)
            if stat["MenuID"] != 3:
                self.send_log(msg)
                self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = True
            else:
                self.process_shop(msg)
        else:
            #選択肢に応じて処理―
            #メインメニュー
            if stat["MenuID"] == 0:
                choice = self.choicer(msg.text,["クエスト","バイト","ショップ","設定"])
                if choice != None:
                    if choice == "クエスト":
                        stat["MenuID"] = 1
                        stat["Quest_MID"] = 0
                    elif choice == "バイト":
                        stat["MenuID"] = 2
                        stat["Work_MID"] = 0
                    elif choice == "ショップ":
                        stat["MenuID"] = 3
                    elif choice == "設定":
                        stat["MenuID"] = 4
                        stat["Setting_ID"] = 0
                    self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                    self.process_menu(msg)
            #クエストメニュー
            elif stat["MenuID"] == 1:
                choice = self.choicer(msg.text,self.quest_sel_dict[stat["Quest_MID"]])
                if choice != None:
                    if stat["Quest_MID"] == 0:
                            if choice == "メイン": stat["Quest_MID"] = 1
                            elif choice == "サブ": stat["Quest_MID"] = 2
                            elif choice == "イベント": stat["Quest_MID"] = 3
                            elif choice == "戻る": stat["MenuID"] = 0
                            self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                            self.process_menu(msg)
                    else:
                            if choice != "戻る": self.rpgdata[msg._from]["Stats"]["Quest"]["Quest_Name"] = choice
                            elif choice == "戻る": stat["Quest_MID"] = 0
                            self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                            if choice != "戻る":
                                self.rpgdata[msg._from]["Stats"]["Screen"] = "quest"
                                self.rpgdata[msg._from]["Stats"]["Quest"]["Questing"] = True
                                self.new_quest(msg)
                            else:
                                self.process_menu(msg)
            #ワークメニュー
            elif stat["MenuID"] == 2:
                choice = self.choicer(msg.text,["看板もち","交通量調査","警備員","パン工場","窓そうじ","工事現場","自宅警備員","戻る"])
                if choice != None:
                    if choice == "看板持ち":
                        pass
                    elif choice == "戻る":
                        stat["MenuID"] = 0
                    self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                    self.process_menu(msg)
            #設定メニュー
            elif stat["MenuID"] == 4:
                choice = self.choicer(msg.text,["インベントリ","装備変更","スキル構成","アナウンス使用","メニューかな表記","戻る"])
                if choice != None:
                    if choice == "Inventory":
                        stat["Setting_ID"] = 1
                    elif choice == "戻る":
                        stat["MenuID"] = 0
                    self.rpgdata[msg._from]["Stats"]["Menu"]["Selecting"] = False
                    self.process_menu(msg)

    def process_shop(self,msg):
        #deepcopyではないため直接呼ばれるが問題はないと思われる？
        stat = self.rpgdata[msg._from]["Stats"]["Shop"]
        #表示部
        if stat["Selecting"] == False:
            #ショップ未選択_選択直後
            if stat["StepID"] == 0:
                if stat["ShopID"] == 0:
                    self.add_log("[ショップ]\nどこに行きますか?",msg)
                    choices = list(stat["List"].keys())
                    choices.append("戻る")
                    self.add_log(self.combine(self.choice_text(choices)),msg)
                elif stat["ShopID"] in stat["List"].keys():
                    stat["Current_Shop"] = stat["List"][stat["ShopID"]]
                    self.add_log("[ %s ]"%(stat["ShopID"]),msg)
                    if "Welcome" in stat["Current_Shop"]["Messages"] and "Clerk" in stat["Current_Shop"]["Messages"]:
                        self.add_log("<%s> : %s"%(stat["Current_Shop"]["Messages"]["Clerk"],stat["Current_Shop"]["Messages"]["Welcome"]),msg)
                    self.add_log("",msg)
                    actions = []
                    if "Talk" in stat["Current_Shop"]: actions.append("会話")
                    #TODO: 互いのインポート処理をここに書こう
                    if "Buy" in stat["Current_Shop"] and "Deny" not in stat["Current_Shop"]["Buy"]: actions.append("買う")
                    if "Sell" in stat["Current_Shop"] and "Deny" not in stat["Current_Shop"]["Sell"]: actions.append("売る")
                    if len(actions) == 0: raise ValueError
                    actions.append("戻る")
                    stat["Current_Shop"]["Actions"] = actions
                    self.add_log(self.combine(self.choice_text(actions)),msg)
            #会話
            elif stat["StepID"] == 1:
                msi = str(random.choice(list(stat["Current_Shop"]["Talk"].keys())))
                if "Clerk" in stat["Current_Shop"]["Messages"]:
                    self.add_log("<%s> : %s"%(stat["Current_Shop"]["Messages"]["Clerk"],stat["Current_Shop"]["Talk"][msi]),msg)
                else:
                    self.add_log(stat["Current_Shop"]["Talk"][msi],msg)
                self.add_log("",msg)
                self.add_log(self.combine(self.choice_text(stat["Current_Shop"]["Actions"])),msg)
                stat["StepID"] = 0
            #"プレイヤーが"買う           
            elif stat["StepID"] == 2:
                self.add_log("< 商品リスト >\n",msg)
                self.add_log("所持金: %sコイン\n"%(self.rpgdata[msg._from]["Money"]),msg)
                if "Import_Buy" in stat["Current_Shop"]["Sell"]:
                    items = stat["Current_Shop"]["Buy"]["Items"]
                else:
                    items = stat["Current_Shop"]["Sell"]["Items"]
                itl = []
                for item in items:
                    im = self.itemdata[str(item["ID"])]
                    itl.append(" %s %s個%sコイン"%(im["Name"],item["Cnt"],item["Price"]))
                self.add_log(self.combine(self.choice_text(itl)),msg)
                stat["Current_Shop"]["Items"] = itl
            #"プレイヤーが"売る
            elif stat["StepID"] == 3:
                self.add_log("< 買取リスト >",msg)
                self.add_log("所持金: %sコイン\n"%(self.rpgdata[msg._from]["Money"]),msg)
                if "Import_Sell" in stat["Current_Shop"]["Buy"]:
                    items = stat["Current_Shop"]["Sell"]["Items"]
                else:
                    items = stat["Current_Shop"]["Item"]["Items"]
                itl = []
                for item in items:
                    im = self.itemdata[str(item["ID"])]
                    itl.append(" %s %s個%sコイン"%(im["Name"],item["Cnt"],item["Price"]))
                self.add_log(self.combine(self.choice_text(itl)),msg)
                stat["Current_Shop"]["Items"] = itl
            self.send_log(msg)
            stat["Selecting"] = True
        #入力受付部
        else:
            #ショップ未選択
            if stat["ShopID"] == 0:
                choices = list(stat["List"].keys())
                choices.append("戻る")
                choice = self.choicer(msg.text,choices)
                if choice != None:
                    stat["Selecting"] = False
                    if choice == "戻る":
                        self.rpgdata[msg._from]["Stats"]["Menu"]["MenuID"] = 0
                        self.rpgdata[msg._from]["Stats"]["Screen"] = "menu"
                        self.process_menu(msg)
                    else:
                        stat["ShopID"] = choice
                        self.process_shop(msg)
            else:
                #ショップ内動作選択
                if stat["StepID"] == 0:
                    choice = self.choicer(msg.text,stat["Current_Shop"]["Actions"])
                    if choice != None:
                        stat["Selecting"] = False
                        if choice == "戻る": stat["ShopID"] = 0
                        elif choice == "会話": stat["StepID"] = 1
                        elif choice == "買う": stat["StepID"] = 2
                        elif choice == "売る": stat["StepID"] = 3
                        self.process_shop(msg)
                #ショップ内購入選択処理
                elif stat["StepID"] == 2:
                    pass
                #ショップ内販売選択処理
                elif stat["StepID"] == 3:
                    pass