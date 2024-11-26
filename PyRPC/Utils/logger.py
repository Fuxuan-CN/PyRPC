
from loguru import logger
import sys

logger.remove() # 移除默认的日志处理器

logFmt = "<lvl>{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}.{function} | {file}:{line} | {message}</lvl>"

logger.add(sys.stderr, format=logFmt, level="INFO", enqueue=True)

def getLogger(name: str, level: str = "INFO"):
    
    return logger.bind(name=name, level=level)