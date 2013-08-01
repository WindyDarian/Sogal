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
Created on Jul 29, 2013
Audio manager.
@author: Windy Darian （大地无敌）@ http://www.agrp.info 
'''
from panda3d.core import AudioSound,AudioManager
from direct.showbase.DirectObject import DirectObject
from direct.interval.LerpInterval import LerpFunc
from direct.interval.FunctionInterval import Func,Wait
from direct.interval.IntervalGlobal import Sequence
from direct.stdpy.file import exists    #use panda3d's file API to support panda's virtual folder

from runtime_data import game_settings,RuntimeData

_fadeinIntervalTable = {}
_intervals = []

def play_audio(audio,fadein = 0, volume = 1, loop = False):
    '''plays an AudioSound'''
    if loop:
        audio.setLoop(True)
    if not fadein:
        audio.setVolume(volume)
        audio.play()
    else:
        interval = LerpFunc(_lerpAdjust, duration = fadein,
                            fromData = 0, toData = volume,
                            extraArgs = [audio], blendType = 'easeOut')
        _fadeinIntervalTable[audio] = interval   
        _intervals.append(interval)    
            #save the interval in the table so if the audio stops during the interval it can stop the interval first
        audio.play()
        interval.start()
        
    
def stop_audio(audio,fadeout = 0):
    '''stops an AudioSound, instant or fade-out'''
    if _fadeinIntervalTable.has_key(audio):     #If the audio is currently on fade-in, then stop and remove the fade-in interval
        _fadeinIntervalTable[audio].pause()
        _intervals.remove(_fadeinIntervalTable[audio])
        del _fadeinIntervalTable[audio]
           
    if not fadeout:
        audio.stop()
    else:
        sequence = Sequence(LerpFunc(_lerpAdjust, duration = fadeout,
                                     fromData = audio.getVolume(), toData = 0,
                                     extraArgs = [audio], blendType = 'easeIn'),
                            Func(audio.stop)
                            )
        sequence.start()  #reduce volume and stop the sound
        
        
def play(filepath, manager, loop = False, fadein = 0, volume = 1):
    '''load a sound in background, and play it when loading finishes'''
    loader.loadSound(manager,
                     filepath,
                     callback = play_audio,extraArgs = [fadein, volume, loop])    
    

def _lerpAdjust(volume,audio):
    '''Adjust the volume dynamiclly in fadein and fadeout'''
    audio.setVolume(volume)
    
_bgmMgr = None
_envMgr = None
_voiceMgr = None
_sfxMgr = None

class AudioPlayer(DirectObject):
    
    '''Audio Player class of Sogal
    usually there only need 1 instance
    '''
    def __init__(self):
        DirectObject.__init__(self)
        
        global _bgmMgr,_envMgr,_sfxMgr,_voiceMgr    
        '''if we already has an AudioPlayer instance,
           we just need to refer to the existing AudioManagers
           insead of creating some new ones'''
        if not _bgmMgr:
            _bgmMgr = AudioManager.createAudioManager()          #don't use ShowBase.musicManager for it can only play 1 music at the same time defaultly so it don't support cross-fade
            base.addSfxManager(_bgmMgr)
        if not _envMgr:
            _envMgr = AudioManager.createAudioManager()
            base.addSfxManager(_envMgr)
        if not _voiceMgr:
            _voiceMgr = AudioManager.createAudioManager()
            base.addSfxManager(_voiceMgr)
        if not _sfxMgr:
            _sfxMgr = AudioManager.createAudioManager()
            base.addSfxManager(_sfxMgr)
            
        self.bgmMgr = _bgmMgr
        self.envMgr = _envMgr
        self.voiceMgr = _voiceMgr
        self.sfxMgr = _sfxMgr
        
        self.applySettings()
        
        self._currentBGM = None #to define there can only be one bgm
        self._currentENV = None # and one environment sound at the same time
        
        '''#test1 Load and play a music
        loader.loadSound(self.bgmMgr,
                         'audio/music/God-only-knows-Secrets-of-the-Goddess-.wav',
                         callback = play_audio,extraArgs = [3,1])
        '''
        '''#test2 A fade-out stop before the fade-in is completed
        sound = loader.loadSound(self.bgmMgr,'audio/music/God-only-knows-Secrets-of-the-Goddess-.wav')
        sq = Sequence(Func(play_audio,sound,10),Wait(5),Func(stop_audio,sound,5))
        sq.start()
        '''
        '''#test3  Load and play a music
        self.playBGM('church-organ-music', 2, 1, True)
        '''
        '''#test4 Another music before the fade-in is completed
        sq = Sequence(Func(self.playBGM,'God-only-knows-Secrets-of-the-Goddess-',10),
                      Wait(5),
                      Func(self.playBGM,'church-organ-music',10),
                      )
        sq.start()
        '''
        
        
#     def destroy(self):
#         self.ignoreAll()
        
    def applySettings(self):
        self.bgmMgr.setVolume(game_settings['music_volume'])
        self.envMgr.setVolume(game_settings['env_volume'])
        self.voiceMgr.setVolume(game_settings['voice_volume'])
        self.sfxMgr.setVolume(game_settings['sfx_volume'])
        
        
    def playVoice(self, path, volume = 1):    
        pathes = game_settings['voicepathes']
        types = game_settings['soundtypes']
        for ft in ((folder,type) for folder in pathes for type in types):
            if exists(ft[0] + path + ft[1]):
                path = ft[0] + path + ft[1]
                break
        play(path, self.voiceMgr, volume = volume)
    
    def playSound(self, path, volume = 1):
        pathes = game_settings['sfxpathes']
        types = game_settings['soundtypes']
        for ft in ((folder,type) for folder in pathes for type in types):
            if exists(ft[0] + path + ft[1]):
                path = ft[0] + path + ft[1]
                break
        play(path,self.sfxMgr, volume = volume)
        
    def playBGM(self, path, fadein = 0, volume = 1, loop = True):
        if self._currentBGM:    #if there is a music playing then stop it
            self.stopBGM(fadein)
        RuntimeData.current_bgm = [path,fadein,volume,loop] #save for loading
        pathes = game_settings['musicpathes']
        types = game_settings['soundtypes']
        for ft in ((folder,type) for folder in pathes for type in types):
            if exists(ft[0] + path + ft[1]):
                path = ft[0] + path + ft[1]
                break
        loader.loadSound(self.bgmMgr,
                     path,
                     callback = self._setAndPlayBGM,extraArgs = [fadein, volume, loop]) 
          
    
    def playENV(self, path, fadein = 0, volume = 1, loop = True):
        if self._currentENV:
            self.stopENV(fadein)
        RuntimeData.current_env = [path,fadein,volume,loop]
        pathes = game_settings['envsoundpathes']
        types = game_settings['soundtypes']
        for ft in ((folder,type) for folder in pathes for type in types):
            if exists(ft[0] + path + ft[1]):
                path = ft[0] + path + ft[1]
                break
        loader.loadSound(self.envMgr,
                     path,
                     callback = self._setAndPlayENV,extraArgs = [fadein, volume, loop]) 
        
    def stopBGM(self, fadeout = 0):
        if self._currentBGM:
            stop_audio(self._currentBGM, fadeout)
        RuntimeData.current_bgm = None
        
    def stopENV(self, fadeout = 0):
        if self._currentENV:
            stop_audio(self._currentENV, fadeout)
        RuntimeData.current_env = None
    
    def stopVoice(self):
        self.voiceMgr.stopAllSounds()
    
    def stopSound(self):
        self.sfxMgr.stopAllSounds()
        
    def stopAll(self,fadeout = 0):
        self.stopBGM(fadeout)
        self.stopENV(fadeout)
        self.stopSound()
        self.stopVoice()
    
    def _setAndPlayBGM(self, audio, fadein, volume, loop):
        self._currentBGM = audio
        
        play_audio(audio, fadein, volume, loop)
        
    def _setAndPlayENV(self, audio, fadein, volume, loop):
        self._currentENV = audio
        play_audio(audio, fadein, volume, loop)
        
    def presave(self):
        pass
        
    def reload(self):
        'reload sound, should be called by StoryManager after loading'
        self.stopAll()
        bgm = RuntimeData.current_bgm
        self.playBGM(bgm[0],1,bgm[2],bgm[3])
        env = RuntimeData.current_env
        self.playENV(bgm[0],1,bgm[2],bgm[3])
        
        
    

        
