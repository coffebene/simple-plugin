# simple-plugin

Python实现的中间件，实现插件热插拔功能。

该模块用于在主逻辑函数执行前后附加其他逻辑，实现类似装饰器功能；用于解决当附加逻辑过多时，装饰器嵌套过深，逻辑混乱问题



**使用示例**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用于实现插件热插拔
注意事项：
	1. 插件导入顺序，依赖插件在目录中的顺序（插件实现时，需考虑插件文件在目录中的位置）
	2. 如果多个插件目录中有重名插件，默认只导入第一个目录中找到插件
"""

import time
from plugin import middleware


def test():
    print "函数真正执行"


while True:
    mid = middleware.Middleware()  # 初始化中间件实例
    mid.funcAppend(test)  # 加载要执行的函数
    mid.addPlugin2Func(test, pluginDir="./plugin/pluginsBefore/", loop=True, position="before")  # 在函数执行前加载插件
    mid.addPlugin2Func(test, pluginDir="./plugin/pluginsAfter/", loop=True, position="after")  # 在函数执行后加载插件
    print mid.funcCallChain(test)  # 打印函数调用链
    mid.process()  # 中间件运行
    time.sleep(10)
```

**函数使用说明**

```python
mid.funcInsert(index,func)
# 在index位置插入主函数
```

```python
mid.funcPop(index=-1)
# 删除index位置主函数
```

```python
mid.funcRemove(func)
# 从中间件主函数列表中删除指定函数
```

```python
mid.funcAppend(func)
# 该函数用于向中间件添加主逻辑函数
```

```python
mid.addPlugin2Func(func, pluginDir=pluginDir, loop=False, position=position)  
# 在函数特定位置（目前支持函数执行前或执行后）加载插件
# 参数
#	func：主逻辑函数
#	pluginDir：插件查找的目录
#	loop：是否递归加载子目录中的插件（默认不递归）
#	position：插件添加的位置（支持before/after两种，不传默认为before）
```

```python
mid.funcCallChain(test)
# 打印函数执行链
```

```python
mid.process()
# 执行插件中主函数
```

