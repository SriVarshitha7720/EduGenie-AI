document.addEventListener("DOMContentLoaded", function () {

    const themeButton = document.getElementById("themeToggle");

    if (!themeButton) return;

    function setTheme(theme){

        if(theme === "dark"){

            document.body.classList.add("dark-mode");
            themeButton.innerHTML = "☀️";

        }else{

            document.body.classList.remove("dark-mode");
            themeButton.innerHTML = "🌙";

        }

        localStorage.setItem("theme", theme);

    }

    themeButton.addEventListener("click", function(){

        if(document.body.classList.contains("dark-mode")){

            setTheme("light");

        }else{

            setTheme("dark");

        }

    });

    const savedTheme = localStorage.getItem("theme") || "light";

    setTheme(savedTheme);

});