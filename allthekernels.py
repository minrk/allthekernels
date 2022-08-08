"""All the Kernels: all your kernels in one kernel.

Like magic!
"""

import os
import sys
import asyncio
from tornado.ioloop import IOLoop

import zmq
from zmq.eventloop import ioloop
ioloop.install()
from zmq.eventloop.future import Context

from traitlets import Dict

from jupyter_client import KernelManager
from ipykernel.kernelbase import Kernel
from ipykernel.kernelapp import IPKernelApp


banner = """\
All The Kernels: A single Jupyter kernel that multiplexes.

Per default, all cells will be executed in the default python kernel. If the
first line of a cell starts with `>`, the line will be parsed as kernel name and
the rest of the cell will be executed in that kernel.

For instance,

    >python2
    def foo():
        ...

will run the cell in a Python 2 kernel, and

    >julia-0.4

will run in Julia 0.4, etc.

You can also set a new default kernel by prefixing the kernel name with `!`:

    >!ir

In this case the current cell and all further cells without a kernel name will
be executed in an R kernel.
"""


__version__ = '1.2.0.dev'


class KernelProxy(object):
    """A proxy for a single kernel


    Hooks up relay of messages on the shell channel.
    """
    def __init__(self, manager, shell_upstream, iopub_upstream, context):
        self.manager = manager
        self.session = manager.session
        self.shell = self.manager.connect_shell()
        self.shell_upstream = shell_upstream
        self.iopub_upstream = iopub_upstream
        self.iosub = context.socket(zmq.SUB)
        self.iosub.subscribe = b''
        self.iosub.connect(self.manager._make_url('iopub'))
        IOLoop.current().add_callback(self.relay_shell)
        IOLoop.current().add_callback(self.relay_iopub)
        self.shell_reply_event = asyncio.Event()  # to track if on shell channel the reply message has been received

    async def relay_shell(self):
        """Coroutine for relaying any shell replies"""
        while True:
            msg = await self.shell.recv_multipart()
            self.shell_reply_event.set()  # the status of shell_reply_event is changed to set when the reply is received
            self.shell_upstream.send_multipart(msg)

    async def relay_iopub(self):
        """Coroutine for relaying IOPub messages from all of our kernels"""
        while True:
            raw_msg = await self.iosub.recv_multipart()
            ident, msg = self.session.feed_identities(raw_msg)
            msg = self.session.deserialize(msg)
            if (msg["msg_type"] != "status"):
                self.iopub_upstream.send_multipart(raw_msg)
            else:
                pass


class AllTheKernels(Kernel):
    """Kernel class for proxying ALL THE KERNELS YOU HAVE"""
    implementation = 'AllTheKernels'
    implementation_version = __version__
    language_info = {
        'name': 'all-of-them',
        'mimetype': 'text/plain',
    }
    banner = banner

    kernels = Dict()
    default_kernel = os.environ.get('ATK_DEFAULT_KERNEL') or 'python%i' % (sys.version_info[0])
    _atk_parent = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.future_context = Context()
        self.shell_stream = self.shell_streams[0]

    def start_kernel(self, name):
        """Start a new kernel"""
        base, ext = os.path.splitext(self.parent.connection_file)
        cf = '{base}-{name}{ext}'.format(
            base=base,
            name=name,
            ext=ext,
        )
        manager = KernelManager(
            kernel_name=name,
            session=self.session,
            context=self.future_context,
            connection_file=cf,
        )
        manager.start_kernel()
        self.kernels[name] = KernelProxy(
            manager=manager,
            shell_upstream=self.shell_stream,
            iopub_upstream=self.iopub_socket,
            context=self.future_context
            )

        return self.kernels[name]

    def get_kernel(self, name):
        """Get a kernel, start it if it doesn't exist"""
        if name not in self.kernels:
            self.start_kernel(name)
        return self.kernels[name]

    def set_parent(self, ident, parent, channel="shell"):
        # record the parent message
        self._atk_parent = parent
        return super().set_parent(ident, parent, channel)

    def split_cell(self, cell):
        """Return the kernel name and remaining cell contents

        If no kernel name is specified, use the default kernel.
        """
        if not cell.startswith('>'):
            # no kernel magic, use default kernel
            return self.default_kernel, cell
        split = cell.split('\n', 1)
        if len(split) == 2:
            first_line, cell = split
        else:
            first_line = cell
            cell = ''
        kernel_name = first_line[1:].strip()
        if kernel_name[0] == "!":
            # >!kernelname sets it as the new default
            kernel_name = kernel_name[1:].strip()
            self.default_kernel = kernel_name
        return kernel_name, cell

    async def execute_request(self, stream, ident, parent):
        """Execute request sent to a kernel

        Gets the `>kernel` line off of the cell,
        finds the kernel (starts it if necessary),
        then relays the request.
        """
        content = parent['content']
        cell = content['code']
        kernel_name, cell = self.split_cell(cell)
        content['code'] = cell
        kernel_client = self.get_kernel(kernel_name)
        self.log.debug("Relaying %s to %s", parent['header']['msg_type'], kernel_name)
        self.session.send(kernel_client.shell, parent, ident=ident)
        await kernel_client.shell_reply_event.wait()  # waiting till shell_reply event status is 'set'
        kernel_client.shell_reply_event.clear()  # then the event's status is changed to 'unset'

    async def relay_to_kernel(self, stream, ident, parent):
        """Relay a message to a kernel

        Gets the `>kernel` line off of the cell,
        finds the kernel (starts it if necessary),
        then relays the request.
        """
        content = parent['content']
        cell = content['code']
        kernel_name, cell = self.split_cell(cell)
        content['code'] = cell
        kernel_client = self.get_kernel(kernel_name)
        self.log.debug("Relaying %s to %s", parent['header']['msg_type'], kernel_name)
        self.session.send(kernel_client.shell, parent, ident=ident)

    inspect_request = relay_to_kernel
    complete_request = relay_to_kernel

    def do_shutdown(self, restart):
        for kernel in self.kernels.values():
            kernel.manager.shutdown_kernel(False, restart)
        return super().do_shutdown(restart)


class AllTheKernelsApp(IPKernelApp):

    kernel_class = AllTheKernels
    # disable IO capture
    outstream_class = None

    def _log_level_default(self):
        return 10


main = AllTheKernelsApp.launch_instance


if __name__ == '__main__':
    main()
