from quart import Quart, render_template, Blueprint, jsonify
from loads import Data

app = Quart(__name__)

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/get_plugins')
async def get_plugins():
    plugins = []

    for plugin, value in Data.cache.items():
        if 'funcs' in value['routes'] or 'methods' in value['routes']:
            plugins.append(plugin)

    return jsonify({'plugins': plugins})

if __name__ == "__main__":
    app.run(debug=False, port=1205)