Labyrinth is a family board game. This project aims to recreate the game as a online multiplayer game, develop understanding of the game's complexity and implement practical search algorithms.

There is one major difference to the original game: all players have the same objective. 
The objective is always randomly chosen to be one of the 50 maze cards which is not occupied by a player's piece.

Also, it is only possible to reach an objective while making a move. Reaching an objective while it is another player's move is not counted.

Manual to the original game: https://www.ravensburger.com/spielanleitungen/ecm/Spielanleitungen/Labyrinth_26448_GB.pdf

# Quick start
Build the client and run the flask web server.
## Build web-client
    cd web-client
    npm install
    npm run test:unit
    npm run build

    cd ../backend

Now is a good time to create and activate a virtual environment, e.g. on Linux:

    python -m venv venv
    . venv/bin/activate

install required packages:

    pip install -r dev-requirements.txt
    python -m pytest ./tests

## Running server  
Flask comes with a built-in server, which is perfectly fine for testing and developement of algorithms

    cd ../backend
    export FLASK_APP=server
    flask run --port=5000

Open localhost:5000 in your browser. Edge and IE are not supported.

If you want the server to be visible in your local network:

    flask run --host=0.0.0.0 --port=5000

## Benchmarks
See readme in backend/experiments for further instructions.

# Compiling algolibs
Algolibs contains C++ implementations of search algorithms, determining moves for a computer player. They are not required, but have better performance than
the python-based implementations shipped with the backend.
## Shared library
Requires cmake version 3.13 or newer. Tested with gcc 8.4.0. The backend application loads .dll files on Windows, and .so files everywhere else.

    cd algolibs
    mkdir build
    cmake -S. -Bbuild/shared
    cmake --build build/shared
    mkdir -p ../backend/instance/lib/
    cp build/shared/libexhsearch/libexhsearch.so ../backend/instance/lib/

## WebAssembly
The repository contains a precompiled WebAssembly binary and runtime. If you want to compile it yourself, you need the emsdk.

    cmake -S. -Bbuild/wasm -DCMAKE_TOOLCHAIN_FILE=~/emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DCOMPILE_TO_WASM=ON
    cmake --build build/wasm
    cp build/wasm/libexhsearch/libexhsearch.js ../backend/static/wasm/
    cp build/wasm/libexhsearch/libexhsearch.wasm ../backend/static/wasm/

The distribution folder is overwritten if you build the web-client. To keep your versions of the WebAssembly files, put them in 

    web-client/public/wasm/


