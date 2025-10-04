document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const feedbackMessage = document.getElementById("feedback-message");

    const API_BASE_URL = "http://127.0.0.1:8000";

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
            // 2. Health check
            const healthRes = await fetch(`${API_BASE_URL}/health`);
            if (!healthRes.ok) throw new Error("API server is unreachable.");
            const healthData = await healthRes.json();
            if (healthData.status !== "OK") throw new Error("Server is down.");

            // 3. Attempt login
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => null);
                const errorMsg = errData?.detail || errData?.message || "Login failed. Please try again.";
                console.error("Login error:", errorMsg);
                showMessage(errorMsg, "error");
                return;
            }

            const data = await res.json();

            if (data.success) {
                localStorage.setItem("authToken", data.token);
                showMessage("Login successful! Redirecting...", "success");

                setTimeout(() => {
                    window.location.href = "/pages/dashboard.html";
                }, 1200);
            } else {
                showMessage(data.message || "Invalid credentials.", "error");
            }
        } catch (err) {
            console.error("Unexpected error:", err);
            showMessage("Unable to connect to the server. Please try again.", "error");
        }
    });
});
