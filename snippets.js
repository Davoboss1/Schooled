function write_alert(msg,type="success"){
	type = type[0].toUpperCase() + type.substr(1);
	if(type=="Danger"){
		type_m = "Error";
	}else{
		type_m = type;
	}

	return '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert"><strong>' + type_m + '!</strong>' + msg + '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>';
}

function(){}
$().event(function(e){});
$.ajax({
	url: "",
	type: "Get/Post",
	timeout: 0,
	data: {},
	success: function(data){},
	error: function(res,textStatus,errorThrown){}
});

$.post("",{}).done(function(data){}).fail(function(res,textStatus,errorThrown){});
$.get("",{}).done(function(data){}).fail(function(res,textStatus,errorThrown){});

