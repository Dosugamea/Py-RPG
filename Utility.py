class Message(object):
    def __init__(self,_from="User",to="User",toType=0,text=""):
        self._from = _from
        self.to = to
        self.toType = 0
        self.text = text
class Client(object):
    def __init__(self):
        self.reqId = 0
    def sendMessage(self,text):
        print("Req<%s>\n\n%s"%(self.reqId,text))
        self.reqId += 1
class Logger(object):
    def add_log(self,text,msg):
        self.rpgdata[msg._from]["Stats"]["Log"].append(text)
    def send_log(self,msg):
        text = self.combine(self.rpgdata[msg._from]["Stats"]["Log"])
        self.cl.sendMessage(text)
        self.rpgdata[msg._from]["Stats"]["Log"] = []
class Choicer(object):
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
    def choicer(self,text="1",ls=["A","B","C"]):
        if text in ls: return text
        try:
            return ls[int(text)-1]
        except:
            if text in self.choice_dict:
                if len(ls) > self.choice_dict[text]-1:
                    return ls[self.choice_dict[text]-1]
    def choice_text(self,ls,kana=False):
        if kana: return [ " %s : %s"%(self.choice_dict[i+1],l) for i,l in enumerate(ls)]
        else: return [ " %s : %s"%(i+1,l) for i,l in enumerate(ls)]
    def combine(self,ls):
        text = ""
        for l in ls:
            text += l+"\n"
        text = text[:len(text)-1]
        return text
    def auto_choice(self,ls):
        for l in ls:
            self.process_rpg(Message(text=str(l)))