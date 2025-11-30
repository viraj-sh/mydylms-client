document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "/api/v1";
    const logoutBtn = document.querySelector('a[href="/static/index.html"]');

    if (!logoutBtn) return;

    logoutBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        try {
            const res = await fetch(`${API_BASE_URL}/auth/logout`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                credentials: "include"
            });

            const data = await res.json().catch(() => ({}));

            // ✅ Successful logout
            if (res.ok && data?.status === "success" && data?.data?.success) {
                console.log("Logout successful.");
            }
            // ⚠️ User already logged out or session expired
            else if (data?.detail === "User not logged in") {
                console.warn("User already logged out or session expired.");
            }
            // ❌ Some other server error
            else {
                console.error("Unexpected logout response:", data);
            }

        } catch (err) {
            console.error("Error during logout request:", err);
        } finally {
            // ✅ Always clear storage and redirect regardless
            localStorage.removeItem("authToken");
            sessionStorage.clear();
            window.location.href = "/static/index.html";
        }
    });
});
