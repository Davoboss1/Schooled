//Scrolls to element with scrolling animation
function animateScrollToId(id) {

	$('html, body').animate({
		scrollTop: ($(id).offset().top - 50)
	}, 1000);
	window.location.href = id;
}

function animateScrollToElem(elem) {
	$('html, body').animate({
		scrollTop: $(elem)[0].offsetTop
	}, 1000);
}

//make navbar transparent when user scrolls down.
var main_nav = document.getElementById("main-nav");
main_nav.onmouseover = function () { main_nav.style.opacity = 1 };
window.onscroll = function () {
	main_nav.style.opacity = "0.5";
}

function write_alert(msg,type){
	if(type===undefined){type="success"}
        if(type=="danger"){
            type_m = "Error";
        }else{
            type_m = type[0].toUpperCase() + type.substr(1);
        }

        return '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert"><strong>' + type_m + '!</strong> ' + msg + '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>';
}

function write_loader(msg){
	if(msg===undefined){msg=""}
    return '<div class="m-auto d-flex flex-column"><div class="mx-auto progressBar"></div><small class="mx-auto">'+msg+'</small></div>';
}
//Help section
var help_requested = false;
function toggleHelp(show) {
	if(show){
		$("#help-container").removeClass("close");
        setTimeout(function(){
		document.getElementById("main-page-body").style.display = "none";
        },500);
		var body = document.getElementById("help-container-body");
		if(!help_requested){
			get_data("/accounts/help_page/",{},body);
            help_requested = true;
		}
	}else{
		$("#help-container").addClass("close");
		document.getElementById("main-page-body").style.display = "block";
	}
}
var list;
$(document).click(function(event) {
	if(!list){return;}
    var $target = $(event.target);
    if(!$target.closest('#helpSideNav').length && $('#helpSideNav').is(":visible") && (event.target !== list[0]) ) {
        document.getElementById("helpSideNav").style.width = "0";
        $("#closeHelp")[0].disabled = false;
    }        
});
	
//End help section
function check_file(input){
	if(input.files[0]){
		return true;
	}else{
		return false;
	}
}

function post_data(url,data,elem,use_server_msg){
	if(use_server_msg===undefined){use_server_msg=false}
	//Add loader
	var elem_obj =$(elem);
	elem_obj.html(write_loader("Submitting..."));
	$.post(url,data).done(function(data){
        if(use_server_msg){
            if(data){
		        $(elem).html(write_alert(data));
                return;
            }
        }
		$(elem).html(write_alert("Data was sent successfully"));

	}).fail(function(res,textStatus,errorThrown){
        if(use_server_msg){
            if(res.responseText){
		        $(elem).html(write_alert(res.responseText,"danger"));
                return;
            }
        }
		$(elem).html(write_alert("Something went wrong, request was not successful.","danger"));
	});
}

function send_request(url,type,data,func){
	$.ajax({
		url: url,
		type: type,
		timeout: 20000,
		data: data,
		success: function(data,textStatus,res){
			func(res,"SUCCESS");
		},
		error: function(res,textStatus,errorThrown){
			func(res,"ERROR");
		},
		complete: function(res,textStatus){
			func(res,"COMPLETE");
		}
	});
}

function post_form(url,form,status_elem,use_server_msg){
	if(use_server_msg===undefined){use_server_msg=false}
	var $form = $(form);
	if(status_elem===undefined){
		$form.find("#form-status").remove();
        status_elem = document.createElement("div");
        status_elem.className = "my-3";
		status_elem.id = "form-status";
		$form.append(status_elem);
	}
	status_elem = $(status_elem);
	status_elem.html(write_loader("Submitting..."));

	$.ajax({
		url: url,
		type: "Post",
		timeout: 15000,
		data: $form.serialize(),
		success: function(data){
			if(use_server_msg){
				if(data){
					status_elem.html(write_alert(data));
					return;
				}
			}
			status_elem.html(write_alert("Form was submitted successfully"));
		},
		error: function(res,textStatus,errorThrown){
			if(use_server_msg){
				if(res.responseText){
					status_elem.html(write_alert(res.responseText,"danger"));
					return;
				}
			}
			status_elem.html(write_alert("Something went wrong, form was not submitted.","danger"));
		}
	});
}

function post_form_file(url,form,status_elem,use_server_msg){
	if(use_server_msg===undefined){use_server_msg=false}
	var $form = $(form);
	if(status_elem===undefined){
		$form.find("#form-status").remove();
        status_elem = document.createElement("div");
        status_elem.className = "my-3";
		status_elem.id = "form-status";
		$form.append(status_elem);
	}
	status_elem = $(status_elem);
	status_elem.html(write_loader("Submitting..."));
	var formdata = new FormData(form);
	$.ajax({
		url: url,
		type: "Post",
		timeout: 20000,
		contentType: false,
		processData: false,
		data: formdata,
		success: function(data){
			if(use_server_msg){
				if(data){
					status_elem.html(write_alert(data));
					return;
				}
			}
			status_elem.html(write_alert("Form was submitted successfully"));
		},
		error: function(res,textStatus,errorThrown){
			if(use_server_msg){
				if(res.responseText){
					status_elem.html(write_alert(res.responseText,"danger"));
					return;
				}
			}
			status_elem.html(write_alert("Something went wrong, form was not submitted.","danger"));
		}
	});
}

function get_data(url,data,elem,status_elem,use_server_msg){
	if(use_server_msg===undefined){use_server_msg=false}
	if(data===undefined){data={}}

	//Add loader
    if(status_elem!==undefined){
	    var status_obj = $(status_elem);
    }else{
	    var status_obj =$(elem);
    }
	status_obj.html(write_loader());
	$.get(url,data).done(function(data){
		status_obj.html("");
        $(elem).html(data);
	}).fail(function(res,textStatus,errorThrown){if(use_server_msg){
		if(res.responseText){
			status_obj.html(write_alert(res.responseText,"danger"));
			return;
			}
		}
		status_obj.html(write_alert("Something went wrong, request was not successful.","danger"));
	});
}
