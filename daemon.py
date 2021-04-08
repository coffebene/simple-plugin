#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
