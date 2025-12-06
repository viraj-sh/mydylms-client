document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "/api/v1";
    const overallValue = document.getElementById("overallValue");
    const detailedBody = document.getElementById("detailedBody");

    function showLoaderRow(message) {
        detailedBody.innerHTML = `<tr><td colspan="6" class="text-center text-gray-500 py-6 italic">${message}</td></tr>`;
    }

    // Updated: Accepts both old and new key formats for subject records
    function createIndividualTableHTML(data) {
        if (!data || !data.length)
            return `<div class="text-gray-500 italic py-2 text-center">No records found</div>`;

        return `
        <div class="overflow-x-auto mt-2">
            <table class="w-full text-left border-collapse rounded-xl shadow-sm">
                <thead class="bg-red-50 text-gray-700 uppercase text-sm rounded-t-xl">
                    <tr>
                        <th class="px-4 py-2">Class No</th>
                        <th class="px-4 py-2">Date</th>
                        <th class="px-4 py-2">Time</th>
                        <th class="px-4 py-2">Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(d => `
                        <tr class="hover:bg-gray-50 transition-colors duration-200 border-b last:border-b-0">
                            <td class="px-4 py-2">${d['Class No'] ?? d['class_no'] ?? '-'}</td>
                            <td class="px-4 py-2">${d['Date'] ?? d['date'] ?? '-'}</td>
                            <td class="px-4 py-2">${d['Time'] ?? d['time'] ?? '-'}</td>
                            <td class="px-4 py-2 font-medium ${(d['Status'] ?? d['status'] ?? '').startsWith('A') ? 'text-yellow-500' : 'text-green-600'}">
                                ${d['Status'] ?? d['status'] ?? '-'}
                            </td>
                        </tr>`).join('')}
                </tbody>
            </table>
        </div>`;
    }

    // Updated: Use new /attendance/overall endpoint and new response structure
    async function loadOverallAndDetailedAttendance() {
        overallValue.textContent = "--%";
        showLoaderRow("Loading detailed attendance...");
        try {
            const res = await fetch(`${API_BASE_URL}/attendance/overall`);
            const data = await res.json();

            if (!data.success || !data.data) {
                overallValue.textContent = "N/A";
                showLoaderRow("No detailed attendance found.");
                return;
            }

            // Set overall percentage
            overallValue.textContent =
                typeof data.data.overall_percentage === "number"
                    ? `${data.data.overall_percentage}%`
                    : "N/A";

            const detailed = Array.isArray(data.data.records) ? data.data.records : [];

            if (!detailed.length) {
                showLoaderRow("No detailed attendance found.");
                return;
            }

            detailedBody.innerHTML = "";

            detailed.forEach(sub => {
                const tr = document.createElement("tr");
                tr.className = "border-b hover:bg-gray-50 transition-colors duration-200";

                tr.innerHTML = `
                    <td class="px-4 py-3 font-medium">${sub.Subject || sub.subject || '-'}</td>
                    <td class="px-4 py-3">${sub['Total Classes'] ?? sub['Total_Classes'] ?? sub['total_classes'] ?? '-'}</td>
                    <td class="px-4 py-3">${sub.Present ?? sub.present ?? '-'}</td>
                    <td class="px-4 py-3">${sub.Absent ?? sub.absent ?? '-'}</td>
                    <td class="px-4 py-3">${sub.Percentage !== null && sub.Percentage !== undefined ? sub.Percentage : (sub.percentage !== null && sub.percentage !== undefined ? sub.percentage : '-')}%</td>
                    <td class="px-4 py-3">
                        ${sub.altid
                        ? `<button class="view-sub-btn text-red-900 font-medium hover:underline text-sm" data-altid="${sub.altid}" data-subject="${sub.Subject || sub.subject}">View</button>`
                        : '-'}
                    </td>
                `;

                detailedBody.appendChild(tr);

                // Expand / collapse subject-level attendance details
                if (sub.altid) {
                    const btn = tr.querySelector(".view-sub-btn");
                    btn.addEventListener("click", async () => {
                        let nextRow = tr.nextElementSibling;
                        if (nextRow && nextRow.classList.contains("details-row")) {
                            nextRow.remove();
                            return;
                        }

                        const detailsTr = document.createElement("tr");
                        detailsTr.className = "details-row bg-gray-50";
                        const td = document.createElement("td");
                        td.colSpan = 6;
                        td.className = "p-4";
                        td.innerHTML = `<p class="text-gray-500 text-center italic">Loading ${sub.Subject || sub.subject} attendance...</p>`;
                        detailsTr.appendChild(td);
                        tr.after(detailsTr);

                        try {
                            const res = await fetch(`${API_BASE_URL}/attendance/course/${sub.altid}`);
                            const data = await res.json();
                            // New API: data.data.attendance is the array
                            td.innerHTML = createIndividualTableHTML(Array.isArray(data.data?.attendance) ? data.data.attendance : []);
                        } catch (err) {
                            console.error(`Error loading attendance for ${sub.Subject || sub.subject}:`, err);
                            td.innerHTML = `<p class="text-yellow-500 text-center italic">Error loading attendance</p>`;
                        }
                    });
                }
            });

        } catch (err) {
            console.error("Error fetching overall/detailed attendance:", err);
            overallValue.textContent = "Error";
            showLoaderRow("Error loading detailed attendance.");
        }
    }

    // Init
    loadOverallAndDetailedAttendance();
});
