# 量子コンピュータ解説記事 ／ 制作メモ

2026年9月14日 着手。きっかけはNECの報道。

## この記事の立ち位置

読者：盛岡周辺の一般のお客様と、地元の取引先・同業者。
狙い：**仕組みを、嘘をつかずにかみ砕く。** そのうえで
「何がすごいか」と**同じ重さで「どこが誤解されているか」**を渡す。

比喩は必ずどこかで破綻する。**どこまでなら使えて、どこから嘘になるか**を
自分で把握したうえで書く。

## きっかけのニュース ── 前提の訂正を2つ

### ①「NECが量子を発見した」ではない
NECが1999年に世界で初めて実現したのは **固体素子による超伝導「量子ビット」**。
量子そのものの発見ではない。

- 論文：Y. Nakamura, Yu. A. Pashkin and J.-S. Tsai,
  "Coherent control of macroscopic quantum states in a single-Cooper-pair box",
  **Nature 398, 786-788 (1999)**。**1999年4月29日号の表紙**。
- 著者は3名。**中村泰信・パシキン・蔡兆申。**「中村・蔡」の2名で書かない。
- 中身：ジョセフソン接合を用いた「クーパー対箱」で、
  基底状態と励起状態の重ね合わせを制御した。
- これが IBM・Google の超伝導方式の源流とされる。

### ②「量子コンピュータから撤退」ではない（そして断定できない）
- 報じられているのは **実機（ハードウェア）の開発中止。**
- 時期は **2026年3月末**。それが **9月7日までに分かった**（時事通信）。
  **NECの発表ではなく、報道が先行している。**
- **NECの広報は「コメントは差し控える」と回答。**
  そのうえで「量子コンピュータの活用について、実用化に向けた技術の見極めとともに、
  産業化に向けた取り組みも進めている」とコメントしたと報じられている。
- ITmediaの見出しも「**中止か**…報道」と確定を避けている。

**→ この記事では「NECが撤退した」と断定しない。**
   書けるのは「複数の報道によれば〜とされています」
   「NECの広報は〜と回答したと報じられています」まで。
   チェック項目③（他社のことを断定していないか）に直接あたる。

## 出典（きっかけ部分）

| 事実 | 出典 |
|---|---|
| 実機開発を3月末に中止、7日までに判明 | 時事通信 https://www.jiji.com/jc/article?k=2026090700732&g=eco |
| 「量子コンピューターの名門」NECが実機開発中止／日本の投資額は米国の5割 | 日経 https://www.nikkei.com/article/DGXZQOUC0745B0X00C26A9000000/ |
| 実機開発を中止（続報） | 日経 https://www.nikkei.com/article/DGXZQOUC051KF0V00C26A9000000/ |
| 「中止か」「報道」として扱う | ITmedia https://www.itmedia.co.jp/news/article/2609/08/2000001250/ |
| 広報の正式回答「技術の見極めを進めている」 | ダイヤモンド https://news.yahoo.co.jp/articles/5c7fd19d04dcb5cb9447855e0c92e3d773cdbdbb |
| 1999年の成果・C&C賞 | NEC https://jpn.nec.com/press/202310/images/1001-01-01.pdf |
| 1999年の成果の解説 | 理研 https://www.riken.jp/pr/closeup/2023/20230612_1/index.html ／東大 https://www.u-tokyo.ac.jp/focus/ja/features/voices066.html |

## 調べものの制約（この日の環境）

- WebSearch：**使える**
- WebFetch：**go.jp はほぼ全滅。itmedia.co.jp も遮断を確認**
- 有料記事（日経・ダイヤモンド）は**本文を読めない。**見出しと要約まで
  → **原典は誰も読んでいない。**公開前に石名坂側で開いて確認する

## 構成案（仮）

1. ニュースの整理 ── 何が起きて、何が起きていないのか
2. そもそも量子ビットとは何か
3. 「すべての答えを同時に計算する」は本当か ← ここが山
4. なぜ冷やすのか／なぜ難しいのか（デコヒーレンス・誤り訂正）
5. 何がすごいのか（できることの中身）
6. 何がすごくないのか（できないこと・時期の見通しの幅）
7. 暮らしへの影響 ── 暗号の話
8. 「量子」を名乗る怪しい話
9. まとめ／参考・出典

## 書式

既存記事に合わせる（`../ai-web3/plan.md` と同じ）。
**空白で見た目を作らない。** 貼り付けで落ちる。

---

## 方式の分け方（2026年9月14日 追記）

石名坂から日経BPの業界地図（2026年版）の画像を受領。
**画像そのものは著作権があるため使えない。** 日経BOOKプラス
「量子コンピューターの業界地図2026」https://bookplus.nikkei.com/atcl/column/020500658/020500004/

ただし**方式の分け方は事実**なので、**自分たちで図を作り直せば使える。**
記事には自作のSVGを置く方針。

| 方式 | 主なプレイヤー（図より） |
|---|---|
| 超電導 | IBM(米)、Google(米)、富士通(日)、本源量子計算科技(中)、IQM(フィンランド)、Rigetti(米) |
| 中性原子 | Google(米)、QuEra(米)、Atom Computing(米)、Pasqal(仏) |
| イオントラップ | Quantinuum(米)、IonQ(米)、Qubitcore(日) |
| マヨラナ粒子 | Microsoft(米) |
| 光 | NTT/OptQC(日)、PsiQuantum(米)、Xanadu(カナダ) |
| シリコン | Intel(米)、日立製作所(日)、Diraq(豪) |

### 自分で確かめたこと

**「中性原子方式にGoogle」は正しい。** 当初これを疑ったが、誤りは私のほうだった。
Google Quantum AI は2026年3月、超電導に加えて中性原子にも取り組むと発表している。
超電導と中性原子を補完的な二本立てと位置づけ、中性原子チームは
Adam Kaufman 氏（コロラド大ボルダー校）が率いる。24か月以内に100量子ビット超の
プロセッサを示すとしている。2025年10月には Atlantic Quantum を買収。

- Google公式ブログ https://blog.google/innovation-and-ai/technology/research/neutral-atom-quantum-computers/
- The Quantum Insider https://thequantuminsider.com/2026/03/24/google-paves-a-two-lane-quantum-roadmap-by-adding-neutral-atom-systems/
- HPCwire https://www.hpcwire.com/2026/04/03/google-expands-quantum-efforts-to-include-neutral-atom-systems/
- DCD https://www.datacenterdynamics.com/en/news/google-expands-quantum-roadmap-to-include-neutral-atoms-as-well-as-superconducting-qubits/

**この図は、超電導の欄にNECを載せていない。** 富士通は載っている。
業界地図がすでに今回の報道を反映している。記事で触れる価値がある。

### 表記の統一
図は「超**電**導」。学術では「超**伝**導」も多い。**日経・時事・NECの報道は「超電導」。**
→ 記事では **「超電導」** に統一する。ただし引用元が「超伝導」ならそのまま引く。

### 残りの確認事項（世界の動向の担当の報告と突き合わせる）
- マヨラナ粒子方式（Microsoft）には強い異論があるはず。**図には異論が書かれていない**
- Qubitcore(日)、OptQC(日)、Diraq(豪) の実態
- 「方式は決まっていない」ことが、この図の最大のメッセージ
