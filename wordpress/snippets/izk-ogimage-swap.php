<?php
/**
 * WPCode 貼り付け用（常時有効にしておくスニペット）
 *
 * テーマが出力している og:image のURLを、軽量化した画像に差し替えます。
 * テーマのファイルは一切変更しません。
 *
 * 前提: izk-ogimage-generate のスニペットで
 *       izk-ogimage-1200x630.jpg を作成済みであること。
 *
 * 使い方:
 *   1. WPCode → 新規スニペット追加 → 空のスニペット → コードタイプ「PHPスニペット」
 *   2. 「=== ここから ===」以降を貼り付け
 *   3. 挿入方法「自動挿入 / サイト全体で実行」
 *   4. 有効化して保存 → Autoptimizeのキャッシュを削除
 *
 * 注意: このスニペットは無効にしないでください。無効にすると元の重い画像に戻ります。
 */

// === ここから ===

// <head> の出力を一時的に受け止める。
add_action( 'wp_head', function () {
	if ( is_admin() || is_feed() ) {
		return;
	}
	if ( ob_start() ) {
		$GLOBALS['izk_og_buffering'] = true;
	}
}, -99999 );

// 受け止めた出力の中で、重い画像のURLを軽い画像に置き換えてから出す。
add_action( 'wp_head', function () {

	if ( empty( $GLOBALS['izk_og_buffering'] ) ) {
		return;
	}
	$GLOBALS['izk_og_buffering'] = false;

	$html = ob_get_clean();
	if ( false === $html ) {
		return;
	}

	$uploads = wp_upload_dir();
	$base    = trailingslashit( $uploads['baseurl'] );

	$old_file = '2025/11/Firefly_重機を消して-177871.png';
	$new_file = 'izk-ogimage-1200x630.jpg';

	$new = $base . $new_file;

	// 生のファイル名と、URLエンコードされた形の両方に対応する。
	$search = array(
		$base . $old_file,
		$base . str_replace( '%2F', '/', rawurlencode( $old_file ) ),
	);

	echo str_replace( $search, $new, $html );

}, 99999 );
