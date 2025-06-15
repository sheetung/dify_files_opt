import paramiko
import logging
import os

class SFTPClient:
    """SFTP客户端用于远程文件操作"""
    
    def __init__(self, host, port, username, password, logger=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.logger = logger or logging.getLogger(__name__)
        self.ssh = None
        self.sftp = None
        
    def connect(self):
        """连接到远程服务器"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password
            )
            self.sftp = self.ssh.open_sftp()
            self.logger.info(f"成功连接到SFTP服务器: {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"SFTP连接失败: {str(e)}")
            return False
            
    def append_to_file(self, remote_path, content):
        """向远程文件追加内容"""
        if not self.sftp:
            if not self.connect():
                # return 
                return False
                
                
        try:
            # 检查文件是否存在，不存在则创建
            try:
                self.sftp.stat(remote_path)
            except FileNotFoundError:
                with self.sftp.file(remote_path, 'w') as f:
                    f.write("")
                self.logger.info(f"创建新文件: {remote_path}")
            
            # 追加内容到文件
            with self.sftp.file(remote_path, 'a') as f:
                f.write(f"\n{content}")
                
            self.logger.info(f"成功追加内容到文件: {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"文件写入失败: {str(e)}")
            # return False
            return e
            
    def close(self):
        """关闭连接"""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        self.logger.info("SFTP连接已关闭")
        
    def __del__(self):
        self.close()
