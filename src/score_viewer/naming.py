"""楽譜PDFのファイル名から曲名を抽出する。

命名が不揃い（区切りが `-` / `_` / 空白、序数が Horn の前後、日付・「のコピー」・
`1,3` のようなパート番号あり）なので、次の方針で曲名だけを取り出す:

  1. 拡張子と「のコピー」を除く
  2. 「(区切り)(序数)? Horn ...」以降を落とす（Horn 直前の序数だけをパートとみなす。
     曲名側の "9th"（Beethoven's 9th）や年 "2025" を誤って消さないための肝）
  3. 末尾に残るパート番号(1,3)・日付(8桁 / YYYY-MM-DD)・区切りを剥がす

例:
  "112_Beethoven's 9th - 4th Horn in F -2024-11-08.pdf" -> "112_Beethoven's 9th"
  "001_Opening Tune_2025 - Horn in F 3rd -2025-11-22 .pdf" -> "001_Opening Tune_2025"
  "021_I can't take my eyes off you_20200115_1,3 Horn in F.pdf"
      -> "021_I can't take my eyes off you"
"""
from __future__ import annotations

import re
from pathlib import Path

# 「(区切り)(Horn 直前の序数)? Horn 以降」をまとめて落とす
_PART_SUFFIX = re.compile(r"\s*[-_ ]\s*(\d+\s*(?:st|nd|rd|th)\s*)?[Hh]orn.*$")
# 末尾に残るゴミ（パート番号・日付）。年4桁は曲名の一部として残す
_TRAILERS = (
    re.compile(r"[-_ ]+\d+(?:\s*,\s*\d+)+$"),   # 1,3 / 2,4
    re.compile(r"[-_ ]+\d{4}-\d{2}-\d{2}$"),    # 2024-11-08
    re.compile(r"[-_ ]+\d{8}$"),                # 20190117
)


def extract_song_name(filename: str) -> str:
    """PDF ファイル名（basename でもフルパスでも可）から曲名を返す。"""
    name = Path(filename).stem
    name = name.replace("のコピー", "")
    name = _PART_SUFFIX.sub("", name)
    prev = None
    while prev != name:
        prev = name
        name = name.rstrip(" \t-_")
        for pat in _TRAILERS:
            name = pat.sub("", name)
    return name.strip()
