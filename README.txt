=================================================================
介绍
Introduction
=================================================================
SOGAL(Seven Ocean Galgame Engine)是基于panda3d的一个Galgame框架，由
世界之镜制作组的大地无敌(http://www.agrp.info)发起，供世界之
镜制作组的第一款游戏使用。

世界之镜制作组是七海游戏文化社(http://sogarts.com，北京航空航天大学学
生七海游戏文化社)的一个独立工作室

我们的第一个游戏的故事部分会使用SOGAL，敬请期待

使用的开源协议是Apache License, Version 2.0，详见LICENSE.txt
因为使用的是Apache License所以只要记得包含窝们的原协议就可以随便用

当前版本基于Panda3d 1.8.1、python 2.7 
反正现在运行还是黑框懒得写了

主要就是使用了自制的Galgame脚本格式方便开发

现在只能显示出一个文本框（你知道得太多了！腹黑脸）

SOGAL(Seven Ocean Galgame Engine) is a panda3d based Galgame framework.
It is started by Windy Darian (or 大地无敌 , http://www.agrp.info(Chinese)) 
of Studio "Sekai no Kagami".

Studio "Sekai no Kagami" is an independent game develop studio
of Seven Ocean Game Arts(SOGA, a student group of Beijing University of 
Astronautics and Aeronautics, http://sogarts.com(Chinese).

We are going to develop use this in our first game. 

SOGAL is under Apache License V2.0, so feel free to use it. Just remember
to include the original license file.

It is based on Panda3d 1.8.1 and Python 2.7 

(But it only prints a textbox based on current scene file yet lol)

Windy Darian（大地无敌）
http://www.agrp.info(Chinese)
p123456638@gmail.com
Jul 23, 2013

#TODO: 快把说明写完
#TODO: Translate it into English (and Japanese?)

==================================================================
如何运行
How to run it?
==================================================================
还在开发阶段 不打算整个打包
所以安装好Panda3D后 使用Panda3D中带的Python执行 develop.py即可

For SOGAL is far from completion, just run develop.py with
the Python in Panda3D:

python develop.py

Panda3D 1.8.1 download at http://www.panda3d.org
==================================================================
如果要来战的话Eclipse和PyDev的设置
How to set up Eclipse and PyDev
==================================================================

嘛如果想在Eclipse中玩的话……

1、在Eclipse中安装PyDev
在Eclipse中选择Help -> Install New Software 然后输入
http://pydev.org/updates安装PyDev
2、在PyDev设置Panda3D环境
参见http://www.panda3d.org/forums/viewtopic.php?t=10659与其相关帖子
为了方便自动完成代码和摆脱那些恶心的PyDev傲娇错误提示，需要添加引用的predef
在EclipseSetUp里
3、安装eGit和GitHub Mynlyn支持
Help -> Install New Software中分别安装http://download.eclipse.org/egit/updates
和http://download.eclipse.org/egit/github/updates/的所需内容
4、进入Eclipse然后在Window->Show View->Others里面打开Git Repositories视图。
然后在视图中将Sogal Clone到本地，将eclipseSetUp.7z里的文件放到Repository目录
然后就能在Eclipse中用Import Projects导入项目进行修改了！

1.Installing PyDev in Eclipse
2.Setting up panda3D in PyDev
Thanks to http://www.panda3d.org/forums/viewtopic.php?t=10659，and the pypredef is here(run away
3.Installing eGit and GitHub support in Eclipse.
EGit P2 Repository - http://download.eclipse.org/egit/updates
Eclipse EGit Mylyn GitHub Repository - http://download.eclipse.org/egit/github/updates/
4.Clone this Repository to local, then extract eclipseSetUp.7z to local repository folder
Then you can right click this repository name in Eclipse git repositories view and 'Import Projects' to import it as a local PyDev project


Windy Darian（大地无敌）
http://www.agrp.info(Chinese)
p123456638@gmail.com
Jul 23, 2013

==================================================================
脚本格式说明
==================================================================

脚本在scene中以.sogal格式存储
注意文件编码统一用UTF-8
而且最好不要用Windows记事本直接编辑因为它存的UTF8好像会有奇怪的标记然后
别的系统可能不认
（嘛窝这边是Visual Studio和Eclipse都用的

关于资源的放置：
图片（背景、立绘、CG）应以png24形式放在images中
anm 播放的panda3D egg格式2d动画也应放在images中
所有声音相关资源在audio中

备忘：
转义符
__在行前可以表示这是一个文本中的空行
\: \：表示这是一个英文或中文冒号而不是名称表达的简化形式
\# 表示是#而非注释

命令列表 
命令写在命令段中（整个命令段以@开头 命令段中以,分隔不同的命令）
注意文件名都不能加空格，以后会考虑能用引号包含

TODO:在StoryManager中实现背景、立绘、声音的支持，注意要考虑到要从某个存档文件中读取背景和立
绘的情况

已实现
name = -Name    设置名字 可以有空格
name -Name   设置名字 可以有空格
文本段中开头-Name: 或-Name：（中文冒号）  设置名字的简化形式
textboxstyle normal/large 改变文本框格式，会清空文本
p 格式中用来清空已有字符 ，large文本框用,注意和显示图片的p的区别是它不带任何参数
textbox -propname -content 改变文本框属性，content可以有空格，会在脚本命名空间中eval计算(也就是如果是字符串要加引号)，参考game_text_box.py中GameTextBox.properties
textbox apply 应用文本框属性的修改，会清空文本

p -key -fileName -x -z (-s) (-fadein)  在指定位置显示立绘位置 0 0表示正中
                                     1 1表示右上 注意除了Location都不能有空格
                                     -相同的Keyword会直接替换 也可以有三个数字代表x y z
                                   
p -key -fileName 显示立绘，如果已存在，其会在当前位置用新图片替代
                         -否则绘制在正中
bg -FileName  立即改变背景
ploc -key -x -z 改变立绘位置 Location应该是两个数字 x z（或是3个x y z）
pcolor -key -r -g -b -a  rgba范围都在0到1
pscale -key -s 缩放
pdel -key  移除立绘
vclear 重置场景。移除所有立绘，将背景设置为黑色。用于初始化和场景切换
o3d -key -fileName -x -y -z -r -g -b -a -sx -sy -sz 显示3D模型，x轴向由 y轴向屏幕内 z轴向上 大小自己看着办吧
o2d -key -fileName -x -y -z -r -g -b -a -sx -sy -sz 在3D中显示2D图片
pa -key -fileName -x -z -sx -sy (-f) 显示egg动画在前景注意动画要手动缩放宽高比

未实现（加#表示暂不忙实现）：
打字机效果外加线性框架！
vclear -Time 重置场景。在一定时间内淡出到黑色
vclear -Time -bgFileName重置场景。以一定速度渐入到某个背景图片，移除所有场景
audio -FileName    播放音频一次
audio3d -FileName -Location 
audiostop    停止当前所有audio播放的音效
music -FileName    循环播放音乐使用默认淡入淡出设置
music -FileName -Time    Time为淡入或音乐交换用时间（所有时间以秒为单位）
se -FileName	循环播放SE
se -FileName -Time  	淡入或交叉SE
sestop	停止SE
sestop -Time	淡出SE
voice -FileName	语音
voice3d -FileName -Location 3d语音 
wait -Time	等待直到队列中的下一行能够被执行 注意快速播放和人工操作能够打破等待状态
mstop    立即停止当前音乐
mstop -Time    淡出当前音乐，Time为淡出时间
bg -FileName -Time 交叉淡入淡出改变背景   
qp -fileName -Location   快速立绘！在进入下一个文本段时就会自动消失！
pclear 移除所有立绘
load -FileName 读取sogal场景脚本文件并添加到事件队列
script   表示接下来的文本段是python脚本（注意其中不能有空行）
script -FileName 运行python脚本文件
选择
循环

