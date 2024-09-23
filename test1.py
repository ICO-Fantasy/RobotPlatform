import inspect

some_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# get some_list name
print(inspect.ismodule(some_list))
print(inspect.isclass(some_list))
print(inspect.iscode(some_list))
# 遍历所有本地变量，查找哪个变量指向该列表对象
variable_names = [name for name, value in globals().items() if value is some_list]

print(variable_names)  # 输出 ['my_list']
