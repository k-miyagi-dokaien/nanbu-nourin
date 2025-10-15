# nanbu-nourin 試作ツールの使い方

- 位置: `projects/nanbu-nourin`
- 入力: テキスト（貼り付け or `.txt`）、テンプレJSON
- 出力: `tokki.html`, `tokki.md`, `template.json`

## 1) スタティック利用（推奨）

1. ブラウザで `web/index.html` を開く
2. 方法A: テキスト貼り付け → 「解析する」
3. 方法B: 「テキストを読み込み」で `.txt` を選択
4. 方法C: 「テンプレJSONを読み込み」で JSON を選択
5. 条項をチェックで除外 → プレビュー確認 → HTML/Markdown/JSON をダウンロード

## 2) 補足: 簡易HTTPサーバでの閲覧

ローカルの相対パス読込（サンプル）は `file://` では制約される場合があります。簡易HTTPサーバで配信するか、手動でファイルを選択してください。

```
# 例: Python 簡易サーバ（プロジェクト直下で）
python3 -m http.server -d projects/nanbu-nourin 8080
# → http://localhost:8080/web/ にアクセス
```

## 実装ノート

- 条見出しは次をサポート:
  - 「第n条（見出し）」の同一行形式
  - 直前行が「（見出し）」で次行が「第 n 条」の分割形式
  - 「第 1 条」のような半角スペース入りも許容
- 採番は除外後に 1 から連番で再採番
- 出力の印刷は CSS の `page-break-before` で制御（初回は除外）

