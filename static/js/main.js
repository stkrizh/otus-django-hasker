function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


$(document).ready(function() {
    $(".votes__vote").click(function() {
        var container = $(this).parents(".votes"),
            target_id = $(this).parents(".votes").data("target"),
            url = $(this).parents(".votes").data("url"),
            value = $(this).data("value");

        if (container.data("loading")) {
            return
        }

        container.data("loading", 1);

        $.ajax({
            type: "POST",
            url: url,
            data: {
                target_id: target_id, 
                value: value
            },
            dataType: "json",
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                container.find(".votes__vote").addClass("votes__vote--inactive");
                container.find(".votes__value span").addClass("hidden");
                container.find(".loader").removeClass("hidden");
            },
            success: function(data, status, xhr) {
                container.find(".votes__value span").html(data["rating"]);
            },
            error: function(xhr, status) {
                if (status == "error" && xhr["status"] == 403) {
                    UIkit.modal($("#modal-center")).show();
                } else {
                    $("#modal-center p").html("Sorry, something went wrong!");
                    UIkit.modal($("#modal-center")).show();
                }
            },
            complete: function(xhr, status) {
                container.find(".votes__vote").removeClass("votes__vote--inactive");
                container.find(".votes__value span").removeClass("hidden");
                container.find(".loader").addClass("hidden");
                container.data("loading", 0);
            }
        });
    })
})
