from concurrent.futures import ThreadPoolExecutor


def run_all(fn, items, max_workers=4):
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fn, items))


def try_all(fn, items, max_workers=4):
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fn, item) for item in items]
        results = []
        for future in futures:
            try:
                results.append((True, future.result()))
            except Exception as error:
                results.append((False, error))
        return results
