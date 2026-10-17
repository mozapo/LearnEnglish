// ---------------------------------------------------------------- storage

add_action( 'init', 'bai_lt_register_cpt' );
function bai_lt_register_cpt() {
	register_post_type(
	'bai_lvl_result',
	array(
	'labels'          => array(
	'name'          => "Seviye Testi Sonu\u{E7}lar\u{131}",
	'singular_name' => 'Seviye Testi Sonucu',
	'menu_name'     => 'Seviye Testi',
	),
	'public'          => false,
	'show_ui'         => true,
	'show_in_menu'    => true,
	'menu_icon'       => 'dashicons-welcome-learn-more',
	'menu_position'   => 26,
	'supports'        => array( 'title', 'custom-fields' ),
	'capability_type' => 'post',
	'capabilities'    => array( 'create_posts' => 'do_not_allow' ),
	'map_meta_cap'    => true,
	'show_in_rest'    => false,
	)
	);
}

// ------------------------------------------------------------- admin list

add_filter( 'manage_bai_lvl_result_posts_columns', 'bai_lt_columns' );
function bai_lt_columns( $cols ) {
	return array(
	'cb'        => isset( $cols['cb'] ) ? $cols['cb'] : '',
	'title'     => 'Aday',
	'bai_level' => 'Seviye',
	'bai_score' => 'Puan',
	'bai_conf'  => "G\u{FC}ven",
	'bai_mail'  => 'E-posta',
	'bai_phone' => 'Telefon',
	'date'      => 'Tarih',
	);
}

add_action( 'manage_bai_lvl_result_posts_custom_column', 'bai_lt_column_value', 10, 2 );
function bai_lt_column_value( $col, $post_id ) {
	$map = array(
	'bai_level' => '_bai_level',
	'bai_score' => '_bai_score',
	'bai_conf'  => '_bai_confidence',
	'bai_mail'  => '_bai_email',
	'bai_phone' => '_bai_phone',
	);
	if ( isset( $map[ $col ] ) ) {
		echo esc_html( (string) get_post_meta( $post_id, $map[ $col ], true ) );
	}
}

function bai_lt_feedback( $level ) {
	$f = array(
	'A1' => "Temel kelime da\u{11F}arc\u{131}\u{11F}\u{131}, geni\u{15F} zaman ve ge\u{E7}mi\u{15F} zaman kal\u{131}plar\u{131} ile k\u{131}sa g\u{FC}nl\u{FC}k diyaloglara odaklan.",
	'A2' => "Ge\u{E7}mi\u{15F} ve gelecek zaman yap\u{131}lar\u{131}, g\u{FC}nl\u{FC}k kelime da\u{11F}arc\u{131}\u{11F}\u{131} ve daha uzun diyaloglarla \u{F6}zg\u{FC}ven kazan.",
	'B1' => "Do\u{11F}ruluk, ak\u{131}c\u{131}l\u{131}k ve g\u{F6}r\u{FC}\u{15F}lerini gerek\u{E7}eleriyle daha ayr\u{131}nt\u{131}l\u{131} ifade etme \u{FC}zerinde \u{E7}al\u{131}\u{15F}.",
	'B2' => "Kesinlik, e\u{15F} dizimler ve do\u{11F}al, uzun konu\u{15F}ma-yazma prati\u{11F}ine odaklan.",
	'C1' => "N\u{FC}ans, \u{FC}slup, deyimsel dil ve karma\u{15F}\u{131}k ileti\u{15F}imde kesinlik geli\u{15F}tirmeye devam et.",
	'C2' => "\u{DC}slup inceli\u{11F}i, ince ayr\u{131}mlar ve retorik kontrol ile ana dili seviyesine yakla\u{15F}.",
	);
	return isset( $f[ $level ] ) ? $f[ $level ] : '';
}

// --------------------------------------------------------------- handler

