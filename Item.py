import random

class Item(object):
    #アイテム確率一覧[{"ITEM_ID":1,"COUNT":10,"PERCENT":100}]
    #からアイテム入手一覧{"ID":1} 作成
    def iper2igot(self,items):
        got = {}
        for item in items:
            rnd = random.randint(1,100)
            per = item["PERCENT"]
            iid = str(item["ITEM_ID"])
            if rnd <= per:
                if iid not in got:
                    got[iid] = item["COUNT"]
                else:
                    got[iid] += item["COUNT"]
        return got            

    #アイテム入手一覧{"ID":1} から アイテム入手テキスト作成
    def igot2itext(self,gotitems):
        txt = ""
        for i in gotitems:
            txt += "　%s x%s\n"%(self.itemdata[i]["Name"],gotitems[i])
        return txt[:len(txt)-1]
        
    #アイテム入手一覧{"ID":1} から RPGデータに加算
    def igot2data(self,gotitems,msg):
        data = self.rpgdata[msg._from]["Items"]
        for i in gotitems:
            if i != "0":
                if i not in data:
                    data[i] = gotitems[i]
                else:
                    data[i] += gotitems[i]
            else:
                self.rpgdata[msg._from]["Money"] += gotitems[i]