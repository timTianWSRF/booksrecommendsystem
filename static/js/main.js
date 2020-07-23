// Hide loader when page content has load
$(window).on('load', function() {
	$("#loader").fadeOut("slow");
});

// Toggle cart
$(function () {
	$("#cart").on("click", function() {
		$(".shopping-cart").fadeToggle( "fast");
	});
});

// Carousel recent photos
$(document).ready(function() {
	$("#recent-photos").owlCarousel({
		autoPlay: 3000,
		items : 8,
		itemsDesktop : [1199, 5],
		itemsDesktopSmall : [990, 3],
		itemsTablet : [768, 1]
	});
});

// Carousel recent photos
$(document).ready(function() {
	$("#rs-photos").owlCarousel({
		autoPlay: 3000,
		items : 8,
		itemsDesktop : [1199, 3],
		itemsDesktopSmall : [990, 2],
		itemsTablet : [768, 1]
	});
});

$(document).ready(function() {
	$("#likeUserBooks").owlCarousel({
		autoPlay: 3000,
		items : 8,
		itemsDesktop : [1199, 5],
		itemsDesktopSmall : [990, 3],
		itemsTablet : [768, 1]
	});
});


// Initialize tooltips
$(function () {
	$('[data-toggle="tooltip"]').tooltip()
});