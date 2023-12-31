import logging

from hyperfunc.config import BASE_DIR

# 创建一个Logger
logger = logging.getLogger("hyperfunc")
logger.setLevel(logging.DEBUG)  # 设置日志级别

# 创建一个FileHandler来将日志写入文件
file_handler = logging.FileHandler(BASE_DIR / "hyperfunc.log")
file_handler.setLevel(logging.DEBUG)  # 为这个Handler设置日志级别

# 创建一个Formatter来定义日志的格式
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# 将FileHandler添加到Logger
logger.addHandler(file_handler)

# # 使用Logger记录消息
# logger.info("This is an info message")
# logger.error("This is an error message")


class TaskLogger:
    def __init__(self):
        self.logger = logger

    def success(self, result_metadata: dict) -> None:
        self.logger.info(result_metadata)

    def exception(self, exception_metadata: dict) -> None:
        self.logger.exception(exception_metadata)


task_logger = TaskLogger()
