from queue import Queue
from threading import Thread

from ipykernel.kernelbase import Kernel
import re
import subprocess
import tempfile
import os
import os.path as path

dbg = 0

class RealTimeSubprocess(subprocess.Popen):
    """
    A subprocess that allows to read its stdout and stderr in real time
    """

    def __init__(self, cmd):
        """
        :param cmd: the command to execute
        """
        super().__init__(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        self._stdio_queue = Queue()
        # stdout -> _stdio_queue
        self._stdout_thread = Thread(target=self._enqueue_output,
                                     args=(self.stdout, 'stdout'))
        self._stdout_thread.daemon = True
        self._stdout_thread.start()
        # stderr -> _stdio_queue
        self._stderr_thread = Thread(target=self._enqueue_output,
                                     args=(self.stderr, 'stderr'))
        self._stderr_thread.daemon = True
        self._stderr_thread.start()

    def _enqueue_output(self, stream, stream_name):
        """
        Add chunks of data from a stream to a queue until the stream is empty.
        """
        for line in iter(lambda: stream.read(4096), b''):
            self._stdio_queue.put((stream_name, line))
        self._stdio_queue.put((stream_name, None))
        stream.close()

    def get_next(self):
        (stream_name,line) = self._stdio_queue.get()
        return (stream_name,line)

class CKernel(Kernel):
    implementation = 'jupyter_c_kernel'
    implementation_version = '1.0'
    language = 'c'
    language_version = 'C11'
    language_info = {'name': 'c',
                     'mimetype': 'text/plain',
                     'file_extension': '.c'}
    banner = "C kernel.\n" \
             "Uses gcc, compiles in C11, and creates source code files and executables in temporary folder.\n"

    def __init__(self, *args, **kwargs):
        super(CKernel, self).__init__(*args, **kwargs)
        self.files = []
        mastertemp = tempfile.mkstemp(suffix='.out')
        os.close(mastertemp[0])
        self.master_path = mastertemp[1]
        filepath = path.join(path.dirname(path.realpath(__file__)), 'resources', 'master.c')
        subprocess.call(['gcc', filepath, '-std=c11', '-rdynamic', '-ldl', '-o', self.master_path])

    def cleanup_files(self):
        """Remove all the temporary files created by the kernel"""
        for file in self.files:
            os.remove(file)
        os.remove(self.master_path)

    def new_temp_file(self, **kwargs):
        """Create a new temp file to be deleted when the kernel shuts down"""
        # We don't want the file to be deleted when closed, but only when the kernel stops
        kwargs['delete'] = False
        kwargs['mode'] = 'w'
        file = tempfile.NamedTemporaryFile(**kwargs)
        self.files.append(file.name)
        return file

    def _write_to_stdout(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stdout', 'text': contents})

    def _write_to_stderr(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stderr', 'text': contents})

    def create_jupyter_subprocess(self, cmd):
        return RealTimeSubprocess(cmd)

    def _filter_magics(self, code):

        magics = {'cflags': [],
                  'ldflags': [],
                  'args': [],
                  'file': None,
                  'cmd': []}

        for line in code.splitlines():
            if line.startswith('//%') or line.startswith('##%'):
                key, value = line[3:].split(":", 2)
                key = key.strip().lower()

                if key in ['ldflags', 'cflags']:
                    for flag in value.split():
                        magics[key] += [flag]
                elif key == "args":
                    # Split arguments respecting quotes
                    for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                        magics['args'] += [argument.strip('"')]
                elif key == 'file':
                    magics['file'] = value.strip()
                elif key == 'cmd':
                    this_cmd = []
                    for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
                        this_cmd.append(argument)
                    # magics['cmd'].append(this_cmd)
                    magics['cmd'].append([ "bash", "-c", value ])

        return magics

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        magics = self._filter_magics(code)
        if magics['file'] is None:
            wp = self.new_temp_file(suffix='.c')
        else:
            wp = open(magics['file'], "w")
        wp.write(code)
        wp.close()
        cmds = magics['cmd']
        for cmd in cmds:
            if dbg:
                self._write_to_stderr("cmd = %s\n" % cmd)
            p = self.create_jupyter_subprocess(cmd)
            closed = {}
            while len(closed) < 2:
                if dbg:
                    self._write_to_stderr("get_next\n")
                stream_name,contents = p.get_next()
                if contents is None:
                    if dbg:
                        self._write_to_stderr("CLOSE %s\n" % stream_name)
                    closed[stream_name] = 1
                else:
                    contents = contents.decode("utf-8")
                    if dbg:
                        self._write_to_stderr("[%s] --> %s\n"
                                              % (contents, stream_name))
                    self.send_response(self.iopub_socket, 'stream',
                                       {'name': stream_name, 'text': contents})
                    if dbg:
                        self._write_to_stderr("[%s] -> %s DONE\n"
                                              % (contents, stream_name))
            if dbg:
                self._write_to_stderr("WAIT ...\n")
            p.wait()
            if dbg:
                self._write_to_stderr("WAIT %s\n" % p.returncode)
            if p.returncode != 0:  # Compilation failed
                self._write_to_stderr("[C kernel] command exited with code {},"
                                      " subsequent commands will not be"
                                      " executed".format(p.returncode))
                break
        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {}}
    def do_shutdown(self, restart):
        """Cleanup the created source code files and executables when shutting down the kernel"""
        self.cleanup_files()
