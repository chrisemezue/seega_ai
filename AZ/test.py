import numpy as np


'''

point_to_index ={1:(0,0,0,1),2:(0,0,1,0),3:(0,1,0,0),4:(0,1,0,2),5:(0,1,1,1),6:(0,2,0,1),7:(0,2,0,3),8:(0,2,1,2),9:(0,3,0,2),10:(0,3,0,4),11:(0,3,1,3),12:(0,4,0,3),13:(0,4,1,4),14:(1,0,0,0),15:(1,0,2,0),
                 16:(1,0,1,1),17:(1,1,0,1),18:(1,1,1,0),19:(1,1,2,1),20:(1,1,1,2),21:(1,2,0,2),22:(1,2,1,1),23:(1,2,2,2),24:(1,2,1,3),25:(1,3,0,3),26:(1,3,1,2),27:(1,3,1,4),28:(1,3,2,3),29:(2,0,1,0),30:(2,0,3,0),
                 31:(2,0,2,1),32:(2,1,2,0),33:(2,1,1,1),34:(2,1,3,1),35:(2,1,2,2),36:(2,2,2,1),37:(2,2,1,2),38:(2,2,2,3),39:(2,2,3,2),40:(2,3,2,2),41:(2,3,1,3),42:(2,3,3,3),43:(2,3,2,4),44:(2,4,2,3),45:(2,4,1,4),
                 46:(2,4,3,4),47:(1,4,1,3),48:(1,4,0,4),49:(1,4,2,4),50:(3,0,2,0),51:(3,0,3,1),52:(3,0,4,0),53:(3,1,3,0),54:(3,1,2,1),55:(3,1,4,1),56:(3,1,3,2),57:(3,2,3,1),58:(3,2,2,2),59:(3,2,4,2),60:(3,2,3,3),
                 61:(3,3,3,2),62:(3,3,2,3),63:(3,3,3,4),64:(3,3,4,3),65:(3,4,3,3),66:(3,4,2,4),67:(3,4,4,4),68:(4,0,3,0),69:(4,0,4,1),70:(4,1,3,1),71:(4,1,4,0),72:(4,1,4,2),73:(4,2,4,1),74:(4,2,4,3),75:(4,2,3,2),
                 76:(4,3,4,2),77:(4,3,3,3),78:(4,3,4,4),79:(4,4,4,3),80:(4,4,3,4), 81:(0,0),82:(0,1),83:(0,2),84:(0,3),85:(0,4),86:(1,0),87:(1,1),88:(1,2),89:(1,3),90:(1,4),91:(2,0),92:(2,1),93:(2,2),94:(2,3),95:(2,4),
                 96:(3,0),97:(3,1),98:(3,2),99:(3,3),100:(3,4),101:(4,0),102:(4,1),103:(4,2),104:(4,3),105:(4,4)}
point_index = []
point = []
for item in point_to_index.items():
    point_index.append(item[0] - 1)
    point.append(item[1])


if (0,3) in point:
    print("YES")
else:
    print("NO")

print(len((3,2)))'''
a = [-11,2,-3,-4,5,10,0]
b= [1,3,1,1]
print(np.tanh(a))