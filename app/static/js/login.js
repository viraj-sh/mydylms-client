document.addEventListener("DOMContentLoaded", async () => {
    const loginForm = document.getElementById("login-form");
    const feedbackMessage = document.getElementById("feedback-message");

    const API_BASE_URL = "/api/v1";
    try {
        const tokenCheck = await fetch(`${API_BASE_URL}/auth/validate-session`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });

        const tokenData = await tokenCheck.json().catch(() => null);

        if (tokenData?.status === "success" && tokenData?.data?.valid) {
            if (feedbackMessage) {
                feedbackMessage.textContent = "Active session found — redirecting...";
                feedbackMessage.classList.remove("hidden", "text-red-600");
                feedbackMessage.classList.add("text-green-600");
            }

            setTimeout(() => {
                window.location.href = "/static/pages/dashboard.html";
            }, 800);

            return;
        }
    } catch (err) {
        console.warn("Session check failed:", err);
    }

    // Utility function to show feedback
    function showMessage(message, type = "error") {
        feedbackMessage.textContent = message;
        feedbackMessage.classList.remove("hidden", "text-red-600", "text-green-600");
        feedbackMessage.classList.add(type === "error" ? "text-red-600" : "text-green-600");
    }

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = loginForm.email.value.trim();
        const password = loginForm.password.value.trim();

        // 1. Validate email domain
        if (!email.endsWith("@dypatil.edu")) {
            showMessage("Only @dypatil.edu email addresses are allowed.", "error");
            return;
        }

        try {
            // 2. Attempt login
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await res.json().catch(() => null);

            if (!data) {
                showMessage("Unexpected server response. Please try again.", "error");
                return;
            }

            // 3. Handle invalid credentials
            if (data.detail === "Login failed: invalid credentials") {
                showMessage("Invalid email or password.", "error");
                return;
            }

            // 4. Validate successful login structure
            if (
                data.success === true &&
                data.data &&
                data.data.cookie &&
                data.data.sesskey &&
                data.data.web_key &&
                data.data.features_key &&
                data.data.my_key &&
                data.data.user_id
            ) {
                // Store session info
                localStorage.setItem("cookie", data.data.cookie);
                localStorage.setItem("sesskey", data.data.sesskey);
                localStorage.setItem("user_id", data.data.user_id);

                showMessage("Login successful! Fetching credentials...", "success");

                // 5. Call /auth/creds before redirecting
                // try {
                //     const credsRes = await fetch(`${API_BASE_URL}/auth/creds`, {
                //         method: "GET",
                //         headers: {
                //             "Content-Type": "application/json",
                //             "Authorization": `Bearer ${data.data.sesskey}`,
                //         },
                //         credentials: "include",
                //     });

                //     const credsData = await credsRes.json().catch(() => null);

                //     if (!credsRes.ok || !credsData) {
                //         showMessage("Failed to initialize user credentials. Please try again.", "error");
                //         return;
                //     }

                //     // Success — all steps complete
                //     showMessage("Login successful! Redirecting...", "success");
                //     setTimeout(() => {
                //         window.location.href = "/static/pages/dashboard.html";
                //     }, 1000);
                // } catch (credsErr) {
                //     console.error("Error fetching /auth/creds:", credsErr);
                //     showMessage("Error initializing credentials. Please try again.", "error");
                // }
            } else {
                showMessage("Login failed. Please try again.", "error");
            }
        } catch (err) {
            console.error("Unexpected error:", err);
            showMessage("Unable to connect to the server. Please try again.", "error");
        }
    });
});
