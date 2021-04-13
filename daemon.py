#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用于实现插件热插拔
注意事项：
    1. 插件导入顺序，依赖插件在目录中的顺序（插件实现时，需考虑插件文件在目录中的位置）
    2. 如果多个插件目录中有重名插件，默认只导入第一个目录中找到插件（python import 机制所导致）
    3. 每个插件必须包含run()方法，且必须返回可判断真假的结果，用于判断后续插件是否继续执行
    4. 主函数需返回{"errCode": 0, "errMsg": "success"}，errCode用于判断后续插件是否执行
    5. 主函数之间互相隔离。前一个主函数执行失败与否，不会影响后一个主函数的执行
"""

import time
from plugin import middleware


def test1():
    print "函数1真正执行"
    return {"errCode": 0, "errMsg": "success"}


def test2(t1, t2, t3="hello"):
    print t1, t2, t3
    print "函数2真正执行"
    return {"errCode": 0, "errMsg": "success"}


while True:
    mid = middleware.Middleware()  # 初始化中间件实例
    mid.funcAppend(test1)  # 加载要执行的函数
    mid.funcAppend(test2)  # 加载要执行的函数
    mid.addPlugin2Func(test1, pluginDir="./plugin/pluginsBefore/", loop=True, position="before")  # 在函数执行前加载插件
    mid.addPlugin2Func(test2, pluginDir="./plugin/pluginsAfter/", loop=True, position="after")  # 在函数执行后加载插件
    mid.addParam2Func(test2, **{"t1": 1, "t2": 2})  # 向特定函数添加参数
    mid.addParam2Plugin(**{"t1": "new", "t2": "life", "t3": "try it"})  # 向插件添加参数集
    print mid.funcCallChain(test1)  # 打印函数调用链
    print mid.funcCallChain(test2)  # 打印函数调用链
    mid.process()  # 中间件运行
    time.sleep(10)
