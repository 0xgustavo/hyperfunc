import datetime
import pickle
import time
import uuid
from functools import update_wrapper
from types import FunctionType

from hyperfunc.core.mq import task_queue, delay_queue
from .decorators import func_timeout, log_result, log_exception, task_as_params

func_mapping_list = []
FUNC_MAPPING = {}


class HyperFunc:
    def __init__(self, func: FunctionType, *, max_retries: int = 0, retry_delay: int = 1, retry_backoff: bool = False):
        update_wrapper(self, func)
        self.func = func  # 保存原始函数

        self._full_func_path = self.func.__module__ + "." + self.func.__name__  # 函数相对于项目根目录的路径接函数名称
        func_mapping_list.append(self._func_mapping())  # 生成 函数名：函数 键值对

        # 保存此函数的其他执行属性
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff

    def __call__(self, *args, **kwargs):
        """
        运行保存传入的原始函数
        :param args:
        :param kwargs:
        :return:
        """
        return self.func({"args": args, "kwargs": kwargs})

    def task_call(self, task: dict):
        return self.func(task)

    def _func_mapping(self) -> dict:
        """
        可能的函数名作为 key，本函数作为 value
        :return:
        """
        f_m = {}
        for _name in self._possible_names(self._full_func_path):
            f_m[_name] = self
        return f_m

    @staticmethod
    def _possible_names(full_name):
        """
        根据当前完整的函数路径，计算出所有可能的函数模块路径有哪些
        :param full_name:
        :return:
        """
        parts = full_name.split(".")
        return [".".join(parts[i:]) for i in range(len(parts) - 1)]

    def _task_metadata(self, *args, **kwargs) -> dict:
        """
        将函数与参数封装成 message
        :param args:
        :param kwargs:
        :return:
        """
        metadata = {
            "id": str(uuid.uuid4()),
            "func": self._full_func_path,
            "args": args,
            "kwargs": kwargs,
            "retries": 0,
        }
        return metadata

    def push(self, *args, **kwargs) -> str:
        """
        将执行的函数封装成 message 传入执行队列
        :param args:
        :param kwargs:
        :return:
        """
        task = self._task_metadata(*args, **kwargs)
        task_queue.lput(pickle.dumps(task))
        return task["id"]

    def delay(
            self, args: tuple = None, kwargs: dict = None, countdown: int | float = 0, eta: datetime.datetime = None
    ) -> str:
        """
        将延迟运行的函数封装成 message 传入延迟队列
        :param eta:
        :param countdown:
        :param args:
        :param kwargs:
        :return:
        """
        args = args if args else ()
        kwargs = kwargs if kwargs else {}

        if eta:
            run_at = eta.timestamp()
        else:
            run_at = time.time() + countdown

        task = self._task_metadata(*args, **kwargs)
        delay_queue.put(pickle.dumps(task), run_at=run_at)
        return task["id"]


def _pre_wrap(
        func: FunctionType, timeout: int | float = 0, ignore_results: bool = False, always_log_exception: bool = False
):
    func = task_as_params(func)  # 第一步，现将函数改造成接受一个 task 字典作为参数的函数，内部再解包调用原始函数

    if timeout:
        func = func_timeout(timeout=timeout)(func)

    if ignore_results:
        if always_log_exception:
            func = log_exception(func)
    else:
        func = log_exception(func)
        func = log_result(func)

    return func


def hyper(
        func: FunctionType = None,
        timeout: int | float = 0,
        ignore_results: bool = False,
        always_log_exception: bool = False,
        **kwargs,
):
    if func is None:
        # 当作为 @hyper() 使用时，返回一个带参数的包装函数
        def wrapper_with_kwargs(f):
            f = _pre_wrap(f, timeout=timeout, ignore_results=ignore_results, always_log_exception=always_log_exception)

            return HyperFunc(f, **kwargs)

        hyper_func = wrapper_with_kwargs
    else:
        # 当作为 @hyper 使用时，直接返回 HyperFunc 对象
        func = _pre_wrap(
            func, timeout=timeout, ignore_results=ignore_results, always_log_exception=always_log_exception
        )

        hyper_func = HyperFunc(func, **kwargs)

    return hyper_func
