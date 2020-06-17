def find_j(arr):
    a=[]
    for i in range(len(arr)-1):
        if arr[i]<arr[i+1]:
            a.append(i)
    return a
def find_l(arr,j):
    a=[]
    for i in range(len(arr)):
        if (i>j):
            if arr[i] > arr[j]:
                a.append(i)

    a_m=max(a)
    a = arr[j]
    b = arr[a_m]
    arr[j] = b
    arr[a_m] = a
    return arr

def rev_array(arr):
    a=[]
    for el in reversed(arr):
        a.append(el)
    return a


def rev_order(arr,j):
   # print(arr)
    n_arr=[]
    o_arr=[]
    for i in range(j+1):
        o_arr.append(arr[i])
    for i in range(j+1,len(arr)):
        n_arr.append(arr[i])
    #print(n_arr)
    if len(n_arr)>1:
        n_arr = rev_array(n_arr)
    #print(n_arr)
    return o_arr+n_arr



def get_perm(st):
    num_arr =[]
    for strl in st:
        num_arr.append(strl)
    perm=[]
    while perm!= sorted(st,reverse=True):
        j_arr = find_j(num_arr)
        if j_arr!=[]:
            j = max(j_arr)
            #print("j:{}".format(j))
            new_arr= find_l(num_arr,j)
            #print("new_Array:{}".format(new_arr))
            perm=rev_order(new_arr,j)
            print(''.join(perm))
            num_arr=perm
        else:
            break



st = input("Enter number")
print(st)
get_perm(st)
