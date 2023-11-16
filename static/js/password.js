window.addEventListener("load", function() {
    // icono para mostrar contraseña
    showPassword = document.querySelector('.show-password');
    showPassword.addEventListener('click', () => {

        // elementos input de tipo clave
        password1 = document.querySelector('.password1');
        password2 = document.querySelector('.password2');
        if (password1.type === "text") {
            password1.type = "password"
            showPassword.classList.remove('fa-eye-slash');
        } else {
            password1.type = "text"
            showPassword.classList.toggle("fa-eye-slash");
        }
    })
});

window.addEventListener("load", function() {
    // icono para mostrar contraseña
    show_c_Password = document.querySelector('.show-confirm-password');
    show_c_Password.addEventListener('click', () => {

        // elementos input de tipo clave
        password2 = document.querySelector('.password2');
        if (password2.type === "text") {
            password2.type = "password"
            show_c_Password.classList.remove('fa-eye-slash');
        } else {
            password2.type = "text"
            show_c_Password.classList.toggle("fa-eye-slash");
        }
    })
});