import concurrent.futures
import functools
import traceback
from types import FunctionType

from hyperfunc.core.logger import task_logger


def task_as_params(func: FunctionType):
    @functools.wraps(func)
    def wrapper(task: dict):
        return func(*task["args"], **task["kwargs"])

    return wrapper


def func_timeout(timeout: int | float):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(f"Function '{func.__name__}' timed out after {timeout} seconds")

        return wrapper

    return decorator


def log_exception(func: FunctionType):
    @functools.wraps(func)
    def wrapper(task: dict):
        try:
            return func(task)
        except Exception as e:
            exception_with_metadata = {
                "task": task,
                "exception": traceback.format_exc(),
            }
            task_logger.exception(exception_with_metadata)
            raise e

    return wrapper


def log_result(func: FunctionType):
    @functools.wraps(func)
    def wrapper(task: dict):
        result = func(task)
        result_with_metadata = {
            "task": task,
            "result": result,
        }
        task_logger.success(result_with_metadata)
        return result

    return wrapper
