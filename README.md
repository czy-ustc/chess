# Chess: A quantum chess engine with artificial intelligence.
[![Travis-CI Build Status](https://travis-ci.com/sql-machine-learning/elasticdl.svg?branch=develop)](https://travis-ci.com/sql-machine-learning/elasticdl)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<center>
    <img src="https://s1.328888.xyz/2022/07/02/LTcK.png" width="30%">
    <img src="https://s1.328888.xyz/2022/07/02/LsWF.png" width="30%">
    <img src="https://s1.328888.xyz/2022/07/03/jFDN.png" width="30%">
</center>


Chess is a python chess library that includes game engine, artificial intelligence algorithm and demonstration website.

## Installation
```
# setup.py
python setup.py install
# or pip
pip install -r requirements.txt

# If you want to debug the front-end page:
# cd chess/web
# npm install
# npm run serve
```

## Docker
```
# build
docker build . -t chess
# run
docker run -d -it -p 80:80 chess
```

## Usage
### Launch Website
```
python -m chess
# INFO:     Started server process [10676]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)
```

### Example Code
```python
from chess import Chess

chess = Chess()
print(chess.agents())
# ['Random', 'Greedy', 'Minimax', 'AlphaBeta', 'BeamSearch', 'Human']
chess.agent1 = "Greedy"
chess.agent2 = "Greedy"
chess.chessboard = []
print(chess.chessboard)
#   +------------------------+
# 8 | r  n  b  q  k  b  n  r |
# 7 | p  p  p  p  p  p  p  p |
# 6 | .  .  .  .  .  .  .  . |
# 5 | .  .  .  .  .  .  .  . |
# 4 | .  .  .  .  .  .  .  . |
# 3 | .  .  .  .  .  .  .  . |
# 2 | P  P  P  P  P  P  P  P |
# 1 | R  N  B  Q  K  B  N  R |
#   +------------------------+
#     a  b  c  d  e  f  g  h
print(chess.run())
# 'Nb1-c3'
print(chess.chessboard)
#   +------------------------+
# 8 | r  n  b  q  k  b  n  r |
# 7 | p  p  p  p  p  p  p  p |
# 6 | .  .  .  .  .  .  .  . |
# 5 | .  .  .  .  .  .  .  . |
# 4 | .  .  .  .  .  .  .  . |
# 3 | .  .  N  .  .  .  .  . |
# 2 | P  P  P  P  P  P  P  P |
# 1 | R  .  B  Q  K  B  N  R |
#   +------------------------+
#     a  b  c  d  e  f  g  h

while not chess.winner:
    chess.run()
    print(chess.chessboard)
#   +------------------------+
# 8 | r  .  b  q  k  b  n  r |
# 7 | p  p  p  p  p  p  p  p |
# 6 | .  .  n  .  .  .  .  . |
# 5 | .  .  .  .  .  .  .  . |
# 4 | .  .  .  .  .  .  .  . |
# 3 | .  .  N  .  .  .  .  . |
# 2 | P  P  P  P  P  P  P  P |
# 1 | R  .  B  Q  K  B  N  R |
#   +------------------------+
#     a  b  c  d  e  f  g  h
# ......
```

## License
Qusim is provided under the [MIT license](LICENSE).