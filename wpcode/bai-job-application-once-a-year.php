<?php
/**
 * BAI - İş başvurusu: kişi başı yılda bir başvuru
 *
 * WPCode snippet (PHP, "Run Everywhere"). Blocks a second job application from the same
 * person within 365 days, across both application forms:
 *   - 3590  Profesyonel Başvuru — Ekibimize Katıl   (/ekibimize-katil)
 *   - 5609  Teach with us — application (English)    (/en/teach-with-us)
 *
 * The same person = same e-mail (case and spaces ignored) OR same phone (last 10 digits,
 * so +90 532 …, 0532 … and 532 … all match). Entries in the trash or permanently deleted
 * do not count, so deleting an application lets that person apply again.
 *
 * Fails open: if the entries table cannot be read, the application goes through.
 */

defined( 'ABSPATH' ) || exit;

if ( ! defined( 'BAI_JA_FORM_IDS' ) ) {
	define( 'BAI_JA_FORM_IDS', array( 3590, 5609 ) );
	define( 'BAI_JA_EN_FORM_IDS', array( 5609 ) );
	define( 'BAI_JA_WINDOW_DAYS', 365 );
}

if ( ! function_exists( 'bai_ja_norm_email' ) ) {
	function bai_ja_norm_email( $value ) {
		$value = strtolower( trim( (string) $value ) );
		return is_email( $value ) ? $value : '';
	}

	function bai_ja_norm_phone( $value ) {
		$digits = preg_replace( '/\D+/', '', (string) $value );
		return strlen( $digits ) >= 10 ? substr( $digits, -10 ) : '';
	}

	/**
	 * Pull the e-mail and phone out of a submission or a stored entry. Keys are SureForms
	 * field names (srfm-email-eposta-…, srfm-number-telefon-…-phone).
	 */
	function bai_ja_contact( $fields ) {
		$email = '';
		$phone = '';
		foreach ( (array) $fields as $key => $value ) {
			if ( ! is_scalar( $value ) ) {
				continue;
			}
			$key = strtolower( (string) $key );
			if ( '' === $email && false !== strpos( $key, 'email' ) && false === strpos( $key, 'confirm' ) && false === strpos( $key, 'sender' ) ) {
				$email = bai_ja_norm_email( $value );
			} elseif ( '' === $phone && ( false !== strpos( $key, 'telefon' ) || false !== strpos( $key, 'phone' ) ) ) {
				$phone = bai_ja_norm_phone( $value );
			}
		}
		return array( $email, $phone );
	}

	function bai_ja_is_same_person( $a, $b ) {
		return ( '' !== $a[0] && $a[0] === $b[0] ) || ( '' !== $a[1] && $a[1] === $b[1] );
	}

	/** True when an earlier application in the window matches, false otherwise or on error. */
	function bai_ja_has_recent_application( $contact ) {
		global $wpdb;
		$table = $wpdb->prefix . 'srfm_entries';
		if ( $wpdb->get_var( $wpdb->prepare( 'SHOW TABLES LIKE %s', $table ) ) !== $table ) {
			return false;
		}
		$ids   = implode( ',', array_map( 'absint', BAI_JA_FORM_IDS ) );
		$since = gmdate( 'Y-m-d H:i:s', strtotime( current_time( 'mysql' ) . ' -' . BAI_JA_WINDOW_DAYS . ' days' ) );
		// phpcs:ignore WordPress.DB.PreparedSQL.InterpolatedNotPrepared -- $table and $ids are built above from constants.
		$rows = $wpdb->get_col( $wpdb->prepare( "SELECT form_data FROM {$table} WHERE form_id IN ({$ids}) AND status <> 'trash' AND created_at >= %s", $since ) );
		if ( $wpdb->last_error ) {
			error_log( 'bai-job-application: entries lookup failed: ' . $wpdb->last_error );
			return false;
		}
		foreach ( (array) $rows as $raw ) {
			$data = json_decode( (string) $raw, true );
			if ( ! is_array( $data ) ) {
				$data = maybe_unserialize( $raw );
			}
			if ( is_array( $data ) && bai_ja_is_same_person( $contact, bai_ja_contact( $data ) ) ) {
				return true;
			}
		}
		return false;
	}
}

add_filter(
	'rest_pre_dispatch',
	function ( $result, $server, $request ) {
		if ( null !== $result || '/sureforms/v1/submit-form' !== $request->get_route() ) {
			return $result;
		}
		$form_id = absint( $request->get_param( 'form-id' ) );
		if ( ! in_array( $form_id, BAI_JA_FORM_IDS, true ) ) {
			return $result;
		}
		$contact = bai_ja_contact( $request->get_params() );
		if ( ( '' === $contact[0] && '' === $contact[1] ) || ! bai_ja_has_recent_application( $contact ) ) {
			return $result;
		}

		$message = in_array( $form_id, BAI_JA_EN_FORM_IDS, true )
			? 'We have already received an application with this e-mail address or phone number in the last 12 months. If you would like to update your application, please write to us through our <a href="' . esc_url( home_url( '/en/contact/' ) ) . '">contact page</a>.'
			: 'Bu e-posta adresi veya telefon numarasıyla son 12 ay içinde bir başvuru aldık. Başvurunuzu güncellemek isterseniz bize <a href="' . esc_url( home_url( '/iletisim/' ) ) . '">İletişim sayfasından</a> yazabilirsiniz.';

		return new WP_REST_Response(
			array(
				'success' => false,
				'data'    => array( 'message' => $message ),
			),
			409
		);
	},
	10,
	3
);
