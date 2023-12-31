from datetime import datetime

from hyperfunc.utils import merge_dicts, complete_partial_datetime


def test_merge_dicts():
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'b': 3, 'c': 4}
    dict3 = {'d': 5}

    assert merge_dicts(dict1, dict2, dict3) == {'a': 1, 'c': 4, 'd': 5}


def test_complete_partial_datetime():
    now = datetime.now()
    res = now.replace(day=25, hour=15, minute=30, second=0, microsecond=0)
    assert complete_partial_datetime('25T15:30:00') == res
