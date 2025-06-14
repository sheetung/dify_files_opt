import requests
import json

class DifyAPI:
    def __init__(self, api_key, base_url):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.last_conversation_id = None

    def send_chat_message(self, query, user, conversation_id=None):
        """发送聊天消息并返回完整响应"""
        url = f"{self.base_url}/chat-messages"
        
        data = {
            "query": query,
            "user": user,
            "inputs": {},
            "response_mode": "streaming"
        }
        
        if conversation_id:
            data["conversation_id"] = conversation_id
            
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                json=data, 
                stream=True
            )
            
            if response.status_code != 200:
                error_msg = f"API错误: {response.status_code} - {response.text}"
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        error_msg += f"\n详细错误: {error_data['message']}"
                except:
                    pass
                raise Exception(error_msg)
            
            # 收集所有响应片段
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data: "):
                        json_str = decoded_line[6:]
                        try:
                            event_data = json.loads(json_str)
                            event_type = event_data.get("event")
                            
                            if event_type == "message":
                                full_response += event_data.get("answer", "")
                            
                            elif event_type == "message_end":
                                self.last_conversation_id = event_data.get("conversation_id")
                                final_answer = event_data.get("answer", "")
                                if final_answer:
                                    full_response += final_answer
                                # 返回完整响应
                                return full_response
                            
                            elif event_type == "error":
                                raise Exception(f"Dify错误: {event_data.get('message')}")
                        
                        except json.JSONDecodeError:
                            print(f"无法解析JSON: {json_str}")
            
            # 如果没有收到message_end事件，返回已收集的内容
            return full_response
        
        except Exception as e:
            print(f"API请求异常: {str(e)}")
            return f"处理消息时出错: {str(e)}"
