var tutorial1 = document.getElementById('tutorial-1');
var tutorial2 = document.getElementById('tutorial-2');
var tutorial3 = document.getElementById('tutorial-3');
var tutorial4 = document.getElementById('tutorial-4');
var tutorial5 = document.getElementById('tutorial-5');
var tutorial6 = document.getElementById('tutorial-6');
var tutorial7 = document.getElementById('tutorial-7');
var tutorial8 = document.getElementById('tutorial-8');
var header = document.getElementById('header-id');
var locationDropdown = document.getElementById('location-dropdown-id');
var dashboardConfig = document.getElementById('dashboard-configuration-id');
var locationGraph = document.getElementById('location-graph-id');
var categoryGraph = document.getElementById('category-graph-id');
var map = document.getElementById('map-id');
var mist = document.getElementById('mist-id');

mist.className = 'clouded'

function toTutorial1() {
	tutorial2.className = 'hidden';
	tutorial1.className = 'visible';
	header.className = 'behind'
}
// var tutorial1 = document.getElementByClassName('tutorial-1')
function toTutorial2() {
	tutorial3.className = 'hidden'
	tutorial2.className = 'visible';
	tutorial1.className = 'hidden';
	header.className = 'front';
	locationDropdown.className = 'behind';
}

function toTutorial3() {
	tutorial4.className = 'hidden';
	tutorial3.className = 'visible';
	tutorial2.className = 'hidden';
	header.className = 'behind';
	locationDropdown.className = 'front';
	dashboardConfig.className = 'behind';
}

function toTutorial4() {
	tutorial5.className = 'hidden';
	tutorial4.className = 'visible';
	tutorial3.className = 'hidden';
	locationDropdown.className = 'behind';
	dashboardConfig.className = 'front';
	locationGraph.className = 'behind';
}

function toTutorial5() {
	tutorial6.className = 'hidden';
	tutorial5.className = 'visible';
	tutorial4.className = 'hidden';
	dashboardConfig.className = 'behind';
	locationGraph.className = 'front';
	categoryGraph.className = 'behind';
}

function toTutorial6() {
	tutorial7.className = 'hidden';
	tutorial6.className = 'visible';
	tutorial5.className = 'hidden';
	locationGraph.className = 'behind';
	categoryGraph.className = 'front';
	map.className = 'behind';
}

function toTutorial7() {
	tutorial8.className = 'hidden'
	tutorial7.className = 'visible';
	tutorial6.className = 'hidden';
	categoryGraph.className = 'behind';
	map.className = 'front';
}

function toTutorial8() {
	tutorial8.className = 'visible';
	tutorial7.className = 'hidden';
	categoryGraph.className = 'behind';
	map.className = 'behind';
}

function toApp() {
	tutorial8.className = 'hidden';
	mist.className = 'clear';
	header.className = 'header';
	locationDropdown.className = 'above';
}
document.getElementById('tutorial-1-btn-forward').addEventListener("click", toTutorial2);
document.getElementById('tutorial-2-btn-back').addEventListener('click', toTutorial1);
document.getElementById('tutorial-2-btn-forward').addEventListener('click', toTutorial3);
document.getElementById('tutorial-3-btn-back').addEventListener('click', toTutorial2);
document.getElementById('tutorial-3-btn-forward').addEventListener('click', toTutorial4);
document.getElementById('tutorial-4-btn-back').addEventListener('click', toTutorial3);
document.getElementById('tutorial-4-btn-forward').addEventListener('click', toTutorial5);
document.getElementById('tutorial-5-btn-back').addEventListener('click', toTutorial4);
document.getElementById('tutorial-5-btn-forward').addEventListener('click', toTutorial6);
document.getElementById('tutorial-6-btn-back').addEventListener('click', toTutorial5);
document.getElementById('tutorial-6-btn-forward').addEventListener('click', toTutorial7);
document.getElementById('tutorial-7-btn-back').addEventListener('click', toTutorial6);
document.getElementById('tutorial-7-btn-forward').addEventListener('click', toTutorial8);
document.getElementById('tutorial-8-btn-back').addEventListener('click', toTutorial7);
document.getElementById('tutorial-8-btn-forward').addEventListener('click', toApp);








