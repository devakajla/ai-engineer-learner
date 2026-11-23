import queue
import threading


def pipeline(items, transform, workers=3):
    if workers < 1:
        raise ValueError("workers must be at least 1")
    items = list(items)
    jobs = queue.Queue()
    results = [None] * len(items)

    def worker():
        while True:
            job = jobs.get()
            if job is None:
                break
            index, item = job
            results[index] = transform(item)

    threads = [threading.Thread(target=worker) for _ in range(workers)]
    for t in threads:
        t.start()
    for index, item in enumerate(items):
        jobs.put((index, item))
    for _ in threads:
        jobs.put(None)
    for t in threads:
        t.join()
    return results
