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

## 複勝の下限が効いている馬を調べる

複勝には最低払戻100円（1.0倍）の下限がある。人気が集中しすぎた馬は
オッズがこの下限に張り付き、本来の確率に見合わない安さで止まる。
逆に言えば、実力が抜けた1番人気の複勝は割安になりうる。
それが実際に起きているかを全レースで確かめる。

```
python3 tools/collect/collect_place_ev.py    # → place_ev.csv
python3 tools/place_ev.py place_ev.csv       # 集計して回収率を出す
```

複勝の払戻はプールの分配で決まるため**事前オッズは遡れない**。
代わりに単勝オッズを人気の集中度の代理指標として使う。
単勝1.5倍の馬なら複勝は1.0〜1.1倍に張り付いているので実用上は足りる。

回収率が複勝の払戻率80%を超える帯があれば、下限の効果が実在することになる。
上位人気帯は標本が少ないので、Wilson法の信頼区間を必ず添えて判断すること。

## 騎手のリーディングと回収率

公表されているリーディングは勝利数の順位表で、回収率までは載らない。
「よく勝つ騎手」と「買って得な騎手」は別物なので、自前で両方を出す。

```
PLACE_EV_OUT=jockey_ev.csv python3 tools/collect/collect_place_ev.py
python3 tools/jockey_leading.py jockey_ev.csv 100   # 100騎乗以上を対象
```

collect_place_ev.py は騎手名と調教師名も取るので、同じCSVから
複勝の下限効果の検証と騎手の回収率分析の両方ができる。

回収率は分散が大きいため、95%信頼区間を必ず併記する。
点推定で100%を超えても、区間が100%をまたぐなら偶然の範囲と判断すること。

## 取得の作法

netkeiba には公開APIが無いため、サイトのHTMLと内部のAJAXエンドポイントから
取得しています。利用規約に自動取得を名指しで禁じる条項はありませんが、
第16条12号が「運営に支障を与える行為」を禁じているため、**私的利用であっても**
同時接続数を3、リクエスト間隔を0.7秒に抑えています。

```
FETCH_WORKERS=3 FETCH_INTERVAL=0.7 python3 tools/collect/fetch_horses.py
```

なお規約第14条は私的利用の範囲を超える複製・販売・出版を、第15条は営利目的の
利用を禁じています。**取得したデータを含むこのリポジトリを公開する場合は、
`data/validation*/` を削除する必要があります。**

正規のデータ源が必要になった場合は JRA-VAN Data Lab.（月額2,090円、SDKは無料）
を使ってください。ただし JV-Link は Windows の ActiveX 前提です。
