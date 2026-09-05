document.addEventListener("DOMContentLoaded", function () {

    const savedTheme = localStorage.getItem("vastrahub_theme");

    if (savedTheme === "dark") {
        document.body.classList.add("dark-mode");
    }

    const lightButton = document.getElementById("lightMode");
    const darkButton = document.getElementById("darkMode");

    if (lightButton) {
        lightButton.addEventListener("click", function () {

            document.body.classList.remove("dark-mode");

            localStorage.setItem(
                "vastrahub_theme",
                "light"
            );

        });
    }

    if (darkButton) {
        darkButton.addEventListener("click", function () {

            document.body.classList.add("dark-mode");

            localStorage.setItem(
                "vastrahub_theme",
                "dark"
            );

        });
    }

});