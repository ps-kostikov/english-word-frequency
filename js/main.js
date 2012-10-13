$(document).ready(function() {
	$("#input").autocomplete({
		source: function(request, response) {
			$.ajax({
				url: "suggest?begin=" + request.term,
				dataType: "json",
				success: function(data) {
							response($.map(data, function(item) {
							return {
								label: item,
								id: item,
								abbrev: item
								};
						}));
					}
				});
			},
			minLength: 1
	});

	function reload_input() {
		$("#input").val('');
		$("#input").autocomplete("close");
		$("#input").focus();
	}

	$("#input").keyup(function(e) {
		text = $("#input").val().toLowerCase();
		$("#input").val(text);
		if(e.which === 13) {
    		$("#search").click();
		}
	});

	$("#search").click(function() {
		var word = $("#input").val();
		if (word == "") {
			word = "1";
		}
		$.ajax({url:"interval?word=" + word, 
			statusCode: {404: function() {
				$("#word").html(word);
				$("#not_found_error").show();
				reload_input();
			}}, 
			success:function(result) {
				words = eval(result);
				html = ""
				for (i=0; i<words.length; i++) {
					var current_word = words[i][0];
					var current_order = words[i][1];
					content = current_order + ". "  + current_word;
					if (current_word == word || current_order == word) {
						content = "<b>" + content + "</b>";
					}
					html += "<tr><td>" + content + "</td></tr>";
				}
				$("#not_found_error").hide();
				$("#result").html(html);
				reload_input();
			}});
	});

	$("#search").click();
});
