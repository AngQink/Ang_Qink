"""Audit wrapper for the single submitted Python file."""
import os
import sys
import sysconfig

target=os.path.realpath(sys.argv[1])
with open(target,'rb') as f:code=compile(f.read(),target,'exec')
own=os.path.normcase(target)
library=os.path.normcase(os.path.realpath(sysconfig.get_paths()['stdlib']))
base=os.path.normcase(os.path.realpath(sys.base_prefix))
dlls=os.path.join(base,'dlls')
archive=os.path.join(base,f'python{sys.version_info.major}{sys.version_info.minor}.zip')
sys.path[:]=[p for p in sys.path if os.path.normcase(os.path.realpath(p)) in {library,base,dlls,archive}]
sys.argv[:]=[target];sys.dont_write_bytecode=True


def allowed(path):
    if isinstance(path,int):return path in (0,1,2)
    path=os.path.normcase(os.path.realpath(os.fsdecode(path)))
    return path in (own,archive,library,dlls) or path.startswith(library+os.sep) or path.startswith(dlls+os.sep)


def audit(event,args):
    if event=='open':
        path,mode,flags=args
        if not allowed(path) or flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):raise PermissionError('forbidden file access')
    elif event in ('os.listdir','os.scandir'):
        if args and args[0] is not None and not allowed(args[0]):raise PermissionError('forbidden directory access')
    elif event.startswith(('subprocess.','ctypes.','socket.')) or event in (
        'os.system','os.posix_spawn','os.spawn','os.exec','os.fork','os.forkpty','_winapi.CreateProcess',
        'os.remove','os.rmdir','os.rename','os.mkdir','os.link','os.symlink','os.truncate'):
        raise PermissionError('forbidden operation')


sys.addaudithook(audit)
exec(code,{'__name__':'__main__','__file__':target,'__package__':None,'__builtins__':__builtins__})
