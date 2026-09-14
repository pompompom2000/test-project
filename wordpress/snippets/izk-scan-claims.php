<?php
/**
 * 石名坂：言い切り表現の棚卸し（調べるだけ。1文字も書き換えません）
 *
 * 使い方
 *   1. WPCode に「PHPスニペット」として貼り、「どこでも実行」で有効化する。
 *   2. WordPress の管理画面（ダッシュボードなど）を開く。
 *      画面の上に、見つかった箇所の一覧が出ます。
 *   3. 結果を確認したら、このスニペットは無効にするか削除してください。
 *
 * 安全について
 *   ・データベースは読むだけです。書き込み・更新・削除は一切しません。
 *   ・結果は管理画面にしか出ません。訪問者には見えません。
 *   ・管理者（manage_options 権限）以外には、何も表示しません。
 */

add_action( 'admin_notices', function () {

	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}

	// 探す言葉。左が探す文字、右が台帳の番号
	$phrases = array(
		'半永久的'                   => '高-11',
		'割れない'                   => '高-11',
		'踏んで割れることもなく'     => '高-11',
		'粉砕される'                 => '高-12',
		'デシベル'                   => '高-14',
		'音で撃退'                   => '高-14',
		'雑草が生えなくなる'         => '高-13',
		'雑草が生えない'             => '高-13',
		'メンテナンスフリー'         => '高-13',
		'足りなくなる心配'           => '高-15',
	);

	global $wpdb;

	$rows  = array();
	$total = 0;

	foreach ( $phrases as $needle => $tag ) {

		$like = '%' . $wpdb->esc_like( $needle ) . '%';

		// --- 1. 記事・固定ページの本文 ---
		$found = $wpdb->get_results(
			$wpdb->prepare(
				"SELECT ID, post_type, post_title, post_content
				   FROM {$wpdb->posts}
				  WHERE post_status = 'publish'
				    AND post_type IN ('post','page')
				    AND post_content LIKE %s
				  ORDER BY ID
				  LIMIT 30",
				$like
			)
		);

		foreach ( $found as $p ) {
			$n = substr_count( $p->post_content, $needle );
			$total += $n;
			$rows[] = array(
				'tag'   => $tag,
				'word'  => $needle,
				'where' => $p->post_type . ' ' . $p->ID,
				'title' => $p->post_title,
				'count' => $n,
				'ctx'   => izk_scan_context( $p->post_content, $needle ),
			);
		}

		// --- 2. カスタムフィールド（ACFなど） ---
		$meta = $wpdb->get_results(
			$wpdb->prepare(
				"SELECT post_id, meta_key, meta_value
				   FROM {$wpdb->postmeta}
				  WHERE meta_value LIKE %s
				    AND meta_key NOT LIKE '\_%%'
				  ORDER BY post_id
				  LIMIT 30",
				$like
			)
		);

		foreach ( $meta as $m ) {
			$n = substr_count( $m->meta_value, $needle );
			$total += $n;
			$rows[] = array(
				'tag'   => $tag,
				'word'  => $needle,
				'where' => 'meta ' . $m->post_id . ' / ' . $m->meta_key,
				'title' => get_the_title( $m->post_id ),
				'count' => $n,
				'ctx'   => izk_scan_context( $m->meta_value, $needle ),
			);
		}
	}

	// --- 3. post-640 の段落の重複も、ついでに数える ---
	$p640 = get_post( 640 );
	$dup  = '';
	if ( $p640 ) {
		$head = '今年は例年に比べて、雪の多い年になりました';
		$c    = substr_count( $p640->post_content, $head );
		$dup  = sprintf( '投稿640「今年は例年に比べて…」の段落： %d 回', $c );
		if ( false !== strpos( $p640->post_content, '住宅地では、道路の除雪で寄せた雪' ) ) {
			$dup .= '　／　2段落めは入っています';
		} else {
			$dup .= '　／　2段落めは入っていません';
		}
	}

	echo '<div class="notice notice-info" style="padding:14px 16px">';
	echo '<h2 style="margin:0 0 10px">石名坂：言い切り表現の棚卸し（調べただけ。何も変えていません）</h2>';
	echo '<p style="margin:0 0 10px">見つかった合計： <strong>' . intval( $total ) . ' か所</strong>';
	if ( $dup ) {
		echo '<br>' . esc_html( $dup );
	}
	echo '</p>';

	if ( empty( $rows ) ) {
		echo '<p>該当する言葉は見つかりませんでした。</p>';
	} else {
		echo '<div style="max-height:520px;overflow:auto;background:#fff;border:1px solid #ccd0d4;padding:10px">';
		echo '<table style="border-collapse:collapse;font-size:12px;width:100%">';
		echo '<tr style="text-align:left;background:#f0f0f1">'
			. '<th style="padding:5px">台帳</th><th style="padding:5px">言葉</th>'
			. '<th style="padding:5px">場所</th><th style="padding:5px">記事名</th>'
			. '<th style="padding:5px">回数</th><th style="padding:5px">前後の文</th></tr>';

		foreach ( $rows as $r ) {
			echo '<tr style="border-top:1px solid #e5e5e5;vertical-align:top">';
			echo '<td style="padding:5px;white-space:nowrap">' . esc_html( $r['tag'] ) . '</td>';
			echo '<td style="padding:5px;white-space:nowrap">' . esc_html( $r['word'] ) . '</td>';
			echo '<td style="padding:5px;white-space:nowrap">' . esc_html( $r['where'] ) . '</td>';
			echo '<td style="padding:5px">' . esc_html( $r['title'] ) . '</td>';
			echo '<td style="padding:5px;text-align:right">' . intval( $r['count'] ) . '</td>';
			echo '<td style="padding:5px;font-family:monospace">' . esc_html( $r['ctx'] ) . '</td>';
			echo '</tr>';
		}
		echo '</table></div>';
	}

	echo '<p style="margin:10px 0 0;color:#646970">'
		. 'このスニペットはデータベースを読むだけです。書き込みは行いません。'
		. '確認が済んだら、無効にするか削除してください。</p>';
	echo '</div>';
} );

/** 見つかった箇所の前後を、短く切り出す */
function izk_scan_context( $haystack, $needle ) {
	$pos = mb_strpos( $haystack, $needle );
	if ( false === $pos ) {
		return '';
	}
	$start = max( 0, $pos - 45 );
	$out   = mb_substr( $haystack, $start, 45 + mb_strlen( $needle ) + 55 );
	$out   = preg_replace( '/\s+/u', ' ', wp_strip_all_tags( $out ) );
	return '…' . trim( $out ) . '…';
}
