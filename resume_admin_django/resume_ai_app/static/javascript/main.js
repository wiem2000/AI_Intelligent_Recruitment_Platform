const user_input = $("#user-input")
const search_icon = $('#search-icon')
const jobs_div = $('#replaceable-content')

const endpoint = ''
const delay_by_in_ms = 100
let scheduled_function = false

let ajax_call = function (endpoint, request_parameters) {
	$.getJSON(endpoint, request_parameters)
		.done(response => {
			// fade out the artists_div, then:
			jobs_div.fadeTo('slow', 0).promise().then(() => {
				// replace the HTML contents
				jobs_div.html(response['html_from_view'])
				console.log(jobs_div)
				// fade-in the div with new contents
				jobs_div.fadeTo('slow', 1)
				// stop animating search icon
				search_icon.removeClass('blink')
			})
		})
}


user_input.on('keyup', function () {

	const request_parameters = {
		q: $(this).val() // value of user_input: the HTML element with ID user-input
	}

	// start animating the search icon with the CSS class
	search_icon.addClass('blink')

	// if scheduled_function is NOT false, cancel the execution of the function
	if (scheduled_function) {
		clearTimeout(scheduled_function)
	}

	// setTimeout returns the ID of the function to be executed
	scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})
