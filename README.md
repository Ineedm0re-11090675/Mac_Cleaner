# macOS Cleaner Demo

这是一个适合初学者继续扩展的 macOS 清理工具练习项目。

项目的分工很简单：

- `C++`：负责扫描文件、统计大小、执行基础删除
- `Python`：负责本地网页服务、系统接口、打开访达、管理启动项
- `浏览器页面`：负责展示结果、勾选文件、触发删除

你可以把它理解成：

- `C++` 是“干活的人”
- `Python` 是“翻译和调度的人”
- `网页` 是“给人看的控制台”

## 现在能做什么

当前已经有 8 个主功能：

1. `全面检查`
   - 把所有功能压成一页快速总览
   - 每个功能只显示最值得你优先处理的几项
   - 可以直接勾选这些项目
   - 支持一键处理当前勾选的总览项目
   - 如果某个模块没有明显问题，会显示“状态良好”

2. `文件清理`
   - 基础清理：用户缓存、用户日志、废纸篓
   - 候选文件：重复文件、长期未使用的大文件
   - 安装文件：`DMG / PKG / 安装压缩包`
   - 下载文件：`Downloads` 中体积较大或长期未使用的文件
   - 大型文件 Top 10

3. `软件缓存`
   - 浏览器缓存：Chrome / Edge / Firefox / Safari
   - 常见软件缓存：网易云音乐 / 微信 / QQ / 钉钉
   - 支持在访达中定位文件

4. `开机启动`
   - 登录项
   - 后台项目（用户级 LaunchAgent）
   - 可以关闭你勾选的项目

5. `应用程序`
   - 扫描“已卸载应用可能留下的残留文件”
   - 会显示风险等级
   - 支持在访达中显示后再决定是否删除

6. `内存管理`
   - 扫描当前用户中占用较高的进程
   - 显示：进程名 / 内存占用 / CPU 占用 / 是否后台进程
   - 给出风险等级和关闭建议
   - 支持选择性结束进程

7. `图片管理`
   - 统一整理截图、下载图片、相似图片、完全重复图片、大图 / 长期未使用图片
   - 支持图片预览
   - 支持在访达中显示、直接打开、勾选删除

8. `磁盘空间`
   - 统计 Desktop / Downloads / Documents / Library 的空间占用
   - 显示每个根目录里最占空间的子目录 / 文件
   - 单独列出最占空间的大文件，支持勾选删除

另外，现在还新增了一套独立的 `PySide6` 客户端骨架：

- 浏览器版继续保留
- 客户端骨架放在 `python/desktop_app/`
- 这套骨架的作用是让你以后可以慢慢把网页版能力迁移成真正桌面客户端

## 你最常用的运行方式

先进入项目目录：

```bash
cd /path/to/codex_demo
```

编译 C++ 核心：

```bash
mkdir -p build
clang++ -std=c++17 -Icpp/include cpp/src/main.cpp cpp/src/cleaner.cpp -o build/mac_cleaner
```

启动本地网页界面：

```bash
python3 python/gui.py
```

运行后终端会打印一个本地地址，例如：

```text
Open in browser: http://127.0.0.1:55669/
```

浏览器通常会自动打开。如果没有自动打开，就把这个地址复制到浏览器里。

现在页面是按路由切分的，你可能会看到这样的地址：

```text
#/files
#/caches
#/startup
#/memory
#/images
#/space
#/applications
#/overview
```

这表示你正在不同的功能页里，不是报错。

## 可选：启动 PySide6 客户端骨架

这套客户端骨架不会替换浏览器版，它只是并行存在的一套桌面 UI 练习工程。

先安装 `PySide6`：

```bash
pip3 install PySide6
```

然后运行：

```bash
python3 python/desktop_app/main.py
```

如果你想直接双击桌面图标来启动客户端，可以运行：

```bash
chmod +x scripts/build_desktop_launcher.sh
./scripts/build_desktop_launcher.sh
```

它会做两件事：

- 在 `~/Applications` 里生成一个 `macOS Cleaner.app`
- 在桌面再放一个同样可双击的入口

这样你就不用每次再进终端手动执行 `python3 python/desktop_app/main.py` 了。

如果你想把它打包成一个可以发给朋友的独立应用，可以运行：

