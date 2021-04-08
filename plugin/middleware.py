# -*- coding:utf-8 -*-

"""
在插件热插拔的基础上实现中间件

PS:
    需要注意的是，插件目录如果有同名文件，则只会导入第一个目录中找到的文件
"""

import logging
import loader
from inspect import isfunction


# 中间件
class Middleware(object):
    
    def __init__(self, logger=logging):
        self.logger = logger
        self.funcList = []  # 要执行的方法列表。示例：[funcA, funcB]
        self.plugin = {}  # 方法要执行的插件列表。示例：{funcA:{"before":[pluginA, pluginB], "after":[pluginC]}
        self.pluginParam = {}  # 各插件参数。示例: {funcA:{"before":[{"pluginDir":"dirA", "loop":False}, {"pluginDir":"dirB","loop":True}]}}
    
    # 在方法列表末尾添加新的对象
    def funcAppend(self, func):
        if not isfunction(func):
            raise TypeError("func must be callable")
        if func not in set(self.funcList):
            self.funcList.append(func)
    
    # 从方法列表中找出某个值第一个匹配项的索引位置
    def funcIndex(self, func):
        if not isfunction(func):
            raise TypeError("func must be callable")
        self.funcList.index(func)
    
    # 将对象插入列表
    def funcInsert(self, index, func):
        if not isfunction(func):
            raise TypeError("func must be callable")
        if func not in set(self.funcList):
            self.funcList.insert(index, func)
    
    # 移除方法列表中的一个元素（默认最后一个元素），并且返回该元素的值
    def funcPop(self, index=-1):
        return self.funcList.pop(index)
    
    # 移除列表中某个值的第一个匹配项
    def funcRemove(self, func):
        if not isfunction(func):
            raise TypeError("func must be callable")
        self.funcList.remove(func)
    
    # 返回方法名称列表
    @property
    def funcNameList(self):
        funcName = [i.__name__ for i in self.funcList]
        return funcName
    
    # 判断插件目录是否已存在
    def dirExist(self, funcName=None, pluginDir=None, position=None):
        # 插件目录是否存在，以及插件下标
        index = 0
        flag = False
        # 判断插件参数是否已存在
        pluginParam = self.pluginParam.get(funcName, {})
        dirName = [i["pluginDir"] for i in pluginParam.get(position, [])]
        if pluginDir in dirName:
            flag = True
            index = dirName.index(pluginDir)
        return flag, index
    
    # 向方法添加插件
    def addPlugin2Func(self, func=None, pluginDir=None, loop=None, position=None):
        # 参数校验
        if not (position and not (position not in ("before", "after"))):
            raise ValueError("position must be none or in ['before', 'after']")
        elif not position:
            position = "before"
        # 获取函数名
        funcName = func
        if isfunction(func):
            funcName = func.__name__
        if funcName not in self.funcNameList:
            raise ValueError("%s not in funcList, please add func to middleware first" % funcName)
        # 存储参数
        pluginParam = self.pluginParam.get(funcName, {})
        if not pluginParam:
            pluginParam[position] = [{"pluginDir": pluginDir, "loop": loop}]
        else:
            exsit, index = self.dirExist(funcName=funcName, pluginDir=pluginDir, position=position)
            if exsit:
                pluginParam[position][index] = {"pluginDir": pluginDir, "loop": loop}
            else:
                if pluginParam.get(position):
                    pluginParam[position].append({"pluginDir": pluginDir, "loop": loop})
                else:
                    pluginParam[position] = [{"pluginDir": pluginDir, "loop": loop}]
        self.pluginParam[funcName] = pluginParam
    
    # 从方法删除插件
    def deletePlugin2Func(self, func=None, pluginDir=None, position=None):
        # 参数校验
        if not (position and not (position not in ("before", "after"))):
            raise ValueError("position must be none or in ['before', 'after']")
        elif not position:
            position = "before"
        # 获取函数名
        funcName = func
        if isfunction(func):
            funcName = func.__name__
        if funcName not in self.funcNameList:
            return
        # 删除插件
        pluginParam = self.pluginParam.get(funcName, {})
        if not pluginParam:
            return
        # 如果没有传具体插件目录则删除整个插件位置
        if not pluginDir:
            pluginParam.pop(position)
        else:
            exsit, index = self.dirExist(funcName=funcName, pluginDir=pluginDir, position=position)
            if exsit:
                pluginParam[position].pop(index)
    
    # 向方法添加插件
    def updatePlugin(self):
        """pluginParam参数示例：
        {
            "funcA": {
                "before": [
                            {
                                "pluginDir": "dirA",
                                "loop": false
                            },
                            {
                                "pluginDir": "dirB",
                                "loop": true
                            }
                        ],
                "after": [
                            {
                                "pluginDir": "dirC",
                                "loop": false
                            }
                        ]
                    }
        }
        """
        for funcName, param in self.pluginParam.items():
            pluginsInfo = {}
            self.plugin[funcName] = pluginsInfo
            for position, dirInfo in param.items():
                plugins = []
                pluginsInfo[position] = plugins
                for d in dirInfo:
                    loaderObj = loader.PluginLoader()
                    loaderObj.loadPlugins(pluginDir=d["pluginDir"], loop=d["loop"])
                    plugins.extend(loaderObj.plugins)
    
    # 返回函数调用链
    def funcCallChain(self, func=None):
        self.updatePlugin()  # 更新插件
        callChain = []
        # 获取函数名
        if not func:
            raise ValueError("func can not be none")
        funcName = func
        if isfunction(func):
            funcName = func.__name__
        # 查询调用链
        if funcName not in self.funcNameList:
            return callChain
        callChain.extend(self.plugin[funcName].get("before", []))
        callChain.append(funcName)
        callChain.extend(self.plugin[funcName].get("after", []))
        return callChain
    
    # 执行函数
    def process(self):
        self.updatePlugin()  # 更新插件
        for func in self.funcList:
            funcName = func.__name__
            plugins = self.plugin.get(funcName)
            if not plugins:
                continue
            beforePlugins = plugins.get("before", [])
            afterPlugins = plugins.get("after", [])
            for p in beforePlugins:
                n, m = p.items()[0]
                method = getattr(m["module"], "run", None)
                if isfunction(method):
                    method()
            func()
            for p in afterPlugins:
                n, m = p.items()[0]
                method = getattr(m["module"], "run", None)
                if isfunction(method):
                    method()
