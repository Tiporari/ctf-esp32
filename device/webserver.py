"""Tiny asyncio HTTP server. Handlers: fn(req) -> str | bytes | (body, status, headers)."""
import asyncio


class Request:
    def __init__(self, method, path, query, headers, body):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body

    def form(self):
        return parse_qs(self.body.decode())

    def cookie(self, name):
        for part in self.headers.get("cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == name:
                return v
        return None


def parse_qs(s):
    out = {}
    for pair in s.split("&"):
        if not pair:
            continue
        k, _, v = pair.partition("=")
        out[unquote(k)] = unquote(v)
    return out


def unquote(s):
    s = s.replace("+", " ")
    parts = s.split("%")
    res = parts[0]
    for p in parts[1:]:
        try:
            res += chr(int(p[:2], 16)) + p[2:]
        except ValueError:
            res += "%" + p
    return res


class Server:
    def __init__(self):
        self.routes = {}

    def route(self, path, methods=("GET",)):
        def deco(fn):
            for m in methods:
                self.routes[(m, path)] = fn
            return fn
        return deco

    async def _handle(self, reader, writer):
        try:
            line = await reader.readline()
            if not line:
                return
            method, target, _ = line.decode().split(" ", 2)
            path, _, qs = target.partition("?")
            headers = {}
            while True:
                h = await reader.readline()
                if h in (b"\r\n", b"\n", b""):
                    break
                k, _, v = h.decode().partition(":")
                headers[k.strip().lower()] = v.strip()
            body = b""
            n = int(headers.get("content-length", 0))
            if n:
                body = await reader.readexactly(min(n, 2048))
            req = Request(method, path, parse_qs(qs), headers, body)
            fn = self.routes.get((method, path))
            if fn is None:
                status, hdrs, out = 404, {}, "404 Not Found"
            else:
                res = fn(req)
                if isinstance(res, tuple):
                    out, status, hdrs = (tuple(res) + (200, {})[len(res) - 1:])[:3]
                else:
                    out, status, hdrs = res, 200, {}
            if isinstance(out, str):
                out = out.encode()
            hdrs = dict(hdrs)
            hdrs.setdefault("Content-Type", "text/html; charset=utf-8")
            hdrs["Content-Length"] = str(len(out))
            hdrs["Connection"] = "close"
            head = "HTTP/1.0 %d X\r\n" % status
            head += "".join("%s: %s\r\n" % kv for kv in hdrs.items()) + "\r\n"
            writer.write(head.encode() + out)
            await writer.drain()
        except Exception as e:
            print("req error:", e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def run(self, port=80):
        await asyncio.start_server(self._handle, "0.0.0.0", port)
        print("HTTP on :%d" % port)
        while True:
            await asyncio.sleep(3600)
