<?php
/**
 * WPCode 貼り付け用（1回だけ実行する使い捨てスニペット）
 *
 * チャットボットのアイコン画像をサーバー上に生成し、メディアライブラリに登録します。
 * 端末へのダウンロードもアップロードも不要です。
 *
 * 使い方:
 *   1. WPCode → 新規スニペット追加 → 空のスニペット → コードタイプ「PHPスニペット」
 *   2. 「=== ここから ===」以降を貼り付け
 *   3. 挿入方法「自動挿入 / 管理画面のみ」（無ければ「サイト全体で実行」でも可）
 *   4. 有効化して保存 → 管理画面の上部に画像のURLが表示される
 *   5. URLをコピーして AI Engine の Icon 欄に貼る
 *   6. 済んだらこのスニペットは無効化してよい（画像は残ります）
 */

// === ここから ===

add_action( 'admin_notices', function () {

	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}

	$filename = 'izk-chat-icon.svg';
	$uploads  = wp_upload_dir();

	if ( ! empty( $uploads['error'] ) ) {
		echo '<div class="notice notice-error"><p>アップロードフォルダを取得できませんでした: '
			. esc_html( $uploads['error'] ) . '</p></div>';
		return;
	}

	$path = trailingslashit( $uploads['basedir'] ) . $filename;
	$url  = trailingslashit( $uploads['baseurl'] ) . $filename;

	// 濃紺の吹き出しに白い「？」。64×64 の座標系で作ってあります。
	$svg = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img" aria-label="砕石について質問する">'
		. '<path d="M32 6C16.5 6 4 15.6 4 27.4c0 6.7 4 12.7 10.3 16.6L11 58l13.5-7.5c2.4.5 5 .8 7.5.8 15.5 0 28-9.6 28-21.4S47.5 6 32 6z" fill="#004276"/>'
		. '<path d="M27.6 33.9c0-5.2 7-5.6 7-9.6 0-2-1.5-3.3-3.7-3.3-2.3 0-3.9 1.4-4.6 3.4l-4.8-1.8c1.3-4 4.8-6.5 9.6-6.5 5.6 0 9.4 3.2 9.4 7.8 0 6.1-7.4 6.7-7.4 10.5v.8h-5.5v-1.3z" fill="#fff"/>'
		. '<circle cx="30.4" cy="42.1" r="3.3" fill="#fff"/>'
		. '</svg>';

	// ファイルがまだ無ければ書き出す。
	if ( ! file_exists( $path ) ) {
		if ( false === file_put_contents( $path, $svg ) ) {
			echo '<div class="notice notice-error"><p>画像を書き出せませんでした。'
				. 'アップロードフォルダの書き込み権限をご確認ください: '
				. esc_html( $path ) . '</p></div>';
			return;
		}
	}

	// メディアライブラリに未登録なら登録する。
	$existing = get_posts( array(
		'post_type'      => 'attachment',
		'post_status'    => 'inherit',
		'posts_per_page' => 1,
		'fields'         => 'ids',
		'meta_query'     => array( array(
			'key'   => '_wp_attached_file',
			'value' => $filename,
			'compare' => 'LIKE',
		) ),
	) );

	if ( empty( $existing ) ) {
		$attachment_id = wp_insert_attachment( array(
			'post_mime_type' => 'image/svg+xml',
			'post_title'     => 'チャットアイコン（？マーク）',
			'post_content'   => '',
			'post_status'    => 'inherit',
		), $path );

		if ( ! is_wp_error( $attachment_id ) && $attachment_id ) {
			update_post_meta( $attachment_id, '_wp_attached_file', $filename );
		}
	}

	echo '<div class="notice notice-success"><p><strong>チャットアイコンを用意しました。</strong><br>'
		. 'このURLを AI Engine の Icon 欄に貼ってください:<br>'
		. '<code style="user-select:all;font-size:14px;">' . esc_html( $url ) . '</code></p></div>';

}, 5 );
