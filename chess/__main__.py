# Author       : czy
# Description  : Website backend engine.
#
# Copyright 2022 Zhiyuan Chen <chenzhiyuan@mail.ustc.edu.cn>

import asyncio
from pathlib import Path
from typing import Any, Coroutine, Dict, List, Optional, Union

import click
import uvicorn
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from starlette.responses import FileResponse

from chess.chess import Chess

app = FastAPI()
chess = Chess()

static = Path(__file__).parent / "web/dist"


class PlayerModel(BaseModel):
    model: str
    config: Optional[dict]


class ChessBoardModel(BaseModel):
    data: list


class ActionModel(BaseModel):
    source: Optional[list]
    target: Optional[list]


# ----------------------------------------------------------------------
# Get / Set Agent


@app.get("/api/agents/")
def agents() -> List[str]:
    """Get the list of agents."""
    return chess.agents()


@app.post("/api/init_player/{index}/")
def init_player(index: int, player: PlayerModel) -> dict:
    """Initialize players."""
    if player.config:
        if index == 1:
            chess.agent1 = player.config
        else:
            chess.agent2 = player.config
    else:
        if index == 1:
            chess.agent1 = player.model
        else:
            chess.agent2 = player.model

    return eval(f"chess.agent{index}.config()")


# ----------------------------------------------------------------------
# Get / Set ChessBoard


@app.post("/api/init_chessboard/")
def init_chessboard(pieces: ChessBoardModel) -> None:
    """Initialize a new game."""
    chess.chessboard = pieces.data
    return None


@app.get("/api/load/{id}/")
def load(id: int) -> dict:
    """Load a endgame."""
    chess.chessboard = id
    return {"chessboard": chess.data, "dead": chess.dead}


@app.get("/api/endgame/{t}/")
def endgame(t: int) -> List[Dict[str, Union[int, str, bool]]]:
    """Get a list of specific types of endgame."""
    return chess.database.search(t)


@app.get("/api/save/{name}/")
def save(name: str) -> None:
    """Save the current chess game."""
    chess.save(name)
    return None


@app.delete("/api/endgame/{id}/")
def remove(id: int) -> None:
    """Delete a endgame."""
    chess.database.remove(id)
    return None


# ----------------------------------------------------------------------
# Play Chess.


@app.get("/api/actions/")
def actions() -> list:
    """Get the list of possible actions on the current chessboard."""
    return chess.actions()


@app.post("/api/run/")
def run(action: ActionModel, response: Response) -> dict:
    """Perform one step."""
    source = action.source
    target = action.target

    args = [(source, target)] if source and target else []

    try:
        record = chess.run(*args)
        return {
            "chessboard": chess.data,
            "dead": chess.dead,
            "game_over": chess.winner.value,
            "record": record,
        }
    except TypeError:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {}


@app.get("/api/undo/")
def undo() -> dict:
    """Undo the previous step."""
    chess.undo()
    return {"chessboard": chess.data, "dead": chess.dead}


@app.get("/api/end/")
def end() -> None:
    """End the current game."""
    chess.end()
    return None


# ----------------------------------------------------------------------
# Static File.


@app.get("/")
async def get_index() -> FileResponse:
    """Home page."""
    return FileResponse(static / "index.html")


@app.get("/article/")
async def get_rule() -> FileResponse:
    """Rule description document."""
    return FileResponse(static / "article.html")


@app.get("/{whatever:path}")
async def get_static_files_or_404(whatever: str) -> FileResponse:
    """Returns the static resource file."""
    file_path = static / whatever
    if file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(static / "index.html")


async def server(port: int, log_level: str) -> Coroutine[Any, Any, None]:
    """Server configuration."""
    config = uvicorn.Config(
        "chess.__main__:app", host="0.0.0.0", port=port, log_level=log_level
    )
    await uvicorn.Server(config).serve()


@click.command()
@click.option("-p", "--port", help="Bind socket to this port.", type=int, default=80)
@click.option("-l", "--log-level", help="Log level.", default="info")
def main(port: int, log_level: str) -> None:
    asyncio.run(server(port, log_level))


if __name__ == "__main__":
    main()
