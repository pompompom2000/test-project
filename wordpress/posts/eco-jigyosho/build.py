# -*- coding: utf-8 -*-
u"""「いわて地球環境にやさしい事業所」三つ星認定の記事本文を組み立てて article.html に書き出す。
数字は岩手県の実施要領（令和6年9月2日改正）と認定事業所一覧（令和8年8月3日現在）から写した。"""
import io, os

def p(t):
    return (u'<!-- wp:paragraph {"fontSize":"medium"} -->\n'
            u'<p class="has-medium-font-size">%s</p>\n<!-- /wp:paragraph -->\n\n' % t)
def h3(t):
    return (u'<!-- wp:heading {"level":3,"fontSize":"medium"} -->\n'
            u'<h3 class="wp-block-heading has-medium-font-size">%s</h3>\n<!-- /wp:heading -->\n\n' % t)
def ul(items, medium=True):
    a = u' {"fontSize":"medium"}' if medium else u''
    c = u' has-medium-font-size' if medium else u''
    li = u''.join(u'<!-- wp:list-item -->\n<li>%s</li>\n<!-- /wp:list-item -->\n' % i for i in items)
    return u'<!-- wp:list%s -->\n<ul class="wp-block-list%s">\n%s</ul>\n<!-- /wp:list -->\n\n' % (a, c, li)
def table(head, rows, cap):
    th = u''.join(u'<th>%s</th>' % x for x in head)
    tr = u''.join(u'<tr>%s</tr>' % u''.join(u'<td>%s</td>' % x for x in r) for r in rows)
    return (u'<!-- wp:table {"fontSize":"medium"} -->\n'
            u'<figure class="wp-block-table has-medium-font-size"><table><thead><tr>%s</tr></thead>'
            u'<tbody>%s</tbody></table><figcaption class="wp-element-caption">%s</figcaption></figure>\n'
            u'<!-- /wp:table -->\n\n' % (th, tr, cap))
def a(href, text, ext=False):
    return u'<a href="%s"%s>%s</a>' % (href, u' target="_blank" rel="noopener"' if ext else u'', text)

S = u'https://www.ishinazaka.co.jp/'
KEN = u'https://www.pref.iwate.jp/kurashikankyou/gx/ontai/1067284.html'
YORYO = u'https://www.pref.iwate.jp/_res/projects/default_project/_page_/001/067/284/r60902_yasashijigyoushoyoryo.pdf'
ICHIRAN = u'https://www.pref.iwate.jp/_res/projects/default_project/_page_/001/067/285/nitnei_260801v3.pdf'
ICHIRAN_PAGE = u'https://www.pref.iwate.jp/kurashikankyou/gx/ontai/1067285.html'
IES = S + u'ies-step1-shutoku/'

b = u''
b += p(u'令和8年10月16日付で、岩手県から<strong>「いわて地球環境にやさしい事業所」の認定書</strong>が届きました。認定区分は<strong>三つ星（★★★）</strong>、認定番号は 8-3-1、認定期間は令和8年10月16日から令和11年10月31日までです。')
b += p(u'この記事では、この制度がどういうものか、星の数が何で決まるのか、三つ星が県内でどのくらいあるのかを、県の要領と認定事業所の一覧から整理します。')
b += p(u'石名坂は、砕石を作り、ダンプで運び、重機で土木工事をする会社です。<strong>燃料と電気を日々使う仕事だからこそ、二酸化炭素を減らす取り組みは、他人事として書ける立場ではありません。</strong>')

b += h3(u'「いわて地球環境にやさしい事業所」とは')
b += p(u'岩手県が平成16年から続けている認定制度です。正式には「いわて脱炭素化経営企業等認定制度」といい、<strong>二酸化炭素の排出を抑える取り組みを積極的に行っている事業所を県が認定し、広く県民に紹介する</strong>ことを目的にしています（実施要領 第1）。')
b += ul([u'申請できるのは、岩手県内に事業所を持って事業活動を行っている事業者',
         u'認定は会社ごとではなく<strong>事業所ごと</strong>',
         u'有効期間は、認定の日から<strong>3年3か月を超えない範囲</strong>で広域振興局が定める（第8）',
         u'認定された事業者は、認定マークを名刺や印刷物に使える（第7）'])
b += p(u'石名坂の認定期間が令和11年10月31日までなのは、この「3年3か月以内」の決まりによるものです。県は更新の受付を四半期ごとに行っていて、満了日は月末にそろえられています。')

