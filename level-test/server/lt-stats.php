/**
 * BAI - Seviye testi: anonim yanıt istatistiği
 *
 * WPCode snippet (PHP, "Run Everywhere"), installed in snippet 4012 on staging and live.
 * Source of truth: level-test/server/lt-stats.php in the LearnEnglish repository.
 *
 * Stores one record per finished 40-question test, so the questions and the cut points can be checked
 * against real data (level-test/PLAN.md, section 1, steps 2 and 3). Stored: date, the answer code
 * ("1" + yyyymmdd + one character per question), test duration in seconds and whether the test was
 * finished early. NOT stored: name, e-mail, phone, IP address or account. Records cannot be linked to
 * a person, so they are anonymous data.
 *
 *   POST /wp-json/bai/v1/lt-stat     public; body {code, d, e}; rate limited
 *   GET  /wp-json/bai/v1/lt-stats    administrators only; all records as JSON
 *
 * Written without angle brackets, ampersands or backslashes on purpose: the tool that installs it over
 * the API runs the code through the HTML filter, which would strip or escape them. So: comparisons with
 * min(), call_user_func() instead of the object arrow, array keys set one by one.
 */

defined( 'ABSPATH' ) || exit;

if ( ! function_exists( 'bai_lts_register_type' ) ) {

	define( 'BAI_LTS_TYPE', 'bai_lt_stat' );
	define( 'BAI_LTS_PER_HOUR', 20 );
	define( 'BAI_LTS_PER_DAY', 2000 );

	function bai_lts_register_type() {
		$args                 = array();
		$args['label']        = 'Seviye testi istatistikleri';
		$args['public']       = false;
		$args['show_ui']      = false;
		$args['show_in_rest'] = false;
		$args['rewrite']      = false;
		$args['query_var']    = false;
		$args['supports']     = array( 'title' );
		register_post_type( BAI_LTS_TYPE, $args );
	}
	add_action( 'init', 'bai_lts_register_type' );

	function bai_lts_routes() {
		$save                        = array();
		$save['methods']             = 'POST';
		$save['callback']            = 'bai_lts_save';
		$save['permission_callback'] = '__return_true';
		register_rest_route( 'bai/v1', '/lt-stat', $save );

		$export                        = array();
		$export['methods']             = 'GET';
		$export['callback']            = 'bai_lts_export';
		$export['permission_callback'] = 'bai_lts_can_export';
		register_rest_route( 'bai/v1', '/lt-stats', $export );
	}
	add_action( 'rest_api_init', 'bai_lts_routes' );

	function bai_lts_can_export() {
		return current_user_can( 'manage_options' );
	}

	function bai_lts_param( $req, $key ) {
		return call_user_func( array( $req, 'get_param' ), $key );
	}

	function bai_lts_reply( $ok, $status ) {
		$body       = array();
		$body['ok'] = $ok;
		return new WP_REST_Response( $body, $status );
	}

	/* A short-lived counter key per visitor. The address is only hashed into a transient name that
	   expires after an hour; it is never stored with the record. */
	function bai_lts_visitor_key() {
		$parts = '';
		foreach ( array( 'REMOTE_ADDR', 'HTTP_X_FORWARDED_FOR' ) as $h ) {
			if ( isset( $_SERVER[ $h ] ) ) {
				$parts .= '|' . sanitize_text_field( wp_unslash( $_SERVER[ $h ] ) );
			}
		}
		return 'bai_lts_v_' . md5( $parts . wp_salt( 'nonce' ) );
	}

	function bai_lts_save( $req ) {
		$code = (string) bai_lts_param( $req, 'code' );
		if ( 1 !== preg_match( '/^1[0-9]{8}[0-4x]{40}$/D', $code ) ) {
			return bai_lts_reply( false, 400 );
		}

		$day_key = 'bai_lts_day_' . gmdate( 'Ymd' );
		$day     = (int) get_transient( $day_key );
		if ( BAI_LTS_PER_DAY === min( $day, BAI_LTS_PER_DAY ) ) {
			return bai_lts_reply( false, 429 );
		}
		$key   = bai_lts_visitor_key();
		$count = (int) get_transient( $key );
		if ( BAI_LTS_PER_HOUR === min( $count, BAI_LTS_PER_HOUR ) ) {
			return bai_lts_reply( false, 429 );
		}
		set_transient( $key, $count + 1, HOUR_IN_SECONDS );
		set_transient( $day_key, $day + 1, DAY_IN_SECONDS );

		$post                 = array();
		$post['post_type']    = BAI_LTS_TYPE;
		$post['post_status']  = 'private';
		$post['post_title']   = gmdate( 'Y-m-d H:i' );
		$post['post_content'] = $code;
		$id                   = wp_insert_post( $post, true );
		if ( is_wp_error( $id ) ) {
			return bai_lts_reply( false, 500 );
		}
		update_post_meta( $id, '_bai_lts_d', min( absint( bai_lts_param( $req, 'd' ) ), 86400 ) );
		update_post_meta( $id, '_bai_lts_e', bai_lts_param( $req, 'e' ) ? 1 : 0 );
		return bai_lts_reply( true, 200 );
	}

	function bai_lts_export( $req ) {
		$q                = array();
		$q['post_type']   = BAI_LTS_TYPE;
		$q['post_status'] = 'private';
		$q['numberposts'] = -1;
		$q['fields']      = 'ids';
		$q['orderby']     = 'ID';
		$q['order']       = 'ASC';
		$rows             = array();
		foreach ( get_posts( $q ) as $id ) {
			$row         = array();
			$row['at']   = get_post_field( 'post_date', $id );
			$row['code'] = get_post_field( 'post_content', $id );
			$row['d']    = (int) get_post_meta( $id, '_bai_lts_d', true );
			$row['e']    = (int) get_post_meta( $id, '_bai_lts_e', true );
			$rows[]      = $row;
		}
		return new WP_REST_Response( $rows, 200 );
	}
}
