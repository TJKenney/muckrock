
	$(function() {
		$('.datepicker').datepicker({
			changeMonth: true,
			changeYear: true,
			minDate: new Date(1776, 6, 4),
			maxDate: '+1y',
			yearRange: '1776:+1'
		});
	});