# 裏取り台帳（量子）

**go.jp・nature.com・arxiv・itmedia など、原典はほぼ全て開けない。**
以下は複数の検索結果が一致したもの。**公開前に ◎印を石名坂側で開いて確認すること。**

## 記事の背骨（自分で裏を取った）

| 事実 | 出典 |
|---|---|
| **2025年ノーベル物理学賞**：John Clarke、Michel H. Devoret、John M. Martinis。<br>「電気回路における巨視的量子トンネル効果とエネルギーの量子化の発見」。<br>実験は**1984〜85年**、**ジョセフソン接合**を使った超伝導回路 | ◎ノーベル財団 https://www.nobelprize.org/prizes/physics/2025/press-release/ ／Physics World https://physicsworld.com/a/john-clarke-michel-devoret-and-john-martinis-win-the-2025-nobel-prize-for-physics/ |
| Martinis氏は**元Googleの量子ハードウェア責任者** | The Quantum Insider https://thequantuminsider.com/2025/10/07/clarke-devoret-and-martinis-win-2025-nobel-prize-in-physics-for-revealing-quantum-effects-in-macroscopic-circuits/ |
| **2025年は国連が定めた「国際量子科学技術年」**（決議 A/RES/78/287、2024年6月7日採択。主導はUNESCO）。量子力学100年 | ◎UNESCO https://www.unesco.org/en/years/quantum-science-technology ／国連 https://digitallibrary.un.org/record/4052700 |
| **2022年ノーベル物理学賞**：Aspect、Clauser、Zeilinger。もつれ光子の実験とBell不等式の破れ | ◎ノーベル財団 https://www.nobelprize.org/prizes/physics/2022/press-release/ |

→ **1984年の実験 → 1999年のNECの量子ビット → いまのGoogle・IBM。** 一本につながる。
   **基礎研究が実を結ぶのに40年。** その40年目に日本の会社が実機づくりから降りた。

## 記事の中心に据える誤解

### 誤解「重ね合わせで、すべての答えを同時に計算する」
**これが最もよく見る説明で、専門家が最も困っている説明。**

- Scott Aaronson（テキサス大）のブログの**キャッチフレーズそのもの**が、
  「量子コンピュータは、すべての可能な解を一度に試して難問を瞬時に解くわけではない」という趣旨。
  https://scottaaronson.blog/ ／ 「Speaking Truth to Parallelism」という分類まである https://scottaaronson.blog/?cat=17
- **IBM公式ブログ**も「量子コンピュータがあらゆる解を並列に探索して最適化問題を効率的に解けるという
  初期の主張は誤解であり、いまだに時々見かける」と書いている
  https://www.ibm.com/quantum/blog/optimization-white-paper
- 日本語：Qmedia https://www.qmedia.jp/misunderstanding-of-qc/

**言えること：**
> たくさんの可能性を「抱える」ことはできる。でもそのまま覗くと、でたらめな答えが1つ返るだけ。
> 本当の技は、**間違った答えどうしを打ち消し合わせて消し、正しい答えだけを残す**こと。
> 波の山と谷がぶつかると平らになる、あの打ち消し合い。
> だから「全部試す機械」ではなく「**間違いを消す機械**」と言ったほうが実態に近い。

## 比喩の線引き（仕組み担当より。記事に直結）

### 使える
- **波の打ち消し合い**（最推奨）。ノイズキャンセリングヘッドホンと同じ原理
  → 壊れる場所：量子の「波」は複素数の確率振幅。物理的に揺れている実体ではない
- **彫刻**（石から余計な部分を削り落とす）
  → 壊れる場所：彫刻家は完成形を知っているが、設計者が知るのは「打ち消し方」だけ

### 使えない
- **「すべての道を同時に歩く迷路」** → 誤解①に直行。**使わない**
- **「並行世界で手分けして計算」** → 多世界解釈という「解釈」。実験で決着していない
- **「0と1を同時なので2ⁿ倍のメモリ」** → 取り出せるのは測定1回につきnビット。Holevoの限界に反する明確な誤り
- **「双子が離れていても同じことを感じる」** → 古典的相関そのもの。**Bell不等式の破れが否定した描像**。
  2022年のノーベル賞の中身を真逆に説明することになる
