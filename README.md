# Rommer 

游戏 ROM 整理以及元数据下载工具

## Roadmap

- 基础元数据文件处理
    - [x] 解析 rdb 元数据文件
    - [x] 解析 no-intro dat 元数据文件
    - [x] 解析 redump dat 元数据文件
    - [x] 解析 MAME 元数据文件
    - [x] 自动下载基础元数据文件
- 元数据匹配
    - [x] 文件名模糊匹配
    - [x] 序列号匹配
    - [x] 哈希匹配
    - [x] 手动文件名映射
- ROM 过滤 (实时下载元数据，不自己维护)
    - [ ] 根据 rom 语言过滤
    - [ ] 根据 rom 地区过滤
    - [ ] 根据 rom 版本过滤
    - [ ] 根据文件列表过滤
- 添加媒体元数据源
    - [x] libretro thumbnails
    - [ ] gamefaqs
    - [ ] gametdb
    - [ ] launchbox
    - [ ] screenscraper
- 封面标准化处理
    - [ ] 添加统一遮罩
    - [ ] 自动统一尺寸
    - [ ] 卡带型游戏输出卡带样式图片
- 游戏文件整理
    - [x] 解析常见压缩文件
    - [x] N64 游戏转为 Big Endian
    - [ ] PSP 游戏转为 CSO 格式
    - [ ] ROM 单独打包成压缩文件
    - [ ] 光盘类 ROM 压缩为 CHD
    - [ ] 按照不同的前端输出不同的文件结构

## 工作流程

首先指定一个游戏 rom 文件夹，并指定此文件夹对应的游戏主机类型，在指定之后程序将会扫描文件夹中的所有 rom，针对不同的游戏主机类型，会有不同的处理逻辑

然后是加载对应的基础元数据文件，不同的元数据文件包含的信息不同，但一般都包含游戏的名称、哈希值、序列号等

之后 rom 文件和元数据文件会进行匹配，这一步用于获得 rom 的标准英文名称

具体的匹配逻辑分为三种：哈希匹配、序列号匹配、文件名匹配，三种匹配的准确性依次递减

匹配后需要下载补充元数据，但无需下载游戏对应的图片视频等信息，主要包括游戏名称、发行商、发行日期、游戏类型等

根据获得的元数据，可以进一步对 rom 进行过滤，例如只保留游戏的某一版本，或者只保留某一地区的游戏等

过滤后下载 rom 对应的封面图片等媒体数据

最后，针对不同的前端以及需求，输出不同的文件结构，或者对文件进行进一步的处理

对于汉化游戏，需要一些额外步骤

由于汉化游戏的哈希值与原版游戏不同，所以需要通过其他方式匹配元数据

第一种方式是通过序列号匹配，汉化游戏一般不会改变游戏的序列号，所以这种方式一般适用于卡带游戏如 GBA、NDS，PSP 也包含序列号信息，因此可以用于匹配

但仍然有很多游戏缺乏序列号信息，此时需要手动创建一个映射文件，将汉化游戏的文件名与原版游戏的文件名进行映射，然后通过文件名匹配的方式进行匹配

之后的步骤与原版游戏相同

## 支持平台

目前只支持到第六代主机

- Atari
    - Atari 2600 (516)
    - Atari 5200 (69)
    - Atari 7800 (59)
    - Atari Jaguar (50)
    - Atari Jaguar CD (13)
    - Atari Lynx (71)
- Bandai
    - Bandai WonderSwan (109)
    - Bandai WonderSwan Color (91)
- Microsoft
    - MSX
    - MSX2
    - Microsoft Xbox
- NEC
    - NEC PC Engine
    - NEC PC Engine CD
    - NEC PC-FX
    - NEC SuperGrafx
- Nintendo
    - Nintendo Entertainment System
    - Nintendo Famicom Disk System
    - Nintendo Super Nintendo Entertainment System
    - Nintendo 64
    - Nintendo GameCube
    - Nintendo Wii
    - Nintendo Wii U
    - Nintendo Game&Watch
    - Nintendo Pokemon Mini
    - Nintendo Game Boy
    - Nintendo Game Boy Color
    - Nintendo Game Boy Advance
    - Nintendo DS
    - Nintendo 3DS
- Sega
    - Sega 32X
    - Sega CD
    - Sega Dreamcast
    - Sega Game Gear
    - Sega Genesis
    - Sega Master System
    - Sega Saturn
    - Sega Mega Drive
- SNK
    - SNK Neo Geo Pocket
    - SNK Neo Geo Pocket Color
- Sony
    - Sony PlayStation
    - Sony PlayStation 2
    - Sony PlayStation Portable

## 其他工具

### parserdb

解析 rdb 文件, 输出为 json 格式或 sqlite3 格式