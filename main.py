from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from .difyDialogue import DifyAPI  # 导入DifyAPI类


# 注册插件
@register(name="difyFileOpt", description="", version="0.1", author="sheetung")
class HelloPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        # 从配置文件获取API密钥和URL
        # config = host.config.get("DifyPlugin", {})
        # self.api_key = config.get("api_key", "app-MQN8n6HBJ7PKvK28p3iLsQps")
        # self.base_url = config.get("base_url", "http://192.168.31.131/v1")
        self.api_key = "app-MQN8n6HBJ7PKvK28p3iLsQps"
        self.base_url = "http://192.168.31.131/v1"
        
        # 创建API客户端
        self.dify_api = DifyAPI(self.api_key, self.base_url)

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
            print('over')
            return
        print(f'msg={msg}')
        # 调用Dify API获取回复
        try:
            # 调用Dify API获取完整响应
            response = self.dify_api.send_chat_message(
                query=msg[2:].strip(),
                user=str(sender_id)
            )
            # self.logger.info(f"收到Dify响应: {response}")
            print(f'response={response}')
            if response:
                await ctx.reply(response)
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
        pass