```bash
chmod +x scripts/build_shareable_app.sh
./scripts/build_shareable_app.sh
```

打包完成后会生成：

- `dist/macOS Cleaner.app`
- `dist/macOS Cleaner-macOS.zip`
- 桌面副本：`~/Desktop/macOS Cleaner-macOS.zip`

这样发给朋友时，通常直接发这个 zip 就够了。
如果你准备把项目开源到 GitHub，推荐把源码和 `dist/macOS Cleaner-macOS.zip` 一起放进仓库，
这样别人不需要本地先安装依赖、再自己重新打包，就可以直接下载桌面端成品试用。

注意：

- 这是未 notarize 的开发版应用
- 朋友第一次打开时，macOS 可能会拦一下
- 一般可以通过“右键 -> 打开”进入
- 如果对方是 Intel Mac，而你当前打包出来的底层 C++ 二进制不是通用架构，可能会遇到兼容性问题

它现在已经有：

- 左侧导航
- 七个页面
- 全面检查 / 文件清理 / 图片管理 / 磁盘空间 / 软件缓存 / 开机启动 / 应用程序 / 内存管理
- 大部分页面已经能扫描、勾选、查看详情和执行操作

它还不是商业级桌面版，但已经不是空骨架了。

## 这个项目的大概结构

如果你是新手，不需要一开始把所有文件都看懂。先知道下面这几个最重要的文件就够了：

```text
cpp/include/cleaner.hpp         C++ 头文件，定义数据结构
cpp/src/cleaner.cpp             C++ 核心扫描和删除逻辑
cpp/src/main.cpp                C++ 命令行入口
python/bridge.py                Python 调用 C++ 二进制
python/gui.py                   本地网页服务入口
python/desktop_app/main.py      PySide6 客户端入口
python/desktop_app/window.py    PySide6 主窗口和页面骨架
python/startup_manager.py       启动项管理
python/application_manager.py   应用残留扫描与删除
python/memory_manager.py        内存占用分析与结束进程
python/image_manager.py         图片扫描、分组和预览图生成
python/disk_manager.py          磁盘空间统计和大文件列表
python/webui/index.html         页面结构
python/webui/app.js             页面交互逻辑
python/webui/style.css          页面样式
```

## 几个常见概念

### 1. 基础清理

这里指的是：

- `~/Library/Caches`
- `~/Library/Logs`
- `~/.Trash`

它是“按目录清理”。

### 2. 候选文件

这里不是系统直接认定的垃圾，而是“值得你手动确认的文件”，比如：

- 重复文件
- 很久没动过的大文件
- 安装包
- 下载目录中的旧文件

所以它更像“建议清理”，不是“一键全删”。

### 3. 在访达中显示

这个按钮不会删除文件，只会帮你在 Finder 里定位它。  
这个功能很重要，因为你常常要先看清楚它到底是什么，再决定要不要删。

### 4. 后台项目

这里主要是用户级 `LaunchAgent`。  
你可以简单理解成：“登录后会自动运行的后台任务”。

### 5. 连续选择

现在浏览器版和桌面端都支持更顺手的范围选择：

- 先点中一个文件
- 按住 `Shift`
- 再点另一个文件

中间这一段会一起被勾选。这样适合你连续处理很多文件时使用。

浏览器版还额外支持：

- 在复选框这一列按住左键
- 向上或向下拖动

拖过的行会连续勾选，更接近 Finder 里连续选中的感觉。

## 安全提醒

这个项目已经尽量做保守处理，但它不是商业级安全产品，所以你仍然要养成下面这个习惯：

- 不确定的文件先点“在访达中显示”
- 看清路径和内容后再删
- 高风险的应用残留先确认，再删除

当前版本默认不去碰这些内容：

- 系统目录
- 浏览器 cookies
- 微信 / QQ / 钉钉聊天正文数据库

## 如果你想继续学习

一个适合新手的阅读顺序是：

1. 先看 `python/gui.py`
   - 理解网页接口是怎么接进来的

2. 再看 `python/bridge.py`
   - 理解 Python 是怎么调用 C++ 的

3. 再看 `cpp/src/main.cpp`
   - 理解命令行参数怎么转成 JSON 输出

4. 最后看 `cpp/src/cleaner.cpp`
   - 理解真正的扫描规则和删除逻辑

这样不会一开始就被大文件吓住。
