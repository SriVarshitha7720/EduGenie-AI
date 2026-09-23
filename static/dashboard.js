let stats = JSON.parse(localStorage.getItem("stats")) || {

    questions:0,

    quizzes:0,

    summaries:0,

    roadmaps:0,

    history:[]
};

document.getElementById("questionsCount").innerHTML = stats.questions;

document.getElementById("quizCount").innerHTML = stats.quizzes;

document.getElementById("summaryCount").innerHTML = stats.summaries;

document.getElementById("roadmapCount").innerHTML = stats.roadmaps;

const activity=document.getElementById("activityList");

activity.innerHTML="";

stats.history.slice().reverse().forEach(item=>{

    activity.innerHTML += `<li>${item}</li>`;

});