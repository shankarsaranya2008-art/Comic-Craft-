document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "comic-form"
            );

        const button =
            document.getElementById(
                "generate-btn"
            );

        if (!form || !button) {
            return;
        }


        form.addEventListener(
            "submit",
            () => {

                button.disabled = true;

                const span =
                    button.querySelector(
                        "span"
                    );

                if (span) {

                    span.textContent =
                        "Creating your comic...";
                }

                button.style.opacity =
                    "0.7";
            }
        );

    }
);