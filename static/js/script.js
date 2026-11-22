/* =========================================
   TASKFLOW - JAVASCRIPT
   ========================================= */

document.addEventListener("DOMContentLoaded", function () {

    // 1. SCROLL REVEAL ANIMATION

    const revealElements = document.querySelectorAll(".reveal");

    if ("IntersectionObserver" in window) {

        const observer = new IntersectionObserver(
            function (entries, observer) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add("visible");

                        observer.unobserve(entry.target);
                    }

                });

            },
            {
                threshold: 0.12
            }
        );

        revealElements.forEach(function (element) {
            observer.observe(element);
        });

    } else {

        revealElements.forEach(function (element) {
            element.classList.add("visible");
        });

    }


    // 2. AUTOMATICALLY SET MINIMUM SCHEDULER DATE

    const dateInputs = document.querySelectorAll(
        'input[type="datetime-local"]'
    );

    dateInputs.forEach(function (input) {

        const now = new Date();

        const localDate = new Date(
            now.getTime() - now.getTimezoneOffset() * 60000
        );

        const formattedDate = localDate.toISOString().slice(0, 16);

        input.min = formattedDate;

    });


    // 3. DISPLAY SELECTED FILE NAMES

    const fileInputs = document.querySelectorAll(
        'input[type="file"]'
    );

    fileInputs.forEach(function (input) {

        input.addEventListener("change", function () {

            const files = Array.from(input.files);

            if (files.length === 0) {
                return;
            }

            const fileNames = files.map(function (file) {
                return file.name;
            });

            console.log("Selected files:", fileNames);

            if (files.length === 1) {
                input.title = files[0].name;
            } else {
                input.title = files.length + " files selected";
            }

        });

    });


    // 4. PREVENT DOUBLE FORM SUBMISSION

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            if (!form.checkValidity()) {
                return;
            }

            const submitButton = form.querySelector(
                'button[type="submit"]:focus'
            ) || form.querySelector(
                'button[type="submit"]'
            );

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.dataset.originalText =
                    submitButton.innerHTML;

                submitButton.innerHTML = "Processing...";

            }

        });

    });


    // 5. AUTOMATICALLY DISMISS FLASH MESSAGES

    const flashMessages = document.querySelectorAll(
        ".flash-message"
    );

    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.transition = "opacity 0.5s ease";
            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 500);

        }, 5000);

    });


    // 6. CONFIRM BEFORE CANCELLING SCHEDULED EMAILS

    const cancelForms = document.querySelectorAll(
        'form[action*="/scheduler/delete"]'
    );

    cancelForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to cancel this scheduled email?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    console.log("TaskFlow JavaScript loaded successfully!");

});