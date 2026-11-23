def parse_request_line(line):
    method, target, version = line.split()
    path, _, query_string = target.partition("?")
    query = {}
    if query_string:
        for pair in query_string.split("&"):
            key, _, value = pair.partition("=")
            query[key] = value
    return {"method": method, "path": path, "query": query, "version": version}
