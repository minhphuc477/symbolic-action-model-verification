class Hypothesis:

    def __init__(self, s, action1, obj11, obj12, action2, obj21, obj22, S1, S2, flag=False, para=None):
        
        self.S = s
        self.action1 = action1
        self.obj11= obj11
        self.obj12 = obj12
        self.action2 = action2
        self.obj21 = obj21
        self.obj22 = obj22
        self.sort1 = S1
        self.sort2=S2
        self.flag = flag
        self.para = para

    def get_state(self):
        return self.S

    def get_sort(self):
        return self.sort2
    def set_parameter(self, value):
        self.para=value

    def is_equal(self, other):
        t1 = (self.S==other.S and self.action1==other.action1 and self.obj11==other.obj11 and self.obj12==other.obj12)
        t2 = (self.S==other.S and self.action2==other.action2 and self.obj21==other.obj21 and self.obj22==other.obj22)

        return (t1 or t2)
