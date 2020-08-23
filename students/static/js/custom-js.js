var student_checkbox = document.getElementsByClassName("student-checkbox");
var present_no = document.getElementById("presentNo");
var absent_no = document.getElementById("absentNo");
absent_no.innerHTML=student_checkbox.length;

document.getElementById("dateView").innerHTML=new Date().toDateString();

for(var i = 0;i<student_checkbox.length;i++)
{
 student_checkbox[i].onclick= function(){
 	var present_count = parseInt(present_no.innerHTML);
	var absent_count = parseInt(absent_no.innerHTML);
	if(this.checked===true){
		present_count+=1;
		absent_count-=1;
	}else{
		present_count-=1;
		absent_count+=1;
	}
	
	present_no.innerHTML=present_count;
	absent_no.innerHTML=absent_count;
 };
 
}

function countPresent(){
	var count = 0;
	for(var i =0;i<student_checkbox.length;i++){
		if(student_checkbox[i].checked===true){
			count++;
		}
	}
	
	present_no.innerHTML=count;
	absent_no.innerHTML=student_checkbox.length-count;
}

function markAll(mark){
for(var i = 0;i<student_checkbox.length;i++){
	if(mark){
	student_checkbox[i].checked=true;
	}else{
		student_checkbox[i].checked=false;
	}
}
if(mark){	present_no.innerHTML=student_checkbox.length;
	absent_no.innerHTML=0;
	}else{	absent_no.innerHTML=student_checkbox.length;
	  present_no.innerHTML=0;
	}
}

var showing = "attendance_mark";
function switchAttendance(){
	var attendance_mark = document.getElementById('attendance-mark');
	var attendance_view = document.getElementById("attendance-view");
  if(showing==="attendance_mark"){
  showing="attendance_view";
  attendance_view.style.display="block";
  attendance_mark.style.display="none";
  }else if(showing==="attendance_view"){
  showing="attendance_mark";
  attendance_mark.style.display="block";
  attendance_view.style.display="none";
  }
 
}

function viewDay(value){
	document.getElementById("dateView").innerHTML=value;
}