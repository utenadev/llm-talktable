## プロジェクト固有の注意事項
- humanとのやりとりは基本、日本語。
- ソースコード内・コメントは指定されなければ英語。コミットメッセージも英語。

## MCP
use context7.

Use Serena. Only work in the current folder; do not scan parents or hidden dirs.
Get the list of changed files from `git diff --name-only`.
For each file:
- Summarize the changes in 1–2 sentences.
- Update `.serena/memories/code_layout.md` if structure or purpose changed.
Append all summaries as bullet points to `.serena/memories/key_tasks.md`.
Confirm the diff of updated memory files.

## 設計・実装
README.md, README.ja.md は最新の実装が反映されてないケースあり。

## Task
TASK_FILE=@my/3task.md 
- {{ TASK_FILE }} を読んで章単位で対応していくこと。
  - 章のタスク用にブランチを切る
  - 対象ソース単位に作業を行う
    - 必要な修正を実施
    - 完了したら、go build でエラーが出ないことを確認
    - git commit する。
  - 章のタスクが完了したら、
    - @{{ TASK_FILE }} に [x] とする
    - 修正・新規追加したしたソース名を @{{ TASK_FILE }} に追記する
  - タスク自体の追加や内容変更についたも、都度 @{{ TASK_FILE }} に追加を行うこと