b += h3(u'星は4段階。三つ星の条件は何か')
b += p(u'認定区分は一つ星から四つ星までの4段階で、上の星ほど条件が積み重なります。実施要領の第3から写すと、次のとおりです。')
b += table([u'区分', u'条件'], [
    [u'★', u'次の3つすべて。（1）電力・重油・ガス・自動車燃料などの使用量削減に向けた具体的な計画と取り組みがある。（2）従業員のマイカー通勤による排出を抑える取り組みがある（ノーマイカーデー、エコドライブの啓発など）。（3）<strong>エコスタッフ</strong>が常駐している'],
    [u'★★', u'★に加えて、環境マネジメントシステムを保有している'],
    [u'★★★', u'★★に加えて、<strong>ISO14001、IES（いわて環境マネジメントシステム）、エコアクション21、グリーン経営などの認証を取得している</strong>'],
    [u'★★★★', u'★★★に加えて、エネルギー使用量の削減など、二酸化炭素の排出抑制の<strong>取り組みの成果が認められる</strong>'],
], u'出典：岩手県「いわて地球環境にやさしい事業所」認定事業実施要領 第3（令和6年9月2日改正）')
b += p(u'「エコスタッフ」は、要領で3通りに決まっています。県が開く「エコスタッフ養成セミナー」を受けた人、環境社会検定試験（eco検定）に合格して1年以上事業所の環境活動に携わっている人、環境省の「脱炭素アドバイザー」の資格を持つ人のいずれかです。')
b += p(u'つまり三つ星は、<strong>計画と通勤対策とエコスタッフ（一つ星）、仕組み（二つ星）、その仕組みが外の審査を通っていること（三つ星）</strong>の三段重ねです。石名坂は' + a(IES, u'2026年8月11日にIESステップ1の認証を取得') + u'しており、これが三つ星の条件にあたります。')

b += h3(u'県内で三つ星は13事業所')
b += p(u'県が公表している認定事業所の一覧（令和8年8月3日現在）では、認定は全部で<strong>311事業所</strong>です。内訳は、四つ星155、<strong>三つ星13</strong>、二つ星46、一つ星97。三つ星のうち11事業所が盛岡広域で、県南と県北が1事業所ずつです。')
b += p(u'三つ星が四つ星より少ないのは、意外に思えるかもしれません。四つ星は「成果が認められること」が条件なので、長く取り組んできた事業所が三つ星を経て四つ星に上がっていき、三つ星は<strong>認証を取ったばかりの事業所が通る段階</strong>になっているためだと読めます。石名坂は、ちょうどその入口に立ったところです。')
b += p(u'なお、この一覧は8月3日現在のものなので、10月16日に認定された石名坂はまだ載っていません。次の更新で掲載される見込みです。')

b += h3(u'認定を受けて、何が変わるのか')
b += p(u'まず、認定マークを名刺や印刷物に使えるようになります。県の案内によると、認定事業所には、県営建設工事の競争入札参加資格審査での加点（三つ星・四つ星が対象）、産業廃棄物処理業者の格付けでの加点、省エネ設備の補助金や融資での優遇などがあるとされています。')
b += p(u'一方で、県がはっきり書いていることがあります。<strong>この認定は事業所の取り組みに対するもので、扱っている商品やサービスの環境性能を保証するものではない</strong>、という点です。石名坂の砕石が「環境にやさしい砕石」になったわけではありません。会社としての取り組みが認められた、ということです。')

b += h3(u'次の目標は、四つ星')
b += p(u'四つ星との差は「成果」です。燃料と電気の使用量を、計画どおりに減らせたかどうかを数字で示す必要があります。IESステップ1で作った環境改善計画は、まさにこの数字を追いかける仕組みです。認定期間の3年のあいだに、ダンプと重機の燃料、事務所と工場の電気の使い方を見直し、結果を数字で残していきます。')
b += p(u'石名坂は' + a(S + u'kitakamigawa-cleanup/', u'北上川流域一斉清掃活動') + u'にも毎年参加しています。川を掃除することと、燃料を減らすことは、どちらも「盛岡で仕事をさせてもらっている会社」としての、同じ一つの姿勢だと考えています。')

b += h3(u'まとめ')
b += ul([u'令和8年10月16日付で、「いわて地球環境にやさしい事業所」の<strong>三つ星</strong>に認定されました（認定期間は令和11年10月31日まで）',
         u'三つ星の条件は、計画・通勤対策・エコスタッフ、環境マネジメントシステム、そしてIESなどの認証取得',
         u'県内の認定は311事業所で、三つ星は13事業所（令和8年8月3日現在）',
         u'次の四つ星には「成果」が要ります。3年間、数字で示していきます'])
b += p(u'<small>※本稿は2026年10月26日時点の情報です。認定の基準は岩手県の実施要領（令和6年9月2日改正）、認定事業所の数は県の一覧（令和8年8月3日現在）によります。制度の詳細は岩手県のページでご確認ください。</small>')

b += h3(u'参考・出典')
b += ul([a(KEN, u'岩手県「いわて脱炭素化経営企業等認定制度」（「いわて地球環境にやさしい事業所」）の概要', True),
         a(YORYO, u'岩手県「いわて地球環境にやさしい事業所」認定事業実施要領（令和6年9月2日改正、PDF）', True),
         a(ICHIRAN, u'岩手県 認定事業所一覧表（令和8年8月3日現在、PDF）', True) + u'／' + a(ICHIRAN_PAGE, u'一覧のページ', True),
         a(IES, u'IESとは？いわて環境マネジメントシステムを取得（石名坂ブログ）'),
         a(u'https://iesiwate.org/about.html', u'IESとは｜いわて環境マネジメントフォーラム', True)], medium=False)

HERE = os.path.dirname(os.path.abspath(__file__))
tail = io.open(os.path.join(HERE, 'tail.html'), encoding='utf-8').read()
io.open(os.path.join(HERE, 'article.html'), 'w', encoding='utf-8').write(b + tail)
print(u'書き出しました', len(b + tail))
