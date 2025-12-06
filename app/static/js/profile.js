document.addEventListener("DOMContentLoaded", () => {
    const profileContent = document.getElementById("profileContent");
    const userInfo = JSON.parse(localStorage.getItem("userInfo") || "{}");

    if (!userInfo || !userInfo.user_name) {
        profileContent.innerHTML = "<p class='text-red-500 col-span-full text-center'>User info not found. Please login again.</p>";
        return;
    }

    const sections = [
        {
            title: "Personal Info",
            fields: [
                { key: "user_name", label: "Name" },
                { key: "dob", label: "DOB" },
                { key: "gender", label: "Gender" },
                { key: "roll_no", label: "Roll No" },
                { key: "category", label: "Category" },
                { key: "religion", label: "Religion" }
            ]
        },
        {
            title: "Contact Info",
            fields: [
                { key: "email_id", label: "Email ID" },
                { key: "mob_no", label: "Mobile No" },
                { key: "pmob_no", label: "Parent Mobile No" },
                { key: "femail_id", label: "Parent Email ID" },
                { key: "address", label: "Address" },
                { key: "city", label: "City" },
                { key: "postal_code", label: "Postal Code" },
                { key: "country", label: "Country" }
            ]
        },
        {
            title: "Academic Info",
            fields: [
                { key: "coll_name", label: "College Name" },
                { key: "degree_name", label: "Degree" }
            ]
        },
        {
            title: "Parents",
            fields: [
                { key: "father_name", label: "Father's Name" },
                { key: "mother_name", label: "Mother's Name" }
            ]
        }
    ];


    profileContent.innerHTML = sections.map(section => `
    <div class="col-span-full md:col-span-1 bg-gray-50 p-4 rounded-lg shadow-sm">
        <h2 class="text-lg font-semibold text-red-800 mb-3 border-b pb-1">${section.title}</h2>
        <div class="space-y-2">
            ${section.fields.map(f => `
                <div class="flex justify-between">
                    <span class="font-medium text-gray-600">${f.label}</span>
                    <span class="text-gray-800">${userInfo[f.key] ?? "-"}</span>
                </div>
            `).join("")}
        </div>
    </div>
`).join("");
});
