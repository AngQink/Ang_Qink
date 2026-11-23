"""Verifier for file and build workflows."""

import argparse
import hashlib
import json
from pathlib import Path
import queue
import os
from random import Random
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory, TemporaryFile
import threading
from zipfile import BadZipFile, ZipFile, ZIP_STORED
import zlib

HERE=Path(__file__).resolve().parent
PUBLIC=HERE.name=="自测"


def command(args, cwd, data=None, timeout=90, env=None):
    output = queue.Queue()
    limited = threading.Event()
    with TemporaryFile() as feed:
        if data is not None:
            feed.write(data)
            feed.seek(0)
        process = subprocess.Popen(args, cwd=cwd, stdin=feed, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=env)

        def capture(stream, label, limit):
            content = bytearray()
            with stream:
                while block := stream.read1(8192):
                    if len(content) + len(block) > limit:
                        limited.set()
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
                        break
                    content.extend(block)
            output.put((label, bytes(content)))

        readers = [threading.Thread(target=capture, args=(process.stdout,"stdout",4*1024*1024), daemon=True),
                   threading.Thread(target=capture, args=(process.stderr,"stderr",256*1024), daemon=True)]
        for reader in readers:
            reader.start()
        try:
            status = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
            raise
        for reader in readers:
            reader.join(timeout=3)
        if limited.is_set() or any(reader.is_alive() for reader in readers):
            raise RuntimeError("Process exceeded the output limit or left a pipe open.")
        captured = dict(output.get() for _ in readers)
        if status:
            detail=(captured["stderr"] or captured["stdout"])[-2400:].decode("utf-8",errors="replace")
            raise RuntimeError(f"{Path(str(args[0])).name}: {detail.strip()}")
        return captured["stdout"]