- **コイン** → 位相がない／比率が50%固定／測定が状態を壊さない、の3点で壊れる

## 他社の主張と、確かめられたことの区別

| 発表 | 会社の主張 | 確かめられたこと |
|---|---|---|
| **Microsoft「Majorana 1」**（2025年2月19日） | 「世界初のトポロジカル量子ビット8個」 | **Nature編集部が査読資料に**「本原稿の結果は、報告されたデバイス中にマヨラナ・ゼロモードが存在する証拠を示すものではない」と明記。<br>◎Nature https://www.nature.com/articles/s41586-024-08445-2 ／Science https://www.science.org/content/article/debate-erupts-around-microsoft-s-blockbuster-quantum-computing-claims ／Physics World https://physicsworld.com/a/experts-weigh-in-on-microsofts-topological-qubit-claim/ |
| **Google Sycamore**（2019） | 「古典スパコンで1万年」 | 古典側が追い上げた。◎Science「Ordinary computers can beat Google's quantum computer after all」https://www.science.org/content/article/ordinary-computers-can-beat-google-s-quantum-computer-after-all |
| **Google Willow**（2024年12月） | 誤り訂正のしきい値を下回った | **Nature査読済み。**符号距離を2上げるごとに論理誤り率が約半分（Λ=2.14）。<br>◎Nature https://www.nature.com/articles/s41586-024-08449-y |

→ **記事を貫かせる一文：この分野では、企業の発表と、科学的に確かめられたことの間に、しばしば大きな隔たりがあります。**
   これは印象ではなく、**Nature編集部自身が査読資料に書いた**という記録に残る事実。

## 数字（採用）

| 事実 | 出典 |
|---|---|
| 理研・富士通が**256量子ビット**機を2025年4月22日に発表。外部提供開始 | ◎理研 https://www.riken.jp/pr/news/2025/20250422_1/index.html |
| IBMは1,121量子ビットのCondorのあと、**133量子ビットのHeronを主力にした**。数より質へ | IBM https://www.ibm.com/quantum/blog/quantum-roadmap-2033 |
| Quantinuum Heliosは**98量子ビット**で2量子ビット忠実度99.921%（業界最高水準） | Quantinuum https://www.quantinuum.com/press-releases/ ／MIT Tech Review https://www.technologyreview.com/2025/11/05/1127659/ |
| RSA2048を破る見積もりは**2,000万量子ビット**（2021年）→ **100万未満**（2025年）と下がってきている | Gidney & Ekerå, Quantum 5, 433 https://quantum-journal.org/papers/q-2021-04-15-433/ ／ https://arxiv.org/abs/2505.15917 |
| **Google は2026年3月、超電導に加えて中性原子方式にも取り組むと発表**（二本立て） | ◎Google公式 https://blog.google/innovation-and-ai/technology/research/neutral-atom-quantum-computers/ ／The Quantum Insider ／HPCwire ／DCD |
| **極低温が要るのは超電導方式（とシリコン）。中性原子は希釈冷凍機不要**、イオントラップも量子ビット自体はミリケルビン不要 | QuEra https://www.quera.com/glossary/dilution-refrigerator ／PostQuantum |
| NISQ は John Preskill が2018年に提唱（Quantum 2, 79） | ◎Quantum誌 https://quantum-journal.org/papers/q-2018-08-06-79/ |

## 採用しない

| 内容 | 理由 |
|---|---|
| 「世界最大は6,100量子ビット」（Caltech） | **原子を並べて保持した成果**で、それで計算したわけではない。書くと必ず誤解を招く |
| 1論理量子ビット＝1,457物理量子ビット | 単一の二次情報。条件不明。**桁として「千〜万」**にとどめる |
| QuEraの96論理量子ビット（2026年1月） | アグリゲーター2件のみ。Nature本体で未確認 |
| Atom Computingの24論理量子ビット | 単一ソース |
| 中国 Xiaohong 504量子ビット | 単一ソース |
| 各国の投資額の比較 | 集計範囲がバラバラ。**日本は円建て約1,000億円とドル建て74億ドルで10倍ずれる。使わない** |
| Intelの量子ロードマップ | 有効な情報が得られず |
| 富士通・理研の1,000量子ビット機 | 「2026年公開予定」の発表のみ。今が2026年9月。**達成の可否を確認できていない** |
| 「スパコンで◯年かかる計算を◯秒で」 | **古典側の改良で縮む性質がある。**Sycamoreで実際に縮んだ |

