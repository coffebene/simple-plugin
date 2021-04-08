#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
该模块用于实现插件热插拔
使用方式有以下两种：
1. loadPlugins 自动导入插件
    如果是自动导入插件，那么模块的顺序会影响插件执行顺序！！！
2. loadPlugin 手动导入插件
    如果是手动导入插件，那么手动导入的顺序会影响插件运行顺序！！！
"""

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
    
    def __init__(self, pluginDir=None):
        self.plugins = []  # 存放加载的模块信息,使用列表是因为列表有序
        if pluginDir and not os.path.isdir(pluginDir):
            raise ValueError("%s must be dir" % pluginDir)
        self.pluginDir = pluginDir  # 模块路径
    
    # 返回插件名称
    @property
    def pluginsName(self):
        pluginName = [i.keys()[0] for i in self.plugins]
        return pluginName
    
    # 查找可导入的module
    def findPlugins(self, pluginDir=None, loop=False):
        """遍历目录，查找可导入plugin
        参数：
            pluginDir: 查找路径
            loop: 是否在子目录中递归加载插件
        """
        plugins = []
        if not (pluginDir and os.path.isdir(pluginDir)):
            pluginDir = self.pluginDir
        # 遍历目录
        for item in os.listdir(pluginDir):
            # 文件拆分为文件名和后缀
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
        newPlugins = self.findPlugins(pluginDir=pluginDir, loop=loop)
        # 删除已卸载的插件，加载新的插件
        plugins = []
        for plugin in newPlugins:
            newPlugin = {}
            try:
                p = {"module": imp.load_module(plugin["name"], *plugin["info"]), "md5": plugin["md5"]}
                newPlugin[plugin["name"]] = p
            except ImportError:
                continue
            else:
                plugins.append(newPlugin)
            finally:
                if plugin["info"][0]:
                    plugin["info"][0].close()
        self.plugins = plugins
        return self.plugins
    
    # 查找module
    def findPlugin(self, pluginDir=None, moduleName=None, loop=False):
        """查找moduleName，并计算md5。如果开启了递归查找，则采用深度优先算法查找模块。
        
        入参：
            pluginDir: 插件目录
            moduleName: 要查找的模块名称
            loop: 如果父目录不存在该模块，是否在子目录中递归查找
        """
        ok, plugin = False, {}
        # 构建寻找路径
        if not (pluginDir and os.path.isdir(pluginDir)):
            pluginDir = self.pluginDir
        # 模块导入
        try:
            fd, pathName, des = imp.find_module(moduleName, [pluginDir])
            plugin = {"name": moduleName, "info": (fd, pathName, des), "md5": md5Sum(pathName)}
            ok = True
        except ImportError as e:
            if not loop:
                return False, e
            for item in os.listdir(pluginDir):
                location = os.path.join(pluginDir, item)
                if os.path.isdir(location):
                    ok, plugin = self.findPlugin(pluginDir=location, moduleName=moduleName, loop=loop)
                    if ok:
                        return ok, plugin
        return ok, plugin
    
    # 加载module
    def loadPlugin(self, pluginDir=None, moduleName=None, loop=False):
        """加载module。如果没有加载过或有更新，则重新加载，否则直接返回self.plugins中保存的
        
        入参：
            pluginDir: 插件目录
            moduleName: 要导入的模块名称
            loop: 如果父目录不存在该模块，是否在子目录中递归查找
        """
        ok, plugin = self.findPlugin(pluginDir=pluginDir, moduleName=moduleName, loop=loop)
        # 如果不存在模块，则删除之前的缓存
        pluginsName = self.pluginsName
        if not ok:
            if moduleName in pluginsName:
                self.delete(moduleName)
            return ok, plugin
        try:
            newPlugin = {}
            if plugin["name"] not in pluginsName:  # 新增模块
                newPlugin = {"module": imp.load_module(plugin["name"], *plugin["info"]), "md5": plugin["md5"]}
                self.plugins.append({plugin["name"]: newPlugin})
            else:  # 更新模块
                for i in self.plugins:
                    for name, moduleInfo in i.items():
                        if name == plugin["name"]:
                            if moduleInfo["md5"] != plugin["md5"]:
                                newPlugin = {"module": imp.load_module(plugin["name"], *plugin["info"]),
                                             "md5": plugin["md5"]}
                                i[name] = newPlugin
                            else:
                                newPlugin = moduleInfo
        except ImportError:
            return False, None
        finally:
            if plugin["info"][0]:
                plugin["info"][0].close()
        return True, newPlugin
    
    # 删除插件
    def delete(self, moduleName):
        if moduleName not in self.pluginsName:
            return
        for plugin in self.plugins:
            if plugin.keys()[0] == moduleName:
                self.plugins.remove(plugin)
                return
