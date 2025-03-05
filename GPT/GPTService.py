import logging
import os
import time

import GPT.machine_id
import GPT.tune as tune
from openai import OpenAI  # 新增依赖
import re


class GPTService():
    def __init__(self, args):
        logging.info('Initializing ChatGPT Service...')
        self.chatVer = args.chatVer

        self.tune = tune.get_tune(args.character, args.model)

        self.counter = 0

        self.brainwash = args.brainwash

        self.model = args.model
        self.api_key = args.APIKey
        self.base_url = args.base_url if hasattr(args,'base_url') else "https://dashscope.aliyuncs.com/compatible-mode/v1"

        if self.chatVer == 1:
            from revChatGPT.V1 import Chatbot
            config = {}
            if args.accessToken:
                logging.info('Try to login with access token.')
                config['access_token'] = args.accessToken

            else:
                logging.info('Try to login with email and password.')
                config['email'] = args.email
                config['password'] = args.password
            config['paid'] = args.paid
            config['model'] = args.model
            if type(args.proxy) == str:
                config['proxy'] = args.proxy

            self.chatbot = Chatbot(config=config)
            logging.info('WEB Chatbot initialized.')


        elif self.chatVer == 3:
            mach_id = GPT.machine_id.get_machine_unique_identifier()
            from revChatGPT.V3 import Chatbot
            if args.APIKey:
                logging.info('you have your own api key. Great.')
                api_key = args.APIKey
            else:
                logging.info('using custom API proxy, with rate limit.')
                os.environ['API_URL'] = "https://api.geekerwan.net/chatgpt2"
                api_key = mach_id

            self.chatbot = Chatbot(api_key=api_key, proxy=args.proxy, system_prompt=self.tune)
            logging.info('API Chatbot initialized.')

            # 新增DeepSeek配置分支
        elif self.chatVer == 4:  # 假设4为DeepSeek专用版本
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key  # 需新增命令行参数
            )
            logging.info('DeepSeek Chatbot initialized.')

    def ask(self, text):
        stime = time.time()
        if self.chatVer == 3:
            prev_text = self.chatbot.ask(text)

        # V1
        elif self.chatVer == 1:
            for data in self.chatbot.ask(
                    self.tune + '\n' + text
            ):
                prev_text = data["message"]

        # 新增DeepSeek分支
        elif self.chatVer == 4:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                        {"role": "system", "content": self.tune},
                        {"role": "user", "content": text}
                ],
                temperature=1,
                max_tokens=4096,  # 支持长文本[7](@ref)
                stream=False
            )
            prev_text = response.choices[0].message.content

        logging.info('ChatGPT Response: %s, time used %.2f' % (prev_text, time.time() - stime))
        return prev_text

    def ask_stream(self, text):
        print("使用流式输出")
        prev_text = ""
        complete_text = ""
        stime = time.time()
        if self.chatVer == 1 or self.chatVer == 3:
            print("使用ChatGPT")
            if self.counter % 5 == 0 and self.chatVer == 1:

                if self.brainwash:
                    logging.info('Brainwash mode activated, reinforce the tune.')
                else:
                    logging.info('Injecting tunes')
                asktext = self.tune + '\n' + text
            else:
                asktext = text
            self.counter += 1
            for data in self.chatbot.ask(asktext) if self.chatVer == 1 else self.chatbot.ask_stream(text):
                message = data["message"][len(prev_text):] if self.chatVer == 1 else data

                if ("。" in message or "！" in message or "？" in message or "\n" in message) and len(complete_text) > 3:
                    complete_text += message
                    logging.info('ChatGPT Stream Response: %s, @Time %.2f' % (complete_text, time.time() - stime))
                    yield complete_text.strip()
                    complete_text = ""
                else:
                    complete_text += message

                prev_text = data["message"] if self.chatVer == 1 else data
        elif self.chatVer == 4:
            print("使用deepseek流式输出")
            try:
                response = self.client.chat.completions.create(
                    model = self.model,
                    messages=[
                        {"role": "system", "content": self.tune},
                        {"role": "user", "content": text}
                    ],
                    stream=True,
                    timeout=30  # 添加超时设置
                )

                complete_text = ""
                sentence_endings = re.compile(r'([。！？\n])')  # 正则表达式匹配终止符

                for chunk in response:
                    if chunk.choices[0].finish_reason == 'stop':
                        if complete_text.strip():
                            #logging.info('deepseek Stream Response: %s, @Time %.2f' % (complete_text, time.time() - stime))
                            yield complete_text.strip()
                        break

                    message = chunk.choices[0].delta.content or ""
                    complete_text += message
                    #print("分割之前的句子："+complete_text)

                    # 统一分割逻辑
                    parts = sentence_endings.split(complete_text)
                    for i in range(0, len(parts) - 1, 2):
                        sentence = (parts[i] + parts[i + 1]).strip()
                        if sentence:
                            logging.info('deepseek Stream Response: %s, @Time %.2f' % (sentence, time.time() - stime))
                            yield sentence
                    complete_text = parts[-1] if len(parts) % 2 else ""

            except Exception as e:
                logging.error(f"Error: {str(e)}")
                yield "服务暂时不可用，请检查网络或配置"
