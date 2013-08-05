#-*- coding:utf-8 -*-
'''
====================================================================================

   Copyright 2013, 2014 Windy Darian (大地无敌), Studio "Sekai no Kagami" 
   (世界之镜制作组) of Seven Ocean Game Arts （七海游戏文化社
   , 北京航空航天大学学生七海游戏文化社） @ http://sogarts.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

====================================================================================
Created on April 5, 2013
A moudle that contains color themes
@author: Windy Darian (大地无敌)
'''

import direct.gui.DirectGuiGlobals as DGG

system_text = {'scale':0.07,
               'fg':(1,1,1,1),
               'shadow':(0.6,0.6,0.5,1),
               }

ilia_textbox = {'background_color' : (36/255.0,195/255.0,229/255.0,0.3),
                'arrow_color' : (1,1,1,1),
                'arrow_scale' : 0.08,
                'arrow_rightspace' : 0.18,
                'foreground_color' : (1,1,1,1),
                'normal_background_image':None,
                'normal_height': 0.6,
                'normal_width': 2.6666667,
                'normal_pos': (0,-0.65),
                'normal_name_pos' : (0.14,-0.12),
                'normal_text_pos' : (0.25,-0.25),
                'normal_text_scale' : 0.09,
                'normal_name_scale' : 0.07,
                'normal_text_wrap' : 24,
                'large_background_image':None,
                'large_height': 1.9,
                'large_width' :2.3,
                'large_pos': (0,0),
                'large_text_pos': (0.18,-0.25),
                'large_text_scale' : 0.08,
                'large_name_scale' : 0.06,
                'large_text_wrap' : 24,
               }

ilia_frame = {'frameColor': (36/255.0,195/255.0,229/255.0,0.3),
              'relief': DGG.FLAT
              }

ilia_button = {'frameColor':((42/255.0,195/255.0,239/255.0,0.75),
                             (1.0,1.0,1.0,1),
                             (72/255.0,235/255.0,255/255.0,0.95),
                             (0.5,0.5,0.5,0.75),),
                'text_scale':0.07,
                'text_fg':(1,1,1,1),
                'text_shadow':(0.5,0.5,0.5,1),
                'relief': DGG.FLAT
                
              }

sirius_frame = {'frameColor': (230/255.0,194/255.0,35/255.0,0.3),
                'relief': DGG.FLAT
              }

sirius_button = {'frameColor':((239/255.0,195/255.0,46/255.0,0.75),
                             (1.0,1.0,1.0,1),
                             (249/255.0,235/255.0,85/255.0,0.95),
                             (0.5,0.5,0.5,0.75),),
                 'text_scale':0.07,
                 'text_fg':(1,1,1,1),
                 'text_shadow':(0.5,0.5,0.5,1),
                 'relief': DGG.FLAT
                
                }
