const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');
const closeBtn = document.querySelector('#close-btn')

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
    closeBtn.style.right = `20px`
    closeBtn.style.padding = `0px`
    closeBtn.style.left = null
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
    closeBtn.style.left = `20px`
    closeBtn.style.padding = `0px`
    closeBtn.style.right = null
});

closeBtn.addEventListener('click', () => {
    window.location.href = '/'
})