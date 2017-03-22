# cess
A simple framework for agent-based modeling which includes support for distributed simulations.

(short for cesspool) 

## Installation
To use cess as-is, just install via pip

    pip install cess

## Development:
To run a developent version to add changes to cess, do something like:

    virtualenv venv #make a virtualenv
    . ./venv/bin/activate #start the env
    pip -r requirements.txt #install tools/libs
    ./runtest.sh #run unit-tests
    
## Distributed support

There are three components to the distributed simulation support:

- the Workers, which perform simulation steps locally
- the Arbiter, which manages workers and mediates their communication
- the Cluster, which communicates to the Arbiter (i.e. sends commands to the cluster)

To run the Arbiter:

    cess arbiter <host:port>

To run a node of Workers (one worker per core):

    cess node <arbiter host:port>

## License

The MIT License (MIT)

Copyright (c) 2016 Francis Tseng

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
