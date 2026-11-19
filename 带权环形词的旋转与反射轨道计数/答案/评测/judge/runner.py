"""Candidate wrapper: restrict accidental external I/O with Python audit hooks."""
import os
import sys
import sysconfig

candidate=os.path.realpath(sys.argv[1])
with open(candidate,'rb') as stream:code=compile(stream.read(),candidate,'exec')
library=os.path.normcase(os.path.realpath(sysconfig.get_paths()['stdlib']))
base=os.path.normcase(os.path.realpath(sys.base_prefix))
dlls=os.path.join(base,'dlls')
zipfile=os.path.join(base,f'python{sys.version_info.major}{sys.version_info.minor}.zip')
own=os.path.normcase(candidate)
sys.path[:]=[p for p in sys.path if os.path.normcase(os.path.realpath(p)) in {library,base,dlls,zipfile}]
sys.argv[:]=[candidate]
sys.dont_write_bytecode=True


def allowed(path):
    if isinstance(path,int):return path in (0,1,2)
    path=os.path.normcase(os.path.realpath(os.fsdecode(path)))
    return path==own or path==zipfile or path==library or path.startswith(library+os.sep) or path==dlls or path.startswith(dlls+os.sep)


def audit(event,args):
    if event=='open':
        path,mode,flags=args
        if not allowed(path) or flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
            raise PermissionError('task permits only its own source and standard-library reads')
    elif event in ('os.listdir','os.scandir'):
        if args and args[0] is not None and not allowed(args[0]):raise PermissionError('external directory access')
    elif event.startswith(('subprocess.','ctypes.','socket.')) or event in (
        'os.system','os.posix_spawn','os.spawn','os.exec','os.fork','os.forkpty','_winapi.CreateProcess',
        'os.remove','os.rmdir','os.rename','os.mkdir','os.link','os.symlink','os.truncate'):
        raise PermissionError('operation forbidden by the task')


sys.addaudithook(audit)
exec(code,{'__name__':'__main__','__file__':candidate,'__package__':None,'__builtins__':__builtins__})
