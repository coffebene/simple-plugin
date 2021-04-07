#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import imp
import glob
import hashlib


# 计算文件或目录的md5值
def md5Sum(entry):
    md5 = hashlib.md5()
    if os.path.isfile(entry) and glob.fnmatch.fnmatch(entry, "*.py"):
        with open(entry, "rb") as fd:
            md5.update(fd.read())
    if os.path.isdir(entry):
        for path, dirList, fileList in os.walk(entry):
            for f in fileList:
                if not glob.fnmatch.fnmatch(f, "*.py"):
                    continue
                with open(os.path.join(path, f), "rb") as fd:
                    md5.update(fd.read())
    return md5.hexdigest()


class PluginLoader(object):
    """plugin加载器。根据plugins目录查找并导入文件"""
    
    def __init__(self, pluginDir):
        self.plugins = {}  # 存放加载的模块信息
        if not os.path.isdir(pluginDir):
            raise ValueError("%s must be dir" % pluginDir)
        self.pluginDir = pluginDir  # 模块路径
    
    # 查找可导入的module
    def findPlugins(self, pluginDir=None, loop=False):
        """遍历目录，查找可导入plugin
        参数：
            pluginDir: 查找路径
            loop: 是否递归导入子包中的模块
        """
        plugins = []
        if not pluginDir or not os.path.isdir(pluginDir):
            pluginDir = self.pluginDir
        # 遍历目录
        for item in os.listdir(pluginDir):
            moduleName, suffix = os.path.splitext(item)
            location = os.path.join(pluginDir, item)
            if os.path.isdir(location):
                if loop:
                    plugins.extend(self.findPlugins(pluginDir=location, loop=loop))
                continue
            elif os.path.isfile(location) and suffix == ".py" and moduleName != "__init__":
                info = imp.find_module(moduleName, [pluginDir])
            else:
                continue
            plugins.append({"name": moduleName, "info": info, "md5": md5Sum(location)})
        return plugins
    
    # 加载plugin。调用findPlugins查找可用plugin并加载
    def loadPlugins(self, pluginDir=None, loop=None):
        for plugin in self.findPlugins(pluginDir=pluginDir, loop=loop):
            try:
                module = {"module": imp.load_module(plugin["name"], *plugin["info"]), "md5": plugin["md5"]}
                self.plugins[plugin["name"]] = module
            finally:
                if plugin["info"][0]:
                    plugin["info"][0].close()
        
        return self.plugins
    
    # 查找module
    def findPlugin(self, pluginDir=None, moduleName=None, loop=False):
        """查找moduleName，并计算md5
        
        入参：
            pluginDir: 插件目录
            moduleName: 要查找的模块名称
            loop: 如果导入模块是包，是否递归导入子包
        """
        # 构建寻找路径
        if pluginDir:
            location = os.path.join(pluginDir, moduleName)
        else:
            location = os.path.join(self.pluginDir, moduleName)
        # 合法性校验
        if not (os.path.isfile(location) or os.path.isdir(location)):
            return False, "file or dir not exist"
        # 模块导入
        try:
            fd, pathName, des = imp.find_module(moduleName, [location])
        except ImportError as e:
            return False, e
        # 判断是否递归导入
        if not fd and des[2] == imp.PKG_DIRECTORY and loop:
            self.findPlugin(pluginDir=pathName, moduleName=moduleName, loop=loop)
        # 插件信息
        plugin = {"name": moduleName, "info": (fd, pathName, des), "md5": md5Sum(location + des[0])}
        return True, plugin
    
    # 加载module
    def loadPlugin(self, pluginDir=None, moduleName=None, loop=False):
        """加载module。如果没有加载过或有更新，则重新加载，否则直接返回self.plugins中保存的
        
        入参：
            pluginDir: 插件目录
            moduleName: 要导入的模块名称
            loop: 如果导入模块是包，是否递归导入子包
        """
        ok, plugin = self.findPlugin(pluginDir=pluginDir, moduleName=moduleName, loop=loop)
        if not ok:
            return ok, plugin
        
        try:
            if plugin["name"] not in self.plugins:  # 新增模块
                self.plugins[plugin["name"]] = {}
                self.plugins[plugin["name"]]["module"] = imp.load_module(plugin["name"], *plugin["info"])
                self.plugins[plugin["name"]]["md5"] = plugin["md5"]
            elif plugin["md5"] != self.plugins[plugin["name"]]["md5"]:  # 更新模块
                self.plugins[plugin["name"]]["module"] = imp.load_module(plugin["name"], *plugin["info"])
                self.plugins[plugin["name"]]["md5"] = plugin["md5"]
        except ImportError:
            return False, None
        finally:
            if plugin["info"][0]:
                plugin["info"][0].close()
        return True, self.plugins[plugin["name"]]["module"]
