<?php
/**
 * 石名坂：チャットボットの窓口だけを開ける
 *
 * このサイトでは、ログインしていない訪問者に対して REST API 全体が
 * 閉じられています（お問い合わせフォームだけ例外）。そのため
 * チャットボットが会話を始められず、訪問者には動きません。
 *
 * このコードは、AI Engine が使う 2 つの窓口だけを開けます。
 * それ以外は今までどおり閉じたままです。元のブロックには手を触れません。
 *
 * WPCode に「PHPスニペット」として貼り、「どこでも実行」で有効化してください。
 */

if ( ! function_exists( 'izk_is_chatbot_rest_route' ) ) {

	/** 開ける窓口かどうかを判定する */
	function izk_is_chatbot_rest_route( $route ) {
		$route = '/' . ltrim( (string) $route, '/' );
		return ( 0 === strpos( $route, '/mwai/' ) || 0 === strpos( $route, '/mwai-ui/' ) );
	}

	/** いま呼ばれている窓口の名前を取り出す */
	function izk_current_rest_route() {
		if ( isset( $GLOBALS['wp']->query_vars['rest_route'] ) ) {
			return (string) $GLOBALS['wp']->query_vars['rest_route'];
		}
		return '';
	}

	/**
	 * 1. 「ログインしていないから駄目」で止める処理を、
	 *    チャットボットの窓口についてだけ取り消す。
	 *    優先順位を最大にして、必ずブロックより後に動くようにする。
	 */
	add_filter(
		'rest_authentication_errors',
		function ( $result ) {
			if ( ! is_wp_error( $result ) ) {
				return $result;
			}
			if ( izk_is_chatbot_rest_route( izk_current_rest_route() ) ) {
				return null;
			}
			return $result;
		},
		PHP_INT_MAX
	);

	/**
	 * 2. ブロックが別の段階で行われている場合にも同じ扱いをする。
	 *    どちらの作りでも効くようにするための保険。
	 */
	add_filter(
		'rest_pre_dispatch',
		function ( $result, $server, $request ) {
			if ( ! is_wp_error( $result ) ) {
				return $result;
			}
			if ( $request instanceof WP_REST_Request
				&& izk_is_chatbot_rest_route( $request->get_route() ) ) {
				return null;
			}
			return $result;
		},
		PHP_INT_MAX,
		3
	);
}
