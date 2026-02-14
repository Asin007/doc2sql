let lastPreviewData = null;

function showLoading(show) {
    document.getElementById("loadingOverlay").style.display = show ? "flex" : "none";
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.style.display = "block";
    setTimeout(() => toast.style.display = "none", 3000);
}

async function previewSchema() {
    showLoading(true);

    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);

    const response = await fetch("/schema", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    lastPreviewData = data;

    showLoading(false);

    renderPreview(data);
}

function renderPreview(data) {
    const container = document.getElementById("previewContent");
    container.innerHTML = "";

    container.innerHTML += `<p><b>Table:</b> ${data.suggested_table_name}</p>`;
    container.innerHTML += `<p><b>Rows:</b> ${data.row_count_preview}</p>`;

    container.innerHTML += "<h4>Columns</h4>";

    Object.entries(data.columns).forEach(([col, type]) => {
        container.innerHTML += `
            <div>
                <input value="${col}" />
                <select>
                    <option ${type==="INTEGER"?"selected":""}>INTEGER</option>
                    <option ${type==="FLOAT"?"selected":""}>FLOAT</option>
                    <option ${type==="TEXT"?"selected":""}>TEXT</option>
                    <option ${type==="TIMESTAMP"?"selected":""}>TIMESTAMP</option>
                </select>
            </div>
        `;
    });

    document.getElementById("previewModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("previewModal").style.display = "none";
}

async function ingestFile() {
    showLoading(true);

    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);

    const response = await fetch("/ingest", {
        method: "POST",
        body: formData
    });

    showLoading(false);

    if (response.ok) {
        showToast("Ingestion successful!");
    } else {
        showToast("Ingestion failed.");
    }
}

function confirmIngest() {
    closeModal();
    ingestFile();
}

document.getElementById("fileInput").addEventListener("change", function() {
    const file = this.files[0];
    if (!file) return;

    const ext = file.name.split(".").pop();
    const badge = document.getElementById("fileBadge");

    badge.innerHTML = `<span style="background:#007bff;color:white;padding:4px 8px;border-radius:4px;">.${ext}</span>`;
});
