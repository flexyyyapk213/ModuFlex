import fs from 'fs';
import { loadPyodide } from 'pyodide';
import readline from 'readline';

async function main() {
    let pythonOutput = "";

    console.error("Загрузка Pyodide...");
    const pyodide = await loadPyodide({
        stdout: (text) => {pythonOutput += text + '\n'},
        stderr: (text) => {pythonOutput += text + '\n'}
    });
    console.error("Pyodide готов к работе");

    const rl = readline.createInterface({
        input: process.stdin,
        terminal: false
    });

    rl.on('line', async (filePath) => {
        if (!filePath || !fs.existsSync(filePath)) {
            console.log(JSON.stringify({ status: "error", output: "NodeJS: File not found" }));
            return;
        }

        try {
            const code = fs.readFileSync(filePath, 'utf8');
            const result = await pyodide.runPythonAsync(code);
            console.log(JSON.stringify({ 
                status: "success", 
                output: pythonOutput ? pythonOutput : null
            }));
        } catch (err) {
            console.log(JSON.stringify({ status: "error", output: pythonOutput + err.message }));
        }

        pythonOutput = "";
    });
}

main();