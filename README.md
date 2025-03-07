# Digital Life Server
这是基于[zixiiu](https://github.com/zixiiu/Digital_Life_Server)的「数字生命」服务修改的部分代码。
包括与前端通信，语音识别，deepseek、chatGPT接入和语音合成。我主要新增了deepseek接入。  
For other part of the project, please refer to:  
[Launcher](https://github.com/CzJam/DL_Launcher) 启动此服务器的图形界面。  
[UE Client](https://github.com/QSWWLTN/DigitalLife) 用于渲染人物动画，录音，和播放声音的前端部分。    
详细的配置流程可参见[readme_detail.md](readme_detail.md)
## Getting stuffs ready to roll:
### 打开cmd使用命令进入你想将项目放入的文件目录，执行下面的命令
```bash
git clone https://github.com/xiaowangaixuexijishu/Digital_Life_Server_deepseek --recursive
cd Digital_Life_Server
```
### 安装依赖项目
1. install pytorch
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    ```

2. install other requirements
    ```bash
    pip install -r requirements.txt
    ```

3. Build `monotonic_align`  这里需要先下载[vits](https://github.com/zixiiu/vits)放入TTS中。
   This may not work that well but you know what that suppose to mean.
   ```bash
   cd "TTS/vits/monotonic_align"
   mkdir monotonic_align
   python setup.py build_ext --inplace
   cp monotonic_align/*.pyd .
   ```

4. Download models  
   [百度网盘](https://pan.baidu.com/s/1EnHDPADNdhDl71x_DHeElg?pwd=75gr)  
   ASR Model:   
   to `/ASR/resources/models`  
   Sentiment Model:  
   to `/SentimentEngine/models`  
   TTS Model:  
   to `/TTS/models`

5. （对于**没有**Nvidia显卡的电脑，采用cpu来跑的话）需要额外做一步（这个我没试过不知道行不行）：

   ​	将 Digital_Life_Server\TTS\TTService.py 文件下 36行

   ```
   self.net_g = SynthesizerTrn(...).cuda()
   修改为
   self.net_g = SynthesizerTrn(...).cpu()
   ```

   

   > 到这里，项目构建完毕🥰

### Start the server
   ```bash
   run-gpt3.5-api.bat
   ```
