def add(a,b):
    return a+b
def sub(a,b):
    return a-b
def product(a,b):
    return a*b
def div(a,b):
    return a//b
def mod(a,b):
    return a%b

num1=int(input("Enter num 1 : "))
num2=int(input("Enter num 2 : "))

print("Sum :",add(num1,num2))
print("Difference :",sub(num1,num2))
print("Product :",product(num1,num2))
print("Quotient :",div(num1,num2))
print("Modulo :",mod(num1,num2))