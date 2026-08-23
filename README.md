# timetable-conventions

timetable プロジェクトの共通規約の正本。親リポジトリ `takayanag-i/timetable` と、そこにネストした `spring` `fastapi` `front-app` `infra` `playwright` が、submodule として同じ実体を参照する。

規約を子リポジトリへコピーしない。コピーすれば grep が古い側に当たる。

## 中身

| パス | 内容 |
|---|---|
| `CONVENTIONS.md` | 規約の条文。第1章から第5章、第1条から第27条 |
| `doc-lint/lint.py` | Markdownの執筆規約を機械的に検査する |
| `doc-lint/SKILL.md` | 検査の使い方と、見ているもの・見ていないもの |
| `ci/check-pinned.sh` | 参照側が固定しているコミットが、この正本の `main` と一致するかを検査する |

条文とその検査を同じ配布路に載せている。規約を変えると検査も同時に届く。

## 参照する側の設定

```bash
git submodule add https://github.com/takayanag-i/timetable-conventions.git .agents/conventions
```

参照側の `CLAUDE.md` は冒頭に次の1行を置く。Claude Code がこの記法で条文を読み込む。

```
@.agents/conventions/CONVENTIONS.md
```

参照側のCIは、`actions/checkout` に `submodules: true` を渡したうえで次の2つを流す。

```bash
python3 .agents/conventions/doc-lint/lint.py .
.agents/conventions/ci/check-pinned.sh
```

`check-pinned.sh` は引数を省くと `.agents/conventions` を見る。別の場所に置いたときはそのパスを渡す。参照先のURLは `.gitmodules` から読む。

## 条文を変えるとき

このリポジトリへPRを出す。マージしたあと、参照側で submodule を進めるPRを別に出す。参照側が古いまま止まると `check-pinned.sh` が落ちる。

## 条文が親リポジトリを指すとき

条文は `docs/` を親リポジトリ https://github.com/takayanag-i/timetable のものとして書く。子リポジトリから相対パスで解決しないため、本文のリンクは絶対URLにする。
