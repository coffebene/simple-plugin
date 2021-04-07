#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from plugin import loader

p = loader.PluginLoader('./plugin')

while True:
    p.loadPlugins(loop=True)
    print p.plugins
    time.sleep(10)
