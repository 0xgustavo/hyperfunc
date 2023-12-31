import pickle
from hyperfunc.core.mq import TaskQueue

task_queue = TaskQueue()

task_queue.lput(pickle.dumps({"a": 1}))
print(task_queue.get())
