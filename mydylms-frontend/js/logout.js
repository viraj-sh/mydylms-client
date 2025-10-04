document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "http://127.0.0.1:8000"; // update per environment
    const logoutBtn = document.querySelector('a[href="/index.html"]');

    if (logoutBtn) {
        logoutBtn.addEventListener("click", async (e) => {
            e.preventDefault();

            try {
                // Attempt to delete credentials on server
                await fetch(`${API_BASE_URL}/auth`, {
                    method: "DELETE",
                });
            } catch (err) {
                console.error("Error deleting credentials:", err);
                // Ignore errors, still proceed to redirect
            } finally {
                // Clear local storage/session storage
                localStorage.removeItem("authToken");
                sessionStorage.clear();

                // Redirect to index.html
                window.location.href = "/index.html";
            }
        });
    }
});