## 担当の報告のうち、私が訂正したもの

**「Googleの中性原子参入は単一ソースであやしい【確度:低】」** ← **これは誤り。**
Google公式ブログ・The Quantum Insider・HPCwire・DCD・Quantum Computing Report の5系統で確認済み。
業界地図の記載も正しい。**採用する。**

## 書いてはいけない言い方

- 「すべての答えを同時に計算する」→ **測定で出るのは1通り。干渉で間違いを消している**
- 「0と1が同時」→ **位相が抜け落ちる。速い理由がまるごと説明から消える**
- 「もつれで光より速く通信できる」→ **通信不可能定理。相関はあるがメッセージは送れない**
- 「量子コンピュータは何でも速い」→ **表計算も文書作成も速くならない。Groverの加速は2乗どまり**
- 「絶対零度」→ **到達できない。「絶対零度に近い10ミリケルビン程度」。かつ超電導方式に限る**
- 「見ると壊れる」→ **「環境と相互作用すると」。観測者問題に読者を引きずり込まない**
- 「トポロジカル量子ビットが実現した」→ **Nature編集部が証拠にならないと注記している**
- 「◯年に実用化」→ **企業のロードマップは目標。主語と「目標」という語を必ず入れる**
- 「◯◯社が世界一」「日本は◯位」→ **方式も測り方も違う。順位をつけられる状態にない**

---

## 追記：一本の線（すべて裏取り済み）

| 年 | 何が起きたか | 出典 |
|---|---|---|
| **1984〜85** | Clarke・Devoret・Martinis が**ジョセフソン接合**の超電導回路で巨視的量子トンネル効果とエネルギーの量子化を実証 | ◎ノーベル財団 https://www.nobelprize.org/prizes/physics/2025/press-release/ |
| **1999** | NECの中村泰信・Pashkin・蔡兆申が「**クーパー対箱**」で量子ビットのコヒーレント制御を世界初実証。<br>Nature 398, 786-788（1999年4月29日号・表紙） | ◎Nature https://www.nature.com/articles/19718 ／理研 https://www.riken.jp/pr/closeup/2023/20230612_1/index.html |
| **2007** | トランズモン提案。論文題名が **"Charge-insensitive qubit design derived from the Cooper pair box"**<br>（＝クーパー対箱から導かれた設計）。Koch ほか、PRA 76, 042319。**共著者に M. H. Devoret** | ◎arXiv https://arxiv.org/abs/cond-mat/0703002 ／APS https://journals.aps.org/pra/abstract/10.1103/PhysRevA.76.042319 |
| **いま** | トランズモンが IBM・Google の主力量子ビット | — |
| **2025年10月** | Clarke・Devoret・Martinis にノーベル物理学賞。**Martinis は元Googleの量子ハードウェア責任者** | ◎ノーベル財団 |
| **2026年3月26日** | **理研・大阪大学が144量子ビットの「叡-Ⅱ」運用開始。**初号機「叡」（64量子ビット、2023年3月27日公開）の後継 | ◎理研 https://www.riken.jp/pr/news/2026/20260326_1/index.html ／◎阪大 https://qiqb.osaka-u.ac.jp/newstopics/pr20260326 |
| **2026年3月末** | NECが実機開発を中止したと**報じられた**（発表ではない） | 時事・日経・共同・ダイヤモンド |

**→ 1984年の実験から40年。その40年目に、日本の一社が機械づくりから降り、
   同じ月に、日本の公的機関は144量子ビットを動かし始めた。**
   「日本が量子をやめた」とは書けない。

## NECについて、書ける／書けない（担当の報告と一致）

