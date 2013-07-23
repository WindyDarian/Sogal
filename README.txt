=================================================================
介绍
=================================================================
SOGAL(Seven Ocean Galgame Engine)是基于panda3d的一个Galgame框架，由
七海游戏文化社(北京航空航天大学学生七海游戏文化社)开发

当前版本基于Panda3d 1.8.1、python 2.7 
反正现在运行还是黑框懒得写了

主要就是使用了自制的Galgame脚本格式方便开发

==================================================================
脚本格式说明
==================================================================


#TODO: 快把说明写完
#TODO: Translate it into English (and Japanese?)

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
p 格式中用来清空已有字符 ，large文本框用
textbox -propname -content 改变文本框属性，content可以有空格，会在脚本命名空间中eval计算(也就是如果是字符串要加引号)，参考game_text_box.py中GameTextBox.properties
textbox apply 应用文本框属性的修改，会清空文本

未实现（加#表示暂不忙实现）：
打字机效果外加线性框架！
sreset 重置场景。停止音乐、移除所有立绘。用于初始化和场景切换
              隐藏UI、绘制黑色顶层画面
sreset -Time -FileName 重置场景。以一定速度渐入某个到中间顶层图片，同时淡出音乐并移除立绘
                                               隐藏UI                                         
sstart -Time -SceneName 开始新场景 SceneName是场景名自取。在开始场景之前先用bgchange改变背景
                                                然后就可以在Time的时间内淡去顶层图片
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

pic -PicKeyword -fileName -Location  在指定位置显示立绘 Location 0 0表示正中
                                     1 1表示右上 注意除了Location都不能有空格
                                     -相同的Keyword会直接替换
pic -PicKeyword -fileName 显示立绘，如果已存在，其会在当前位置用新图片替代
                         -否则绘制在正中
ploc -PicKeyword -Location 改变立绘位置
qp -fileName -Location   快速立绘！在进入下一个文本段时就会自动消失！
pdel -PicKeyword  移除立绘
pclear 移除所有立绘
bg -FileName  改变背景
bg -FileName -Time 交叉淡入淡出改变背景

load -FileName 读取sogal场景脚本文件并添加到事件队列
script   表示接下来的文本段是python脚本（注意其中不能有空行）
script -FileName 运行python脚本文件
选择
循环

