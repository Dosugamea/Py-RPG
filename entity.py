class EntityData():
	def __init__(self,name="DUMMY",LV=1,HP=10,MP=10,ATK=10,DEF=10,MDF=10,SPD=10,LUC=10,TYPE="Fire",Skill_1=Skill(),Skill_2=Skill(),Skill_3=Skill()):
		self.name = name
		self.LV = LV
		self.HP = HP
		self.MP = MP
		self.ATK = ATK
		self.DEF = DEF
		self.MDF = MDF
		self.SPD = SPD
		self.LUC = LUC
		self.TYPE = TYPE
		self.Skill_1 = Skill_1
		self.Skill_2 = Skill_2
		self.Skill_3 = Skill_3
		self.description = "Dummy Message"
		
	def print_info(self):
		print("Name: %s"%(self.name))
		print(self.description))