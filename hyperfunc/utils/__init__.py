import ast
import importlib
import importlib.util
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

from hyperfunc import core


def register_funcs(base_dir: Path):
    """遍历项目文件夹，跳过 'venv' 'site-packages' 目录."""
    for file_path in base_dir.rglob('*.py'):
        if all([invalid_path not in str(file_path) for invalid_path in ['venv', 'site-packages']]):
            relative_path = file_path.relative_to(base_dir)
            analyze_file(relative_path)

    core.FUNC_MAPPING = merge_dicts(*core.func_mapping_list)  # 猴子补丁，合并已识别过的函数


def analyze_file(file_path: Path):
    """动态加载 Python 文件并执行以寻找被装饰的函数."""

    # Function to check for the hyper decorator
    def is_hyper_decorated(_node):
        for decorator in _node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func,
                                                              ast.Name) and decorator.func.id == 'hyper':
                return True
            if isinstance(decorator, ast.Name) and decorator.id == 'hyper':
                return True
        return False

    if not file_path.exists():
        return

    with open(file_path, 'r') as file:
        file_content = file.read()

    # Parse the content of the file
    try:
        parsed_ast = ast.parse(file_content)
    except SyntaxError as e:
        raise SyntaxError(f"Syntax error in the file: {e}")

    # Check all function definitions for the hyper decorator
    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.FunctionDef) and is_hyper_decorated(node):

            module_name = str(file_path).replace(os.sep, '.').replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(module)
            except Exception as e:
                print(f"Error loading module {module_name}: {e}")
            return


def merge_dicts(*dicts) -> dict:
    """
    多个字典，去除重复键后，合并成一个字典
    :param dicts:
    :return:
    """
    # 计算所有键的出现频率
    key_freq = Counter(key for d in dicts for key in d)
    # 合并字典，但排除重复的键
    merged_dict = {k: v for d in dicts for k, v in d.items() if key_freq[k] == 1}

    return merged_dict


def _fill_date(date_str: str) -> tuple:
    now = datetime.now()
    parts = date_str.split('-')

    if len(parts) == 2:
        return 'yearly', str(now.year) + parts[0] + parts[1]
    elif len(parts) == 1:
        return 'monthly', str(now.year) + str(now.month) + parts[0]
    else:
        raise ValueError("Invalid date")


def complete_partial_datetime(partial_time_str):
    """
    补充部分时间字符串，并将其转换为 datetime 对象。

    :param partial_time_str: 部分时间字符串，格式应为 'DDTHH:MM:SS'
    :return: 完整的 datetime 对象
    """
    if ' ' in partial_time_str:
        date, time = partial_time_str.split(' ')
