
//Script makes navbar transparent when user scrolls down.
  	var main_nav=document.getElementById("main-nav");
  	main_nav.onmouseover=function(){main_nav.style.opacity=1};
  	var prevScrollpos = window.pageYOffset;
  	
window.onscroll = function() {
	
  var currentScrollPos = window.pageYOffset;
  if (prevScrollpos < currentScrollPos) {
   main_nav.style.opacity="0.5";
  }
  prevScrollpos = currentScrollPos;
}


//For marking and counting attendance checkbox
//Next three lines gets needed elements from dom.
var student_checkbox = document.getElementsByClassName("student-checkbox");
var present_no = document.getElementById("presentNo");
var absent_no = document.getElementById("absentNo");
absent_no.innerHTML=student_checkbox.length;

//Getting date for view attendance
document.getElementById("dateView").innerHTML=new Date().toDateString();

//Counting no of students present and absent
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
//Counting students present
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

//Mark all funtion to mark and unmark all.
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
//Toggle between mark attendance and view attendance page.
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

//Showing date.
function viewDay(value){
	document.getElementById("dateView").innerHTML=value;
}




