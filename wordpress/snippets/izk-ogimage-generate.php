<?php
/**
 * WPCode 貼り付け用（1回だけ実行する使い捨てスニペット）
 *
 * いま og:image に指定されている 3.87MB の PNG から、
 * SNS共有に適した 1200×630 の JPEG を作ります。
 * WordPress 内蔵の画像処理機能を使うので、外部ツールもアップロードも不要です。
 *
 * 使い方:
 *   1. WPCode → 新規スニペット追加 → 空のスニペット → コードタイプ「PHPスニペット」
 *   2. 「=== ここから ===」以降を貼り付け
 *   3. 挿入方法「自動挿入 / サイト全体で実行」
 *   4. 有効化して保存 → 管理画面の上部に、できた画像のURLが表示される
 *   5. All in One SEO → ソーシャルネットワーク で、そのURLを既定の共有画像に設定
 *   6. 済んだらこのスニペットは無効にしてよい（画像は残ります）
 */

// === ここから ===

add_action( 'admin_notices', function () {

	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}

	// 変換元。いま og:image に使われている画像のファイル名。
	$source_relative = '2025/11/Firefly_重機を消して-177871.png';

	// 出力設定。SNSの推奨は 1200×630。
	$out_name = 'izk-ogimage-1200x630.jpg';
	$width    = 1200;
	$height   = 630;
	$quality  = 82;

	$uploads = wp_upload_dir();
	if ( ! empty( $uploads['error'] ) ) {
		printf( '<div class="notice notice-error"><p>アップロードフォルダを取得できません: %s</p></div>',
			esc_html( $uploads['error'] ) );
		return;
	}

	$base = trailingslashit( $uploads['basedir'] );
	$src  = $base . $source_relative;
	$dst  = $base . $out_name;
	$url  = trailingslashit( $uploads['baseurl'] ) . $out_name;

	if ( ! file_exists( $dst ) ) {

		if ( ! file_exists( $src ) ) {
			printf( '<div class="notice notice-error"><p>変換元の画像が見つかりません:<br><code>%s</code><br>'
				. 'メディアライブラリでファイル名をご確認のうえ、スニペット内の $source_relative を直してください。</p></div>',
				esc_html( $src ) );
			return;
		}

		$editor = wp_get_image_editor( $src );
		if ( is_wp_error( $editor ) ) {
			printf( '<div class="notice notice-error"><p>画像処理を開始できません: %s</p></div>',
				esc_html( $editor->get_error_message() ) );
			return;
		}

		// 中央を切り抜いて 1200×630 ちょうどにする。
		$resized = $editor->resize( $width, $height, true );
		if ( is_wp_error( $resized ) ) {
			printf( '<div class="notice notice-error"><p>リサイズに失敗しました: %s</p></div>',
				esc_html( $resized->get_error_message() ) );
			return;
		}

		$editor->set_quality( $quality );

		$saved = $editor->save( $dst, 'image/jpeg' );
		if ( is_wp_error( $saved ) ) {
			printf( '<div class="notice notice-error"><p>保存に失敗しました: %s</p></div>',
				esc_html( $saved->get_error_message() ) );
			return;
		}

		// メディアライブラリに登録して、あとから管理できるようにする。
		$attachment_id = wp_insert_attachment( array(
			'post_mime_type' => 'image/jpeg',
			'post_title'     => 'SNS共有用画像 1200x630',
			'post_status'    => 'inherit',
		), $dst );

		if ( ! is_wp_error( $attachment_id ) && $attachment_id ) {
			update_post_meta( $attachment_id, '_wp_attached_file', $out_name );
		}
	}

	$size = file_exists( $dst ) ? size_format( filesize( $dst ) ) : '不明';

	printf(
		'<div class="notice notice-success"><p><strong>SNS共有用の画像を作りました（%s）。</strong><br>'
		. 'このURLを All in One SEO → ソーシャルネットワーク の共有画像に設定してください:<br>'
		. '<code style="user-select:all;font-size:14px;">%s</code></p></div>',
		esc_html( $size ), esc_html( $url )
	);

}, 5 );
