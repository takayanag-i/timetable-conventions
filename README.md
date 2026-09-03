# timetable-conventions

timetable プロジェクトの共通規約の正本。親リポジトリ `takayanag-i/timetable` と、そこにネストした `spring` `chat` `ledger` `fastapi` `front-app` `infra` `playwright` が、submodule として同じ実体を参照する。

規約を子リポジトリへコピーしない。コピーすれば grep が古い側に当たる。

## 中身

| パス | 内容 |
|---|---|
| `SDGs.md` | 13のゴールと72のターゲット |
| `doc-lint/lint.py` | Markdownの執筆規約を機械的に検査する |
| `doc-lint/SKILL.md` | 検査の使い方と、見ているもの・見ていないもの |
| `ci/check-pinned.sh` | 参照側が固定しているコミットが、この正本の `main` と一致するかを検査する |
| `proto/timetable/v1/annotations.proto` | 単位をまたぐgRPCのメソッドに採番を付ける注釈 |

条文とその検査を同じ配布路に載せている。規約を変えると検査も同時に届く。

## gRPCの採番の注釈

`grpc_id` は、単位をまたぐgRPCのメソッドが自分の採番を持つための注釈である。値は親リポジトリの `docs/基本設計/API一覧/gRPC一覧.md` の表が持つIDを指す。

```protobuf
import "timetable/v1/annotations.proto";

service TicketService {
  rpc IssueTicket(IssueTicketRequest) returns (IssueTicketResponse) {
    option (timetable.v1.grpc_id) = "GRPC0001";
  }
}
```

宣言をここに1つ置くのは、拡張の番号が資源だからである。 `google.protobuf.MethodOptions` の同じ番号を複数のリポジトリで宣言すると、両方を取り込んだ時点で衝突する。番号帯を分けても、同じ意味の注釈が単位の数だけ増える。

参照側は `buf.yaml` の入力にこのディレクトリを足す。

```yaml
version: v2
inputs:
  - directory: proto
  - directory: .agents/conventions/proto
```

生成物の置き場は参照側が決める。 この注釈から出る生成コードは、参照側の `gen/` に他のprotoと同じ規則で出す。Goの取り込み先が参照側のモジュールと食い違うときは、`buf.gen.yaml` の `opt` で対応を与える。

## 参照する側の設定

```bash
git submodule add https://github.com/takayanag-i/timetable-conventions.git .agents/conventions
```

参照側の `CLAUDE.md` は冒頭に次の1行を置く。Claude Code がこの記法で条文を読み込む。

```
@.agents/conventions/SDGs.md
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
