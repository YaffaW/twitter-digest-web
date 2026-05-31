"""Simple background worker queue for running blocking tasks in a thread."""
import threading
import queue
import logging

logger = logging.getLogger("bg_worker")

_q = queue.Queue()


def _worker_loop():
    while True:
        func, args, kwargs = _q.get()
        try:
            logger.info(f"Running background task: {getattr(func, '__name__', str(func))}")
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Background task failed: {e}")
        finally:
            _q.task_done()


_thread = threading.Thread(target=_worker_loop, daemon=True)
_thread.start()


def enqueue(func, *args, **kwargs):
    """Enqueue a callable to run in background."""
    _q.put((func, args, kwargs))
