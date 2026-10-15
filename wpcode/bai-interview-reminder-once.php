/**
 * BAI - Görüşme hatırlatması: kişi başına bir kez (stopgap)
 *
 * The bai-booking plugin (v0.8.0) sends the interview reminder on every run of its hourly
 * job once the interview is less than 24 hours away, and never records that it was sent.
 * Mahdiyeh's 15 Oct 22:00 interview produced 6 reminders each for her and for the owner on live.
 *
 * This snippet lets each interview reminder through once per recipient per interview
 * (same recipient + same subject, which includes the interview date and time) and blocks
 * the repeats. A rescheduled interview has a new time in its subject, so it gets its own
 * single reminder. Nothing else is touched.
 *
 * Remove it once the booking plugin itself sends one reminder (1 hour before).
 *
 * Install: Code Snippets → + Add Snippet → Add Your Custom Code → PHP Snippet,
 * paste this whole file, Insert Method: Auto Insert, Location: Run Everywhere, activate.
 */

if ( ! function_exists( 'bai_iv_reminder_is_repeat' ) ) {
	/**
	 * True when this reminder already went to this recipient. Records the first send.
	 *
	 * @param string $to      Recipient list, comma separated.
	 * @param string $subject Mail subject.
	 * @return bool
	 */
	function bai_iv_reminder_is_repeat( $to, $subject ) {
		$is_reminder = ( 0 === stripos( $subject, 'Reminder: your interview' ) )
			|| ( 0 === strpos( $subject, 'Yarın görüşme:' ) )
			|| ( 0 === strpos( $subject, 'Hatırlatma: görüşme' ) );
		if ( ! $is_reminder ) {
			return false;
		}
		$key = 'bai_iv_rem_' . md5( strtolower( trim( $to ) ) . '|' . $subject );
		if ( get_transient( $key ) ) {
			return true;
		}
		set_transient( $key, time(), 3 * DAY_IN_SECONDS );
		return false;
	}
}

add_filter(
	'wp_mail',
	function ( $atts ) {
		$to = is_array( $atts['to'] ) ? implode( ',', $atts['to'] ) : (string) $atts['to'];
		if ( bai_iv_reminder_is_repeat( $to, (string) $atts['subject'] ) ) {
			$atts['to']           = array();
			$atts['bai_iv_block'] = 1;
		}
		return $atts;
	},
	1
);

add_filter(
	'pre_wp_mail',
	function ( $return, $atts ) {
		if ( ! empty( $atts['bai_iv_block'] ) ) {
			return false;
		}
		return $return;
	},
	0,
	2
);
