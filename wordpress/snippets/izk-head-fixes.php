<?php
/**
 * WPCode 貼り付け用（常時有効にしておくスニペット）
 *
 * いま動いている「og画像 差し替え」の置き換え版です。
 * 次の2つを、テーマのファイルを触らずに直します。
 *
 *   1. og:image を軽量化した画像に差し替える
 *   2. Googleフォントの読み込みを、実際に使っている書体だけに絞る
 *
 * Autoptimize の設定は変更しません。「結合とヘッダーで遅延リンク」のままで動きます。
 *
 * 使い方:
 *   既存の「og画像 差し替え」スニペットのコード欄を全部消して、
 *   「=== ここから ===」以降を貼り直し、保存するだけです。
 *   （新しく作って二重に動かさないでください）
 *
 * 注意: このスニペットは無効にしないでください。
 */

// === ここから ===

// <head> の出力を一時的に受け止める。
add_action( 'wp_head', function () {
	if ( is_admin() || is_feed() ) {
		return;
	}
	if ( ob_start() ) {
		$GLOBALS['izk_head_buffering'] = true;
	}
}, -99999 );

// 受け止めた出力を書き換えてから出す。
add_action( 'wp_head', function () {

	if ( empty( $GLOBALS['izk_head_buffering'] ) ) {
		return;
	}
	$GLOBALS['izk_head_buffering'] = false;

	$html = ob_get_clean();
	if ( false === $html ) {
		return;
	}

	// --- 1. og:image を軽い画像に差し替える -------------------------------
	$uploads = wp_upload_dir();
	$base    = trailingslashit( $uploads['baseurl'] );

	$old_image = '2025/11/Firefly_重機を消して-177871.png';
	$new_image = $base . 'izk-ogimage-1200x630.jpg';

	$html = str_replace(
		array(
			$base . $old_image,
			$base . str_replace( '%2F', '/', rawurlencode( $old_image ) ),
		),
		$new_image,
		$html
	);

	echo $html;

}, 99999 );

/**
 * Googleフォントを、実際に使っている書体だけに絞る。
 *
 * このサイトのフォント読み込みタグは Autoptimize が組み立てているため、
 * 上の <head> 書き換えでは間に合わない。Autoptimize が用意している
 * 専用の差し込み口を使う。
 *
 * 現状は3書体を要求しているが、CSSで使われているのは Zen Maru Gothic のみ。
 * 300 と 500 のウェイトもサイト内で未使用のため外している。
 * display:swap は Autoptimize が自動で付けるので、ここには書かない。
 */
add_filter( 'autoptimize_filter_extra_gfont_fontstring', function ( $fontstring ) {
	return 'Zen+Maru+Gothic:400,700,900';
} );
