const header = document.querySelector("header");

window.addEventListener("scroll" , function(){
    header.classList.toggle("sticky", window.scrollY > 0);

});
    // Smooth scroll

let menu = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navbar');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navbar.classList.toggle('open');
};

window.onscroll = () => {
    menu.classList.remove('bx-x');
    navbar.classList.remove('open');
};

document.getElementById('email').addEventListener('input', function (e) {
    var pattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
    if (pattern.test(e.target.value)) {
        e.target.setCustomValidity('');
    } else {
        e.target.setCustomValidity('Please enter a valid email address');
    }
});

// window.addEventListener("load", function() {
//     var bannerImage = document.querySelector(".banner img");
//     bannerImage.classList.add("loaded");
// });

