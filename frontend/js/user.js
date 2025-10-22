document.addEventListener("DOMContentLoaded", async () => {
    const API_BASE_URL = "/api";
    const userMenuBtn = document.getElementById("userMenuBtn");
    const userDropdown = document.getElementById("userDropdown");
    const userNameDisplay = document.getElementById("userNameDisplay");
    const dropdownLogoutBtn = document.getElementById("dropdownLogoutBtn");

    // Toggle dropdown
    if (userMenuBtn) {
        userMenuBtn.addEventListener("click", () => {
            userDropdown.classList.toggle("hidden");
        });
    }

    // Fetch user info
    try {
        const res = await fetch(`${API_BASE_URL}/auth/me`);
        const data = await res.json();

        if (data.status === "success" && data.data?.user_name) {
            userNameDisplay.textContent = data.data.user_name;
            // Save the user info locally for profile.html
            localStorage.setItem("userInfo", JSON.stringify(data.data));
        } else {
            userNameDisplay.textContent = "User";
        }
    } catch (err) {
        console.error("Error fetching user info:", err);
        userNameDisplay.textContent = "User";
    }

    // Logout button inside dropdown
    if (dropdownLogoutBtn) {
        dropdownLogoutBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            try {
                await fetch(`${API_BASE_URL}/auth/logout`, { method: "DELETE" });
            } catch (err) {
                console.error("Error logging out:", err);
            } finally {
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = "/static/index.html";
            }
        });k
    }

    // Close dropdown if clicked outside
    document.addEventListener("click", (e) => {
        if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
            userDropdown.classList.add("hidden");
        }
    });
});
