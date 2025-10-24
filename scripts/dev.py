import asyncio
import os
import sys
from typing import List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_DIR = os.path.join(ROOT_DIR, "server")
WEB_DIR = os.path.join(ROOT_DIR, "web")


async def run_process(cmd: List[str], env: dict) -> int:
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=ROOT_DIR,
        env=env,
    )
    try:
        return await process.wait()
    except asyncio.CancelledError:
        process.terminate()
        await process.wait()
        raise


async def main() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = SERVER_DIR

    backend_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    frontend_cmd = ["npm", "--prefix", WEB_DIR, "run", "dev"]

    backend_task = asyncio.create_task(run_process(backend_cmd, env))
    frontend_task = asyncio.create_task(run_process(frontend_cmd, env))

    done, pending = await asyncio.wait(
        {backend_task, frontend_task},
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()

    for task in done:
        exc = task.exception()
        if exc:
            raise exc
        code = task.result()
        if code:
            raise SystemExit(code)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except KeyboardInterrupt:
        raise SystemExit(0)