function bai_lt_handle( WP_REST_Request $req ) {
	
	$key   = 'bai_lt_' . bai_lt_client_ip();
	$count = (int) get_transient( $key );
	if ( $count >= 5 ) {
		return new WP_REST_Response( array( 'ok' => false, 'error' => 'rate_limited' ), 429 );
	}
	
	$student = $req->get_param( 'student' );
	$result  = $req->get_param( 'result' );
	$answers = $req->get_param( 'answers' );
	
	if ( ! is_array( $student ) || ! is_array( $result ) ) {
		return new WP_REST_Response( array( 'ok' => false, 'error' => 'bad_payload' ), 400 );
	}
	
	$trap = $req->get_param( 'website' );
	if ( ! empty( $trap ) ) {
		return new WP_REST_Response( array( 'ok' => true ), 200 );
	}
	
	$name  = sanitize_text_field( substr( (string) ( isset( $student['name'] ) ? $student['name'] : '' ), 0, 80 ) );
	$email = sanitize_email( substr( (string) ( isset( $student['email'] ) ? $student['email'] : '' ), 0, 120 ) );
	$phone = sanitize_text_field( substr( (string) ( isset( $student['phone'] ) ? $student['phone'] : '' ), 0, 40 ) );
	$level = strtoupper( sanitize_text_field( substr( (string) ( isset( $result['placed'] ) ? $result['placed'] : '' ), 0, 2 ) ) );
	
	$allowed = array( 'A1', 'A2', 'B1', 'B2', 'C1', 'C2' );
	if ( '' === $name || ! is_email( $email ) || ! in_array( $level, $allowed, true ) ) {
		return new WP_REST_Response( array( 'ok' => false, 'error' => 'invalid' ), 400 );
	}
	
	$score    = max( 0, min( 40, (int) ( isset( $result['correct'] ) ? $result['correct'] : 0 ) ) );
	$accuracy = max( 0, min( 100, (int) ( isset( $result['accuracy'] ) ? $result['accuracy'] : 0 ) ) );
	$unknown  = max( 0, min( 40, (int) ( isset( $result['unknown'] ) ? $result['unknown'] : 0 ) ) );
	$duration = max( 1, min( 7200, (int) ( isset( $result['durationSeconds'] ) ? $result['durationSeconds'] : 1 ) ) );
	$conf_in  = isset( $result['confidence'] ) ? (string) $result['confidence'] : '';
	$conf     = in_array( $conf_in, array( 'High', 'Medium', 'Low' ), true ) ? $conf_in : 'Low';
	$by_level = isset( $result['byLevel'] ) ? $result['byLevel'] : array();
	
	$post_id = wp_insert_post(
	array(
	'post_type'   => 'bai_lvl_result',
	'post_status' => 'publish',
	'post_title'  => $name . ' - ' . $level . ' (' . $score . '/40)',
		),
		true
		);
	
	if ( is_wp_error( $post_id ) ) {
		return new WP_REST_Response( array( 'ok' => false, 'error' => 'store_failed' ), 500 );
	}
	
	$meta = array(
	'_bai_name'       => $name,
	'_bai_email'      => $email,
	'_bai_phone'      => $phone,
	'_bai_level'      => $level,
	'_bai_score'      => $score,
	'_bai_accuracy'   => $accuracy,
	'_bai_confidence' => $conf,
	'_bai_unknown'    => $unknown,
	'_bai_duration'   => $duration,
	'_bai_by_level'   => wp_json_encode( $by_level ),
	'_bai_answers'    => wp_json_encode( is_array( $answers ) ? array_slice( $answers, 0, 40 ) : array() ),
	);
	foreach ( $meta as $k => $v ) {
		update_post_meta( $post_id, $k, $v );
	}
	
	set_transient( $key, $count + 1, HOUR_IN_SECONDS );
	
	if ( function_exists( 'FluentCrmApi' ) ) {
		try {
			$parts = explode( ' ', $name, 2 );
			FluentCrmApi( 'contacts' )->createOrUpdate(
			array(
			'first_name' => $parts[0],
			'last_name'  => isset( $parts[1] ) ? $parts[1] : '',
			'email'      => $email,
			'phone'      => $phone,
			'status'     => 'subscribed',
			'source'     => 'Seviye Testi',
			)
			);
		} catch ( Exception $e ) {
			unset( $e );
		}
	}
	
	$rows = '';
	foreach ( $allowed as $l ) {
		$x = isset( $by_level[ $l ] ) ? $by_level[ $l ] : array();
		$c = isset( $x['correct'] ) ? (int) $x['correct'] : 0;
		$t = isset( $x['total'] ) ? (int) $x['total'] : 0;
		$u = isset( $x['unknown'] ) ? (int) $x['unknown'] : 0;
		$rows .= '<tr><td style="padding:8px 12px">' . esc_html( $l ) . '</td><td style="padding:8px 12px">' . $c . '/' . $t . '</td><td style="padding:8px 12px">' . $u . '</td></tr>';
	}
	
	$headers = array( 'Content-Type: text/html; charset=UTF-8' );
	$book    = esc_url( home_url( '/randevu-olustur/' ) );
	$lname   = bai_lt_level_name( $level );
	
	$student_html = '<div style="font-family:Helvetica,Arial,sans-serif;max-width:640px;margin:auto;background:#16233F;color:#E8EDF7;padding:32px;border-radius:16px">'
		. "<p style='letter-spacing:.14em;text-transform:uppercase;font-size:12px;color:#B98A2E;margin:0 0 10px'>Bir Ad\u{131}m \u{130}leri</p>"
		. '<h2 style="margin:0 0 14px;font-size:24px">Tebrikler ' . esc_html( $name ) . '!</h2>'
		. '<div style="text-align:center;border:1px solid rgba(185,138,46,.4);border-radius:14px;padding:24px;background:rgba(185,138,46,.08)">'
		. '<div style="font-size:54px;font-weight:800;color:#B98A2E;line-height:1">' . esc_html( $level ) . '</div>'
		. '<div style="font-size:18px;margin-top:6px">' . esc_html( $lname ) . '</div></div>'
		. "<p style='margin:22px 0 6px'><strong>Puan:</strong> " . $score . "/40 &#183; <strong>Do\u{11F}ruluk:</strong> " . $accuracy . '%</p>'
		. "<p style='margin:0 0 22px'><strong>Sonraki ad\u{131}m\u{131}n:</strong> " . esc_html( bai_lt_feedback( $level ) ) . '</p>'
		. '<table style="border-collapse:collapse;width:100%;color:#E8EDF7;font-size:14px">' . $rows . '</table>'
		. "<p style='margin:26px 0 0'><a href='" . $book . "' style='display:inline-block;background:#B98A2E;color:#1A1206;text-decoration:none;font-weight:700;padding:14px 26px;border-radius:12px'>\u{DC}cretsiz \u{F6}n g\u{F6}r\u{FC}\u{15F}me ayarla</a></p>"
		. "<p style='font-size:12px;color:#7C8CA8;margin-top:26px'>Bu sonu\u{E7} bir seviye tahminidir; resm\u{EE} bir Cambridge English s\u{131}nav\u{131} ya da sertifikas\u{131} de\u{11F}ildir.</p></div>";
	
	$admin_html = '<div style="font-family:Helvetica,Arial,sans-serif;max-width:700px;margin:auto;color:#172033">'
		. '<h2>Yeni seviye testi tamamlandi</h2>'
		. '<p><strong>Aday:</strong> ' . esc_html( $name ) . '</p>'
		. '<p><strong>E-posta:</strong> ' . esc_html( $email ) . '</p>'
		. '<p><strong>Telefon:</strong> ' . esc_html( $phone ? $phone : '-' ) . '</p>'
		. '<p><strong>Sonuc:</strong> ' . esc_html( $level ) . ' - ' . esc_html( $lname ) . '</p>'
		. '<p><strong>Puan:</strong> ' . $score . '/40 (' . $accuracy . '%)</p>'
		. "<p><strong>G\u{FC}ven:</strong> " . esc_html( $conf ) . ' &#183; <strong>Bilmiyorum:</strong> ' . $unknown . '</p>'
		. "<p><strong>S\u{FC}re:</strong> " . (int) floor( $duration / 60 ) . 'dk ' . ( $duration % 60 ) . 'sn</p>'
		. '<table style="border-collapse:collapse;font-size:14px">' . $rows . '</table>'
		. '<p><a href="' . esc_url( admin_url( 'edit.php?post_type=bai_lvl_result' ) ) . '">Tum sonuclari gor</a></p></div>';
	
	$sent_student = wp_mail( $email, "\u{130}ngilizce seviyen: " . $level . ' - ' . $lname, $student_html, $headers );
	$sent_admin   = wp_mail( bai_lt_admin_email(), 'Yeni seviye testi: ' . $name . ' - ' . $level, $admin_html, array_merge( $headers, array( 'Reply-To: ' . $name . ' <' . $email . '>' ) ) );
	
	update_post_meta( $post_id, '_bai_mail_student', $sent_student ? 'sent' : 'failed' );
	update_post_meta( $post_id, '_bai_mail_admin', $sent_admin ? 'sent' : 'failed' );
	
	return new WP_REST_Response( array( 'ok' => true, 'mailStudent' => (bool) $sent_student, 'mailAdmin' => (bool) $sent_admin ), 200 );
}