def bytes_json(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def recover_jobs(work, seeds):
    expected={}
    jobs=[]
    for i,seed in enumerate(seeds):
        random=Random(seed)
        tag=f"run-{i:02d}"
        folder=work/tag
        folder.mkdir()
        state={"counter":random.randrange(91),"obsolete":seed}
        revision=seed%11
        (folder/"checkpoint.json").write_bytes(bytes_json({"revision":revision,"items":state}))
        journal=[]
        for n in range(1, random.randrange(3,9)):
            rev=revision+1
            journal.extend([{"op":"begin","revision":rev},
                            {"op":"set","key":f"part-{random.randrange(5)}","value":random.randrange(-88,89)},
                            {"op":"del","key":"obsolete"},
                            {"op":"commit","revision":rev}])
            write=journal[-3]
            state[write["key"]]=write["value"]
            state.pop("obsolete",None)
            revision=rev
        if seed%3==0:
            suffix=b'{"op":"begin","revision":'+str(revision+1).encode()+b'}\n{"op":'
        elif seed%3==1:
            suffix=bytes_json({"op":"begin","revision":revision+1})+bytes_json({"op":"set","key":"counter","value":123})
            suffix+=bytes_json({"op":"commit","revision":revision+2})
            suffix+=bytes_json({"op":"commit","revision":revision+1})
        else:
            suffix=bytes_json({"op":"begin","revision":revision+1})+b'{"op":"commit","revision":'+str(revision+1).encode()+b'}'
        (folder/"journal.jsonl").write_bytes(b"".join(bytes_json(row) for row in journal)+suffix)
        expected[tag+"/recovered.json"]=bytes_json({"revision":revision,"items":state})
        jobs.append(tag)
    (work/"jobs.txt").write_text("\n".join(jobs)+"\n",encoding="ascii")
    return expected


def jar_jobs(work,seeds):
    code="""import java.nio.charset.StandardCharsets;
public class Greeting {
    public static void main(String[] args) throws Exception {
        try (var stream = Greeting.class.getResourceAsStream("/notice.txt")) {
            System.out.print(new String(stream.readAllBytes(), StandardCharsets.UTF_8));
        }
    }
}
"""
    (work/"Greeting.java").write_text(code,encoding="ascii")
    command(["javac","-encoding","UTF-8","--release","17","Greeting.java"],work)
    classfile=(work/"Greeting.class").read_bytes()
    manifest=b"Manifest-Version: 1.0\r\nMain-Class: Greeting\r\n\r\n"
    expected={}
    job_rows=[]
    for i,seed in enumerate(seeds):
        random=Random(seed)
        base=f"in-{i:02d}.jar"
        output=f"out-{i:02d}.jar"
        revision=random.choice([8,9,10,11,15,17,24])
        variants=[(0,"notice.txt",f"base {seed}\n".encode()),
                  (11,"notice.txt",f"eleven {seed}\n".encode()),
                  (17,"notice.txt",f"seventeen {seed}\n".encode()),
                  (9,"labels/region",f"region {seed%7}\n".encode()),
                  (15,"labels/region",f"override {seed%11}\n".encode()),
                  (0,"plain.txt",b"plain\n"),(0,"Greeting.class",classfile)]
        random.shuffle(variants)
        with ZipFile(work/base,"w") as archive:
            archive.writestr("META-INF/MANIFEST.MF",b"Manifest-Version: 1.0\r\nMulti-Release: true\r\nMain-Class: Greeting\r\n\r\n")
            for rev,path,payload in variants:
                name=f"META-INF/versions/{rev}/{path}" if rev else path
                archive.writestr(name,payload)
        chosen={name:max((r,b) for r,n,b in variants if n==name and r<=revision)[1]
                for name in {name for r,name,b in variants if r<=revision}}
        chosen["META-INF/MANIFEST.MF"]=manifest
        expected[output]=chosen
        job_rows.append(f"{revision}\t{base}\t{output}")
    (work/"jobs.tsv").write_text("\n".join(job_rows)+"\n",encoding="ascii")
    return expected



def shards_jobs(work,seeds):
    expected={}
    jobs=[]
    for i,seed in enumerate(seeds):
        random=Random(seed)
        name=f"pack-{i:02d}"
        directory=work/name
        directory.mkdir()
        jobs.append(name)
        count=2+seed%7
        entries=[]
        selected={}
        for block in reversed(range(count)):
            if seed%5==0 and block==1: continue
            raw=random.randbytes((seed+block*5)%67)
            path=f"block-{block}.bin"
            (directory/path).write_bytes(raw)
            entries.append(f"{block}\t{path}\t{zlib.crc32(raw):08x}")
            selected[block]=raw
            if seed%3==0:
                newer=random.randbytes((seed+block*6)%52)
                name2=f"new-{block}.bin"
                (directory/name2).write_bytes(newer)
                entries.append(f"{block}\t{name2}\t{zlib.crc32(newer):08x}")
                selected[block]=newer
            if seed%7==0:
                unrelated=random.randbytes(23)
                name3=f"bad-{block}.bin"
                (directory/name3).write_bytes(unrelated)
                entries.append(f"{block}\t{name3}\t{(zlib.crc32(unrelated)+1)%2**32:08x}")
        (directory/"count.txt").write_text(str(count)+"\n",encoding="ascii")
        (directory/"fragments.tsv").write_text("\n".join(entries)+"\n",encoding="ascii")
        missing=next((j for j in range(count) if j not in selected),None)
        expected[name]=(None,f"missing {missing}\n".encode()) if missing is not None else (b"".join(selected[j] for j in range(count)),b"complete\n")
    (work/"jobs.txt").write_text("\n".join(jobs)+"\n",encoding="ascii")
    return expected


def inventory_jobs(work,seeds):
    expected={}
    folders=[]
    for i,seed in enumerate(seeds):
        name=f"release-{i:02d}"
        folder=work/name
        stage=folder/"staging"
        (stage/"media").mkdir(parents=True)
        rng=Random(seed)
        old={
            "readme.txt":b"A",
            "media/说明.txt":"初稿".encode(),
            "obsolete.log":rng.randbytes(3),
        }
        current={
            "readme.txt":b"A",
            "media/说明.txt":f"版本 {seed}\n".encode(),
            "new file.bin":rng.randbytes(seed%19),
        }
        if seed%3==0:
            current["internal/debug.log"]=b"private"
        if seed%5==0:
            current["media/work.tmp"]=b"cache"
        if seed%2==0:
            current["obsolete.log"]=old["obsolete.log"]
        for name2,data in current.items():
            path=stage/name2
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
        (folder/"baseline.json").write_bytes(bytes_json({key:hashlib.sha256(value).hexdigest() for key,value in old.items()}))
        current={k:v for k,v in current.items() if "internal" not in k.split("/") and not k.endswith(".tmp")}
        lines=[]
        for key in sorted(old.keys()|current.keys()):
            if key not in current:
                lines.append(f"delete\t{key}\t-")
            else:
                digest=hashlib.sha256(current[key]).hexdigest()
                if key not in old:lines.append(f"add\t{key}\t{digest}")
                elif current[key]!=old[key]:lines.append(f"replace\t{key}\t{digest}")
        expected[name]=("\n".join(lines)+("\n" if lines else "")).encode()
        folders.append(name)
    (work/"jobs.txt").write_text("\n".join(folders)+"\n",encoding="ascii")
    return expected

def ledger(seed,channel):
    rng=Random(seed)
    lines=[(rng.randrange(1,300),rng.randrange(-80,140)) for _ in range(8+seed%6)]
    # Baseline rejects negative deltas. Canary preserves them.
    if channel=="Stable":
        out=[(stamp,delta if delta>=0 else 0,29, (stamp*19+(delta if delta>=0 else 0))%997) for stamp,delta in lines]
    else:
        out=[(stamp,delta,43,(stamp*31+delta+997)%997) for stamp,delta in lines]
    return lines,out


def build_job(mode,tree,root,channel):
    if mode=="cmake":
        target=root/("cmake-"+channel)
        env={**os.environ}
        command(["cmake","-S",str(tree),"-B",str(target),"-G","Ninja",
                 "-DCMAKE_CXX_COMPILER=g++","-DBENCH_CHANNEL="+channel],root,env=env)
        command(["cmake","--build",str(target),"--target","receipt"],root,env=env)
        return target/("receipt.exe" if os.name=="nt" else "receipt")
    cargo=shutil.which("cargo") or "cargo"
    target=root/("cargo-"+channel)
    env={**os.environ,"CARGO_TARGET_DIR":str(target),"CARGO_NET_OFFLINE":"true","CARGO_TERM_COLOR":"never"}
    flag="baseline" if channel=="Stable" else "next"
    command([cargo,"build","--offline","--no-default-features","--features",flag],tree,env=env)
    return target/"debug"/("receipt.exe" if os.name=="nt" else "receipt")


def batch_text(rows):
    return "".join(" ".join(map(str,line))+"\n" for line in rows).encode("ascii")


def check(mode, source, workspace, work, seeds):
    rows=[]
    if mode=="snapshot":
        source=Path(shutil.copyfile(source,work/"recover.py"))
        truth=recover_jobs(work,seeds)
        inputs = {f: f.read_bytes() for folder in work.glob('run-*') for f in folder.iterdir()}
        command([sys.executable,"-B","-I",str(source),"jobs.txt"],work)
        if any(not path.is_file() or path.read_bytes() != content for path,content in inputs.items()):
            raise RuntimeError('A source checkpoint or journal was changed.')
        for file,data in truth.items():
            target=work/file
            rows.append((file,target.is_file() and target.read_bytes()==data))
        return rows

    if mode=="jar":
        shutil.copyfile(source,work/"Main.java")
        truth=jar_jobs(work,seeds)
        command(["javac","-encoding","UTF-8","Main.java"],work)
        command(["java","-cp",str(work),"Main","jobs.tsv"],work)
        first = {name:(work/name).read_bytes() for name in truth if (work/name).is_file()}
        command(["java","-cp",str(work),"Main","jobs.tsv"],work)
        for i,(name,expected) in enumerate(truth.items()):
            out=work/name
            good=False
            if out.is_file() and out.read_bytes()==first.get(name):
                try:
                    with ZipFile(out) as archive:
                        members=archive.infolist()
                        names=[m.filename for m in members]
                        good=(names==["META-INF/MANIFEST.MF",*sorted(set(expected)-{"META-INF/MANIFEST.MF"})]
                              and all(m.compress_type==ZIP_STORED and m.date_time==(1980,1,1,0,0,0) for m in members)
                              and all(archive.read(n)==expected[n] for n in names))
                except (BadZipFile,OSError,ValueError):
                    pass
            if good and i in {0,len(truth)-1}:
                launched=command(["java","-jar",name],work)
                good=launched==expected["notice.txt"]
            rows.append((name,good))
        return rows

    if mode=="shards":
        shutil.copyfile(source,work/"main.go")
        truth=shards_jobs(work,seeds)
        executable=work/("bundle.exe" if os.name=="nt" else "bundle")
        command([os.environ.get("BENCH_GO","go"),"build","-o",str(executable),"main.go"],work)
        command([str(executable),"jobs.txt"],work)
        for directory,(payload,status) in truth.items():
            dst=work/directory
            binfile=dst/"bundle.bin"
            result=(binfile.is_file() and binfile.read_bytes()==payload) if payload is not None else not binfile.exists()
            actual=dst/"status.txt"
            rows.append((directory,result and actual.is_file() and actual.read_bytes()==status))
        return rows

    if mode=="inventory":
        shutil.copyfile(source,work/"main.ps1")
        truth=inventory_jobs(work,seeds)
        command(["pwsh","-NoLogo","-NoProfile","-File","main.ps1","jobs.txt"],work)
        for directory,expected in truth.items():
            dest=work/directory/"delta.tsv"
            rows.append((directory,dest.is_file() and dest.read_bytes()==expected))
        return rows

    tree=work/"build-input"
    shutil.copytree(workspace,tree)
    name="CMakeLists.txt" if mode=="cmake" else "Cargo.toml"
    shutil.copyfile(source,tree/name)
    for channel in ("Stable","Canary"):
        binary=build_job(mode,tree,work,channel)
        subsets=[(seed,*ledger(seed,channel)) for seed in seeds if (seed%2==0)==(channel=="Stable")]
        if not subsets:
            continue
        payload=batch_text(row for _,data,_ in subsets for row in data)
        response=command([str(binary)],work,payload,timeout=30).replace(b"\r\n",b"\n").splitlines()
        offset=0
        for seed,_,expected in subsets:
            wanted=batch_text(expected).splitlines()
            rows.append((f"{channel}-{seed}",response[offset:offset+len(wanted)]==wanted))
            offset+=len(wanted)
        if offset!=len(response):
            rows[-1]=(rows[-1][0],False)
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    profile=json.loads((HERE/"profile.json").read_text(encoding="utf-8"))
    data=(HERE/"cases.json").read_bytes()
    if hashlib.sha256(data).hexdigest()!=profile["sha256"]:
        parser.error("Fixture digest mismatch.")
    seeds=json.loads(data)
    question=HERE.parent if PUBLIC else HERE.parents[1]/"题目"
    workspace=question/"workspace"
    source=(args.candidate or (workspace if PUBLIC else HERE.parent/"reference")).resolve()
    if source.is_dir(): source/=profile["entry"]
    cases=[];error=None
    try:
        with TemporaryDirectory(prefix="workflow-") as raw:
            cases=check(profile["mode"],source,workspace,Path(raw),seeds)
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as exc:
        error=str(exc); print(error,file=sys.stderr)
    passed=sum(good for _,good in cases)
    for name,good in cases:
        if not good:print("FAIL",name)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        report={"passed":passed,"total":len(seeds),"checks":cases,"error":error}
        (args.output/"report.json").write_bytes(bytes_json(report))
    print(f"{passed}/{len(seeds)} passed.")
    return 0 if passed==len(seeds) else 1


if __name__=="__main__":
    sys.exit(main())