**書ける**
- 実機（ハードウェア）の開発を2026年3月末に取りやめたと**報じられた**
- それが**9月に報道で明らかになった**（3月末から約5か月のタイムラグ）
- 量子コンピューティング技術やサービスの開発は続けるとされる
- **NEC自身は「撤退」「中止」という言葉を使っていない。**広報の正式回答は
  「実用化に向けた技術の見極めを進めるとともに、産業化に向けた取り組みを進めている」
- NECは2023年10月、両氏のC&C賞受賞にあたり「世界で初めて実現」と公式に表彰していた
  ◎NEC https://jpn.nec.com/press/202310/20231010_01.html

**書けない**
- 「NECが発表した」（**していない**）
- 「量子コンピュータから撤退した」（実機開発の話）
- 止めたのがゲート型かアニーリング型か（**報道は方式を特定していない**）
- 移籍した研究者の人数・氏名（**公表されていない**）
- **「日本の投資額は米国の5割」（日経の見出し）**
  → 別の日経記事は「日本7億ドル／米国37億ドル」＝**約19%**。デロイトも「米国は日本の約5倍」。
  **集計基準が違い、数字が矛盾する。この数字は書かない**
- NECの経営判断への評価（「出遅れた」など。報道が言っていない）
- 共同通信の「欧米は数百量子ビット、NECは8量子ビット」という並置
  → NECの8量子ビットは**産総研との量子アニーリングマシン**。**方式の違う数字の並置。転記しない**

## 便乗商法について：重要な空振り

**「量子」を冠した商品を名指しして処分・注意喚起した公的機関の発表は、一件も見つからなかった。**
消費者庁（景表法・特商法）、国民生活センター、公取委、厚労省、金融庁、東京都——すべて空振り。

→ **「国民生活センターが量子○○に注意喚起している」とは書けない。**
→ 書けるのは「**今回調べた範囲では見つかりませんでした**」と、
   周辺の事実（科学用語で健康効果をうたった商品が景表法違反で措置命令を受けた例＝水素水関連）まで。
→ 着地は **「判断がつかないときは消費者ホットライン188へ」**。断定を伴わず、読者に実害がない。

**絶対に書かない**：特定の商品名・会社名を挙げて「詐欺」「効果がない」と書くこと。
公的な裏づけがないまま、名誉毀損のリスクだけを会社に持ち込む。
**「量子とつく商品はすべて怪しい」も誤り**（量子センシング、MRI関連、PQCなど本物がある）。

## 暮らしへの影響（採用）

| 事実 | 出典 |
|---|---|
| G7の文書が「**Harvest now, decrypt later**」（いま暗号文を盗み、将来解読する）に言及。<br>金融機関に監視と検討の開始を推奨 | ◎金融庁 https://www.fsa.go.jp/inter/etc/20240926/quantum_letter.html ／◎日本銀行 https://www.boj.or.jp/intl_finance/meeting/group/gro240926a.htm （2024年9月26日、2機関が同じ文書を公表） |
| **個人が自分で暗号を入れ替える必要はない。**PQCへの移行はOS・ブラウザ・事業者側で進む | 官庁が一般消費者に対応を求めた発表は**見つからなかった** |
| すでにApple(iMessage)、Signal、Chromeで耐量子暗号が入り始めている | PQShield ほか（**版番号・時期は細かく書かない**） |
| **「耐量子暗号(PQC)」と「量子暗号(QKD)」は別物。**記事では「耐量子暗号」で統一 | CRYPTREC ほか |
| RSA2048を破る見積もりは2,000万量子ビット(2021)→100万未満(2025)。現在の最先端は百個台 | Gidney & Ekerå ／ arXiv:2505.15917 |

**書かない**：「2030年にRSAは使えなくなる」（根拠のNIST IR 8547は**草案段階**）。
CRYPTREC改定日2026年3月30日（**原文未確認。書くなら総務省ページで要再確認**）。
「金融庁が銀行に要請」（日経1件のみ、金融庁の一次発表を確認できず）。
富士通「デジタルアニーラ」を量子の実用例として紹介すること（**量子ではなく専用デジタル回路**）。
