aa=['a','b','c']
bb=[1,2,3]
# method1
for a,b in zip(aa,bb):
    print('a:',a,'b:',b)

# method2
for i, a in enumerate(aa):
    b=bb[i]
    print('a:',a,'b:',b)

# method3
for i in range(len(aa)):
    a=aa[i]
    b=bb[i]
    print('a:', a, 'b:', b)
