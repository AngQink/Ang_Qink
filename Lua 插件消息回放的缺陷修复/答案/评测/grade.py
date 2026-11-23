"""Build and evaluate one native-language submission."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import queue
import re
import shutil
import sqlite3
import time
import subprocess
import sys
from tempfile import TemporaryDirectory
import threading

HERE = Path(__file__).resolve().parent
INT = re.compile(rb"-?(?:0|[1-9][0-9]{0,11})")


class RunError(Exception):
    pass


def tool(name, env_key=None):
    value = os.environ.get(env_key) if env_key else None
    found = value or shutil.which(name)
    if not found and os.name == "nt" and name in {"csc", "vbc"}:
        fallback = Path(os.environ["SystemRoot"]) / "Microsoft.NET/Framework64/v4.0.30319" / (name + ".exe")
        if fallback.is_file():
            found = str(fallback)
    if not found:
        raise RunError(f"Tool not available: {name}" + (f" (set {env_key} or add it to PATH)" if env_key else ""))
    return found


def invoke(command, work, source, timeout, cap):
    chunks = queue.Queue()
    clipped = threading.Event()
    with source.open("rb") if source else open(os.devnull, "rb") as pipe:
        process = subprocess.Popen(command, cwd=work, stdin=pipe, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        def capture(stream, limit, label):
            data = bytearray()
            with stream:
                while block := stream.read1(8192):
                    if len(data) + len(block) > limit:
                        clipped.set()
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
                        break
                    data.extend(block)
            chunks.put((label, bytes(data)))
        workers = [threading.Thread(target=capture, args=(process.stdout, cap, "stdout"), daemon=True),
                   threading.Thread(target=capture, args=(process.stderr, 256 * 1024, "stderr"), daemon=True)]
        for worker in workers:
            worker.start()
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
            raise RunError(f"Timed out after {timeout}s: {Path(command[0]).name}")
        for worker in workers:
            worker.join(timeout=3)
        if clipped.is_set() or any(worker.is_alive() for worker in workers):
            raise RunError("Output limit exceeded or a child kept the output pipe open.")
        data = dict(chunks.get() for _ in workers)
        if code:
            detail = (data["stderr"] or data["stdout"])[-1400:].decode("utf-8", errors="replace")
            raise RunError(f"Exit {code}: {detail.strip()}")
        if source and data["stderr"].strip():
            raise RunError("The solution wrote diagnostics to stderr.")
        return data["stdout"]


def command_for(profile, work, source, support):
    language = profile["language"]
    entry = profile["entry"]
    shutil.copyfile(source, work / entry)
    program = "solution.exe" if os.name == "nt" else "solution"
    output = str(work / program)
    if language == "python":
        return [sys.executable, "-B", "-I", entry]
    if language == "lua":
        return [tool("lua", "BENCH_LUA"), entry]
    if language == "gdscript":
        shutil.copyfile(support / "project.godot", work / "project.godot")
        return [tool("godot", "BENCH_GODOT"), "--headless", "--quiet", "--path",
                str(work), "--script", entry]

    if language in {"javascript", "typescript"}:
        return [tool("node"), entry]
    if language == "powershell":
        return [tool("pwsh"), "-NoLogo", "-NoProfile", "-NonInteractive", "-File", entry]
    if language == "bash":
        return [tool("bash"), "--noprofile", "--norc", entry]
    if language == "awk":
        return [tool("awk"), "-f", entry]
    if language == "perl":
        return [tool("perl"), entry]
    if language == "vbs":
        return [tool("cscript"), "//Nologo", entry]
    if language == "batch":
        return [tool("cmd"), "/d", "/c", entry, "input.txt"]
    if language == "sql":
        return []
    if language == "java":
        invoke([tool("javac"), "-encoding", "UTF-8", entry], work, None, 60, 256 * 1024)
        return [tool("java"), "-cp", str(work), "Main"]
    if language == "cuda":
        nvcc = tool("nvcc")
        architect = os.environ.get("BENCH_CUDA_ARCH", "sm_120")
        prefix = [tool("cmd"), "/d", "/c", os.environ["BENCH_MSVC_WRAPPER"]] if os.environ.get("BENCH_MSVC_WRAPPER") else []
        build = prefix + [nvcc, f"-arch={architect}", "-O2", "-o", program, entry]
    elif language == "asm":
        for filename in ("driver.c",):
            shutil.copyfile(support / filename, work / filename)
        build = [tool("gcc"), "-O2", "-o", program, entry, "driver.c"]
    elif language in {"c", "cpp", "fortran"}:
        compiler = {"c":"gcc", "cpp":"g++", "fortran":"gfortran"}[language]
        build = [tool(compiler), "-O2", "-static", "-o", program, entry]
        if language == "fortran":
            build.insert(1, "-ffree-line-length-none")
    elif language == "rust":
        build = [tool("rustc"), "--edition=2021", "-O", "-o", program, entry]
    elif language == "go":
        build = [tool("go", "BENCH_GO"), "build", "-o", program, entry]
    elif language in {"csharp", "vbnet"}:
        build = [tool("csc" if language == "csharp" else "vbc"), "/nologo", "/out:" + program, entry]
    else:
        raise RunError(f"Unknown language {language}")
    invoke(build, work, None, 90, 512 * 1024)
    return [output]


def sqlite_query(query, rows, timeout):
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE TABLE input (a INTEGER,b INTEGER,c INTEGER,d INTEGER,e INTEGER,f INTEGER)")
        db.executemany("INSERT INTO input VALUES (?,?,?,?,?,?)", rows)

        def authorize(action, name, arg, database, trigger):
            if action in {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE}:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and arg.lower() != "load_extension":
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ and name == "input" and database in {"main", None}:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        db.set_authorizer(authorize)
        until = time.monotonic() + timeout
        db.set_progress_handler(lambda: int(time.monotonic() >= until), 5000)
        result = bytearray()
        for i, row in enumerate(db.execute(query)):
            if i >= len(rows) or len(row) != 4 or not all(type(v) is int for v in row):
                raise RunError("Expected four integer columns and one result row per input.")
            result.extend((" ".join(map(str, row)) + "\n").encode("ascii"))
        return result
    except sqlite3.Error as exc:
        raise RunError(f"SQLite: {exc}") from exc
    finally:
        db.close()


def replay(profile, command, cases, work):
    rows = [row for case in cases for row in case["input"]]
    input_path = work / "input.txt"
    if profile["language"] == "sql":
        query = (work / profile["entry"]).read_text(encoding="utf-8")
        data = sqlite_query(query, rows, profile["timeout"])
    else:
        input_path.write_text("".join(" ".join(map(str, row)) + "\n" for row in rows), encoding="ascii", newline="\n")
        data = invoke(command, work, input_path, profile["timeout"], min(4 * 1024 * 1024, 100 * len(rows) + 4096))
    if profile["language"] == "gdscript":
        output = work / "result.txt"
        if not output.is_file() or output.stat().st_size > 4 * 1024 * 1024:
            raise RunError("Expected a result.txt within the artifact size limit.")
        data = output.read_bytes()
        output.unlink()
    lines = data.splitlines()
    if len(lines) != len(rows):
        raise RunError(f"Expected {len(rows)} result rows; found {len(lines)}.")
    parsed = []
    for count, line in enumerate(lines, 1):
        words = line.split()
        if len(words) != 4 or any(not INT.fullmatch(word) for word in words):
            raise RunError(f"Invalid result row at line {count}.")
        parsed.append([int(word) for word in words])
    result = []
    offset = 0
    for case in cases:
        count = len(case["input"])
        actual = parsed[offset:offset+count]
        expected = case["expected"]
        first = next((i for i,(a,b) in enumerate(zip(actual,expected),1) if a != b), None)
        result.append({"name":case["name"],"passed":first is None,"first_mismatch":first})
        offset += count
    return result


def load():
    profile_path = HERE / "profile.json"
    cases_path = HERE / "cases.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if sha256(cases_path.read_bytes()).hexdigest() != profile["sha256"]:
        raise RunError("The fixture file does not match the published digest.")
    return profile, json.loads(cases_path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--output", type=Path, help="new directory for JSON report")
    args = parser.parse_args()
    profile, cases = load()
    public = HERE.name == "自测"
    default = HERE.parent / "workspace" if public else HERE.parent / "reference"
    source = (args.candidate or default).resolve()
    if source.is_dir():
        source /= profile["entry"]
    results = []
    error = None
    try:
        if not source.is_file():
            raise RunError(f"Cannot find {source.name}.")
        with TemporaryDirectory(prefix="bench-build-") as t:
            work = Path(t)
            question = HERE.parent if public else HERE.parents[1] / "题目"
            cmd = command_for(profile, work, source, question / "workspace")
            results = replay(profile, cmd, cases, work)
    except (OSError, RunError, ValueError) as exc:
        error = str(exc)
    passed = sum(row["passed"] for row in results)
    report = {"passed":passed, "total":len(cases), "cases":results, "error":error}
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",encoding="utf-8")
    if error:
        print(error, file=sys.stderr)
    for row in results:
        if not row["passed"]:
            print(f"FAIL {row['name']} at row {row['first_mismatch']}")
    print(f"{passed}/{len(cases)} passed.")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
