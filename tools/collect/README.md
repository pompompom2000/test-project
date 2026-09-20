# 検証データの集め方

モデルの重みを過去成績で検証するためのデータ収集スクリプトです。
netkeiba から取得するので、実行には時間がかかります（全体で30分程度）。

```
cd <作業ディレクトリ>

# 1. 開催日と race_id を列挙する
python3 tools/collect/list_race_days.py          # → daylist.json

# 2. 各開催日の馬場状態を調べ、道悪だった日を特定する
python3 tools/collect/screen_wet_days.py         # → probe.json

# 3. 道悪の日の全レースから、芝の重・不良レースを抜き出す
python3 tools/collect/collect_races.py           # → races_raw.json

# 4. 出走各馬の血統と全戦績を取得する
python3 tools/collect/fetch_horses.py            # → horse_cache/

# 5. レースごとの入力JSONを作る
python3 tools/collect/build_validation.py        # → data/validation/

# 6. 重みを検証する
node tools/validate.js data/validation/*.json
```

## 秋G1の検証データ

道悪に限定した検証とは別に、秋（9〜12月）のG1を集めるスクリプトもあります。

```
python3 tools/collect/collect_g1.py      # → g1_races.json（G1_YEARS で年を指定）
python3 tools/collect/fetch_horses.py    # → horse_cache/（RACES_RAW=g1_races.json）
python3 tools/collect/build_g1.py        # → data/validation-g1/
```

秋G1はほとんどが良馬場です。道悪度が0だと血統・馬体重・道悪実績の補正は
すべてゼロになるため、道悪向けの特徴量だけでは検証になりません。
`build_g1.py` は馬場状態に依存しない材料を追加で集計します。

- G1・重賞での出走数と3着内数（クラス経験）
- 同距離帯（±200m）と同競馬場での成績（距離適性・コース適性）
- 前走の着順と人気、前走からの間隔（調子とローテーション）
- 斤量、年齢、枠順、脚質

## 未来データを混ぜないこと

各馬の「良馬場／道悪成績」は、**対象レースの当日より前**の芝レースだけで集計します。
`build_validation.py` の以下の判定がその制約です。

```python
if d >= race_date:       # 対象レース当日以降は使わない
    continue
```

これを外すと、後のレース結果を使って過去を予想することになり、
検証結果が実力より良く出てしまいます。

## この検証で測れないもの

過去レースでは外厩・調教評価・厩舎コメント・パドック・当日の傾向が遡って取得できません。
したがって検証できるのは、機械的に再現できる**血統・馬体重・道悪実績・コース傾向**の
4ファクターだけです。
