document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "/api"; 

    // DOM elements
    const semesterGrid = document.getElementById("semesterGrid");
    const subjectGrid = document.getElementById("subjectGrid");
    const documentsContainer = document.getElementById("documentsContainer");
    const searchInput = document.getElementById("searchDocs");
    const filterSelect = document.getElementById("docFilter");

    // State
    let semesters = [];
    let subjects = [];
    let documents = [];
    let selectedSemester = null;
    let selectedSubject = null;

    // Types that should NOT show Download button
    const HIDE_ALL_BUTTONS_TYPES = new Set(["quiz", "forum", "assign"]);
    const HIDE_DOWNLOAD_TYPES = new Set(["url"]);
    const DIRECT_URL_TYPES = new Set([]);
    const HIDE_ALL_MESSAGE = "Manual Task";
    // Helpers
    function capitalizeFirst(s) {
        if (!s && s !== 0) return "";
        s = String(s);
        return s.charAt(0).toUpperCase() + s.slice(1);
    }

    function showPlaceholder(container, message) {
        container.innerHTML = `
            <div class="col-span-full text-center text-gray-400 py-6">
                ${message}
            </div>`;
    }

    function showError(container, message) {
        container.innerHTML = `
            <div class="col-span-full text-center text-red-600 py-6 font-medium">
                ${message}
            </div>`;
    }

    function clearActiveSelector(selectorClass) {
        document.querySelectorAll(selectorClass).forEach(el => {
            el.classList.remove("bg-red-50", "font-semibold");
        });
    }

    // 1. Load semesters
    async function loadSemesters() {
        showPlaceholder(semesterGrid, "Loading semesters...");
        try {
            const res = await fetch(`${API_BASE_URL}/sem`);
            if (!res.ok) throw new Error("Failed to fetch semesters");
            const data = await res.json();
            semesters = data.data || [];

            if (!semesters.length) {
                showError(semesterGrid, "No semesters found.");
                return;
            }

            semesterGrid.innerHTML = semesters
                .map((sem, idx) => `
                    <button data-sem="${idx + 1}" 
                        class="semester-btn bg-white shadow-sm border border-gray-200 px-4 py-2 rounded-xl hover:bg-red-50 transition text-sm font-medium flex-shrink-0">
                        ${sem.semester}
                    </button>
                `).join("");

            document.querySelectorAll(".semester-btn").forEach(btn =>
                btn.addEventListener("click", () => {
                    clearActiveSelector(".semester-btn");
                    btn.classList.add("bg-red-50", "font-semibold");

                    selectedSemester = btn.dataset.sem;
                    selectedSubject = null;

                    // Clear subjects and documents
                    subjectGrid.innerHTML = "";
                    documentsContainer.innerHTML = "";
                    showPlaceholder(documentsContainer, "Select a subject to load documents");

                    searchInput.value = "";
                    searchInput.disabled = true;
                    filterSelect.innerHTML = `<option value="all">All</option>`;
                    filterSelect.disabled = true;

                    loadSubjects(selectedSemester);
                })
            );
        } catch (err) {
            console.error("loadSemesters:", err);
            showError(semesterGrid, "Error loading semesters.");
        }
    }

    // 2. Load subjects
    async function loadSubjects(semNo) {
        showPlaceholder(subjectGrid, "Loading subjects...");

        try {
            const res = await fetch(`${API_BASE_URL}/sem/${semNo}/course`);
            if (!res.ok) throw new Error("Failed to fetch subjects");

            const data = await res.json().catch(() => null);
            if (!data || data.status !== "success" || !data.data) {
                showError(subjectGrid, "Unexpected response from server.");
                return;
            }

            const subjects = data.data.subjects || [];

            if (!Array.isArray(subjects) || subjects.length === 0) {
                showError(subjectGrid, "No subjects found for this semester.");
                return;
            }

            // Render subjects as a list
            subjectGrid.innerHTML = `
            <ul class="flex flex-col gap-1">
                ${subjects
                    .map(
                        sub => `
                            <li data-sub="${sub.id}" 
                                class="subject-item px-3 py-2 cursor-pointer hover:bg-red-50 rounded transition">
                                ${sub.name}
                            </li>`
                    )
                    .join("")}
            </ul>
        `;

            // Attach click listeners to each subject
            document.querySelectorAll(".subject-item").forEach(item =>
                item.addEventListener("click", () => {
                    clearActiveSelector(".subject-item");
                    item.classList.add("bg-red-50", "font-semibold");

                    const selectedSubject = item.dataset.sub;

                    // Reset document-related UI
                    documentsContainer.innerHTML = "";
                    searchInput.value = "";
                    searchInput.disabled = true;
                    filterSelect.innerHTML = `<option value="all">All</option>`;
                    filterSelect.disabled = true;

                    // ✅ Updated: loadDocuments now only needs subId
                    loadDocuments(selectedSubject);
                })
            );
        } catch (err) {
            console.error("loadSubjects:", err);
            showError(subjectGrid, "Error loading subjects. Please try again.");
        }
    }


    // 3. Load documents
    async function loadDocuments(courseId) {
        if (!courseId) {
            showPlaceholder(documentsContainer, "Select a subject to load documents");
            return;
        }

        // Skeleton loader
        documentsContainer.innerHTML = Array.from({ length: 6 })
            .map(() => `<div class="animate-pulse bg-gray-200 h-28 rounded-xl w-full"></div>`)
            .join("");

        try {
            const res = await fetch(`${API_BASE_URL}/course/${courseId}/docs`);
            if (!res.ok) throw new Error("Failed to fetch documents");

            const data = await res.json().catch(() => null);
            if (!data || data.status !== "success" || !Array.isArray(data.data)) {
                showError(documentsContainer, "Unexpected server response.");
                return;
            }

            // Flatten all weeks into one array
            documents = data.data.flatMap(week => Array.isArray(week.docs) ? week.docs : []);

            if (!documents.length) {
                showPlaceholder(documentsContainer, "No documents found for this course.");
                return;
            }

            // Create filter dropdown options
            const types = Array.from(new Set(documents.map(d => (d.mod || "unknown").toLowerCase()))).sort();
            filterSelect.innerHTML =
                `<option value="all">All</option>` +
                types.map(t => `<option value="${t}">${capitalizeFirst(t)}</option>`).join("");
            filterSelect.disabled = false;
            searchInput.disabled = false;

            renderDocuments();
        } catch (err) {
            console.error("loadDocuments:", err);
            showError(documentsContainer, "Error loading documents. Please try again.");
        }
    }




    // 4. Render documents
    function renderDocuments() {
        if (!documents || !documents.length) {
            showPlaceholder(documentsContainer, "Select a subject to load documents");
            return;
        }

        const query = (searchInput.value || "").toLowerCase().trim();
        const filter = (filterSelect.value || "all").toLowerCase();

        const filtered = documents.filter(doc => {
            const modType = (doc.mod || "unknown").toLowerCase();
            const matchesFilter = filter === "all" || modType === filter;
            const matchesSearch =
                (doc.doc_name || "").toLowerCase().includes(query) ||
                (doc.module || "").toLowerCase().includes(query);
            return matchesFilter && matchesSearch;
        });

        if (!filtered.length) {
            showPlaceholder(documentsContainer, "No matching documents found");
            return;
        }

        // Utility to format date like "08 Oct, 02:15 PM"
        const formatDate = (timestamp) => {
            if (!timestamp) return "Unknown";
            const date = new Date(timestamp * 1000);
            const day = date.getDate().toString().padStart(2, "0");
            const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const month = monthNames[date.getMonth()];
            let hours = date.getHours();
            const minutes = date.getMinutes().toString().padStart(2, "0");
            const ampm = hours >= 12 ? "PM" : "AM";
            hours = hours % 12 || 12;
            return `${day} ${month}, ${hours.toString().padStart(2, "0")}:${minutes} ${ampm}`;
        };

        // Utility to clean filename (remove extension)
        const cleanFileName = (name = "Untitled") => {
            // Common extensions to strip
            const knownExts = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".zip"];
            let clean = name.trim();
            for (const ext of knownExts) {
                if (clean.toLowerCase().endsWith(ext)) {
                    clean = clean.slice(0, -ext.length);
                    break;
                }
            }
            // Fallback: strip anything after last '.' if any
            if (clean.includes(".")) {
                clean = clean.substring(0, clean.lastIndexOf("."));
            }
            return clean.trim();
        };

        documentsContainer.innerHTML = filtered.map(doc => {
            const modType = (doc.mod || "unknown").toLowerCase();
            const typeLabel = `Type: ${capitalizeFirst(modType)}`;
            const hideAllButtons = HIDE_ALL_BUTTONS_TYPES.has(modType);
            const hideDownload = HIDE_DOWNLOAD_TYPES.has(modType);
            const useDirectUrl = DIRECT_URL_TYPES.has(modType);

            const viewHref = useDirectUrl
                ? (doc.doc_url || "#")
                : (doc.view_id ? `${API_BASE_URL}/doc/${doc.view_id}?action=view` : "#");

            const downloadHref = doc.view_id
                ? `${API_BASE_URL}/doc/${doc.view_id}?action=download`
                : "#";

            const displayName = cleanFileName(doc.doc_name || doc.module || "Untitled");

            return `
            <div class="doc-card bg-white border border-gray-200 shadow-sm rounded-xl p-4 hover:shadow-md transition">
                <h4 class="font-semibold text-slate-800">${displayName}</h4>
                <p class="text-sm text-slate-500">${typeLabel}</p>
                <div class="mt-2 text-xs text-gray-500">Uploaded: ${formatDate(doc.time)}</div>
                <div class="mt-3 flex justify-between items-center">
                    <div class="text-xs text-gray-500">View ID: ${doc.view_id || "N/A"}</div>
                    <div class="flex gap-3">
                        ${hideAllButtons
                    ? `<span class="text-gray-400 text-sm italic">${HIDE_ALL_MESSAGE}</span>`
                    : `
                                    <a href="${viewHref}" target="_blank" rel="noopener noreferrer" class="text-red-700 font-medium hover:underline text-sm">View</a>
                                    ${hideDownload ? "" : `<a href="${downloadHref}" class="text-red-700 font-medium hover:underline text-sm">Download</a>`}
                                `
                }
                    </div>
                </div>
            </div>
        `;
        }).join("");
    }




    // 5. Event listeners
    searchInput.addEventListener("input", renderDocuments);
    filterSelect.addEventListener("change", renderDocuments);

    // Init
    loadSemesters();
});
