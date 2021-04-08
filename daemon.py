#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from plugin import middleware


def test():
    print "函数真正执行"


while True:
    mid = middleware.Middleware()
    mid.funcAppend(test)
    mid.addPlugin2Func(test, pluginDir="./plugin/pluginsBefore/", loop=True, position="before")
    mid.addPlugin2Func(test, pluginDir="./plugin/pluginsAfter/", loop=True, position="after")
    print mid.pluginParam
    print mid.funcCallChain(test)
    mid.process()
    time.sleep(10)
