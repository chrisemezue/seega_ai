import numpy as np
import sys
import cgitb
cgitb.enable()
signs = ['+','-','/','*','=']

#Code copyright: Daniel @ https://stackoverflow.com/users/975477/daniel

def cartesian_coord(*arrays,num):
    req=[]
    grid = np.meshgrid(*arrays)
    coord_list = [entry.ravel() for entry in grid ]
    points = np.vstack(coord_list).T
    for point in points:
        ua,u_ind = np.unique(point,return_counts=True)
        if np.all(u_ind == 1,axis=0):
           # print(point)
            req.append(point)

    return req

#a = np.arange(10)
#num=6
#print(cartesian_coord(*num*[a],num=num))

def get_text(text):
    operator={}
    op_before_a=[]
    op_before_sign = []
    op_before_b=[]
    op_after_a =[]
    op_after_sign=[]
    op_after_b = []
    t = text.split('=')
    #print(t[0])
    #print(t[1])
    k = 0
    for txt in t[0]:
        if txt in signs:
            k=1
            op_before_sign.append(txt)
        if k==0 and txt not in signs:
            op_before_a.append(txt)
        if k==1 and txt not in signs:
            op_before_b.append(txt)
    l=0
    for txt in  t[1]:
        if txt in signs:
            l=1
            op_after_sign.append(txt)
        if l==0 and txt not in signs:
            op_after_a.append(txt)
        if l==1 and txt not in signs:
            op_after_b.append(txt)



    #print(op_before_sign)
    #print(op_before_b)
    operator['before_a']=op_before_a
    operator['before_sign']=op_before_sign
    operator['before_b']=op_before_b
    operator['after_a']=op_after_a
    operator['after_sign']=op_after_sign
    operator['after_b']=op_after_b
    return operator
g = sys.argv[1]
op_ = get_text(g)

def take_array_to_dict(operator):
    op_before=operator['before_a'] + operator['before_sign'] + operator['before_b']
    op_after = operator['after_a'] + operator['after_sign'] + operator['after_b']
    op_dict={}
    op_dict['+']='+'
    op_dict['=']='='
    op_dict['-']='-'
    op_all=op_before+['=']+op_after
    #print(op_all)
    op_all_set= set(op_all)-set(signs)
    op_all_list = list(op_all_set)
    #print(op_all_set)
    op_all_length = len(op_all_set)
    #print(op_all_length)
    set_before = set(op_before)
    set_after = set(op_after)
    file= 'C:/Users/USER/Desktop/RL_SEEGA/AZ/size_{}.npy'.format(op_all_length)
    arrs = np.load(file)
    count=0
    for arr in arrs:
        i=0
        for strl in arr:
            op_dict['{}'.format(op_all_list[i])] = strl
            i+=1
        op_b_a_eval = [op_dict[c] for c in operator['before_a']]
        op_b_a_eval=''.join(op_b_a_eval)
        if len(op_b_a_eval)>1:
            op_b_a_eval = op_b_a_eval.lstrip('0')
        op_b_b_eval = [op_dict[c] for c in operator['before_b']]
        op_b_b_eval = ''.join(op_b_b_eval)
        if (len(op_b_b_eval) > 1):
            op_b_b_eval = op_b_b_eval.lstrip('0')
        op_a_a_eval = [op_dict[c] for c in operator['after_a']]
        op_a_a_eval = ''.join(op_a_a_eval)
        if (len(op_a_a_eval) > 1):
            op_a_a_eval = op_a_a_eval.lstrip('0')
        op_a_b_eval = [op_dict[c] for c in operator['after_b']]
        op_a_b_eval = ''.join(op_a_b_eval)
        if (len(op_a_b_eval) > 1):
            op_a_b_eval = op_a_b_eval.lstrip('0')
        #op_eval = [op_dict[c] for c in op_all]
        #op_eval = ''.join(op_eval)
        if operator['after_sign']!=[]:
            s=op_b_a_eval+operator['before_sign'][0]+op_b_b_eval+'=='+op_a_a_eval+operator['after_sign'][0]+op_a_b_eval
        else:
            s = op_b_a_eval + operator['before_sign'][0] + op_b_b_eval + '==' + op_a_a_eval
        op_eval = '('+s+')'
        ans = eval(op_eval)
        for_print=[]
        if ans==True:
            count+=1
            for op in op_all:
                for_print.append(op_dict[op])
            print(' '.join(for_print))
            print('<br>')
    print("ALL DONE")
    print('<br>')
    print("Total Number of Rebus: {}".format(count))



take_array_to_dict(op_)


def remove_zeros(arr):
    return arr.lstrip('0')