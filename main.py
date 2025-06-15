from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from .difyDialogue import DifyAPI  # 导入DifyAPI类
from .sftp_client import SFTPClient  # 导入SFTP客户端
import yaml
import os


# 注册插件
@register(name="difyFileOpt", description="", version="0.1", author="sheetung")
class HelloPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        # 配置文件路径
        config_path = os.path.join(os.path.dirname(__file__), 'cfg.yaml')
        # 从YAML文件读取配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            cfg = {}  # 设置空配置，避免后续代码出错
        print(f'cfg={cfg}')

         # 获取Dify配置
        dify_config = cfg.get('dify', {})
        self.api_key = dify_config.get('api_key', "app-")
        self.base_url = dify_config.get('base_url', "http:")

        # # 从配置文件获取API密钥和URL
        # self.api_key = "app-MQN8n6HBJ7PKvK28p3iLsQps"
        # self.base_url = "http://192.168.31.131/v1"
        
        # 创建API客户端
        self.dify_api = DifyAPI(self.api_key, self.base_url)

        # 获取SFTP配置
        sftp_config = cfg.get('sftp', {})
        self.sftp_host = sftp_config.get('host', "")
        self.sftp_port = sftp_config.get('port', 22)
        self.sftp_user = sftp_config.get('username', "")
        self.sftp_pass = sftp_config.get('password', "")
        self.remote_file = sftp_config.get('remote_file', "")
        
        # 创建SFTP客户端
        self.sftp_client = SFTPClient(
            host=self.sftp_host,
            port=self.sftp_port,
            username=self.sftp_user,
            password=self.sftp_pass
        )
        
        # 连接SFTP服务器
        self.sftp_client.connect()

    # 异步初始化
    async def initialize(self):
        pass

    # 当收到群消息时触发
    @handler(GroupMessageReceived)
    async def group_normal_message_received(self, ctx: EventContext):
        msg = str(ctx.event.message_chain)  # 这里的 event 即为 PersonNormalMessageReceived 的对象
        sender_id = ctx.event.sender_id
        # print(msg)
        if not msg.startswith("df"):
            # print('over')
            return
        # print(f'msg={msg}')
        # 调用Dify API获取回复
        try:
            # 调用Dify API获取完整响应
            response = self.dify_api.send_chat_message(
                query=msg[2:].strip(),
                user=str(sender_id)
            )
            # self.logger.info(f"收到Dify响应: {response}")
            # print(f'response={response}')
            if response:
                # await ctx.reply(response)
                # ctx.prevent_default()

                # 2. 将响应写入远程文件
                print(f'sftpstate={self.remote_file}-{response}')
                success = self.sftp_client.append_to_file(self.remote_file, response)
                print(f'sftp state={success}')
                if not success:
                    print("SFTP写入失败")
                res = f'同步状态：{success}\n内容：\n{response}'
                await ctx.reply(res)
                ctx.prevent_default()
            else:
                await ctx.reply("Dify API返回空响应")
                ctx.prevent_default()
                
        except Exception as e:
            # self.logger.error(f"处理消息时出错: {str(e)}")
            await ctx.reply(f"处理消息时出错: {str(e)}")
            ctx.prevent_default()

    # 插件卸载时触发
    def __del__(self):
        # pass
        # 关闭SFTP连接
        self.sftp_client.close()
        print("DifyFileOpt插件已卸载")
