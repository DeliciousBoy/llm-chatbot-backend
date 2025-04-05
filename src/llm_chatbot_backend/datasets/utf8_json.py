import json
from pathlib import Path

from kedro.io import AbstractDataset
from kedro.io.core import (
    get_filepath_str,
    get_protocol_and_path,
)


class Utf8JSON(AbstractDataset):
    def __init__(self, filepath: str, save_args=None, load_args=None):
        self._protocol, self._path = get_protocol_and_path(filepath)
        self._filepath = Path(filepath)
        self._fs_args = {"mode": "r", "encoding": "utf-8"}
        self._save_args = {"indent": 2, "ensure_ascii": False}
        self._load_args = {}
        if save_args:
            self._save_args.update(save_args)
        if load_args:
            self._load_args.update(load_args)

    def _load(self) -> dict:
        with self._fs_open("r") as f:
            return json.load(f, **self._load_args)

    def _save(self, data: dict) -> None:
        with self._fs_open("w") as f:
            json.dump(data, f, **self._save_args)

    def _fs_open(self, mode):
        from fsspec import open as fs_open

        return fs_open(
            get_filepath_str(self._filepath, self._protocol),
            mode=mode,
            encoding="utf-8",
        )

    def _describe(self):
        return dict(filepath=self._filepath)
