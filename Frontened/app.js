// ================= CONFIG =================
const BASE_URL = "http://127.0.0.1:8500";

// ================= GLOBAL STATE =================
let currentRoot = "";
let currentPath = "";
let navHistory = [];
let navIndex = -1;

let contextFilePath = "";
let contextFileName = "";
let contextIsFolder = false;

// ================= TOAST =================
function showToast(message) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;

    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ================= ROOT HANDLING =================
function loadRoots() {
    fetch(`${BASE_URL}/files/roots`)
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById("root-select");
            if (!select) return;

            select.innerHTML = "";
            data.roots.forEach(r => {
                const opt = document.createElement("option");
                opt.value = r.id;
                opt.textContent = r.path;
                select.appendChild(opt);
            });

            currentRoot = select.value;
            currentPath = "";
            navHistory = [];
            navIndex = -1;
            loadFiles("");
        })
        .catch(() => showToast("❌ Failed to load roots"));
}

function changeRoot() {
    const select = document.getElementById("root-select");
    currentRoot = select.value;
    currentPath = "";
    navHistory = [];
    navIndex = -1;
    loadFiles("");
}

// ================= FILE LOADING =================
function loadFiles(path = "", recordHistory = true) {
    fetch(`${BASE_URL}/files?root=${currentRoot}&path=${encodeURIComponent(path)}`)
        .then(res => res.json())
        .then(data => {
            currentPath = data.current;

            if (recordHistory) {
                navHistory = navHistory.slice(0, navIndex + 1);
                navHistory.push(currentPath);
                navIndex++;
            }

            const label = document.getElementById("file-root-label");
            if (label) label.textContent = "Root: " + currentRoot;

            renderFileTree(data.items);
        })
        .catch(() => showToast("❌ Failed to load files"));
}

// ================= FILE TREE =================
function renderFileTree(items) {
    const root = document.getElementById("file-tree-root");
    root.innerHTML = "";

    // ⬅ Back button
    if (currentPath) {
        const backRow = document.createElement("div");
        backRow.className = "file-item dir";

        const backLabel = document.createElement("span");
        backLabel.className = "file-label";
        backLabel.textContent = "⬅ ..";

        backLabel.onclick = () => {
            const parent = currentPath.split("\\").slice(0, -1).join("\\");
            loadFiles(parent);
        };

        backRow.appendChild(backLabel);
        root.appendChild(backRow);
    }

    items.forEach(i => {
        const row = document.createElement("div");
        row.className = "file-item " + (i.is_dir ? "dir" : "file");

        const label = document.createElement("span");
        label.className = "file-label";
        label.textContent = (i.is_dir ? "📁 " : "📄 ") + i.name;

        // Single click = select
        label.onclick = () => {
            document
                .querySelectorAll(".file-label.selected")
                .forEach(el => el.classList.remove("selected"));
            label.classList.add("selected");
        };

        if (i.is_dir) {
            // Double click = open folder
            label.ondblclick = () => {
                const nextPath = currentPath
                    ? currentPath + "\\" + i.name
                    : i.name;
                loadFiles(nextPath);
            };

            // Right click = folder menu
            label.oncontextmenu = (e) => {
                e.preventDefault();
                const folderPath = currentPath
                    ? currentPath + "\\" + i.name
                    : i.name;
                showContextMenu(e, folderPath, i.name, true);
            };
        } else {
            // Double click = download file
            label.ondblclick = () => {
                const filePath = currentPath
                    ? currentPath + "\\" + i.name
                    : i.name;
                downloadFileWithProgress(filePath, i.name);
            };

            // Right click = file menu
            label.oncontextmenu = (e) => {
                e.preventDefault();
                const filePath = currentPath
                    ? currentPath + "\\" + i.name
                    : i.name;
                showContextMenu(e, filePath, i.name, false);
            };
        }

        row.appendChild(label);
        root.appendChild(row);
    });
}

// ================= DOWNLOAD WITH PROGRESS =================
function downloadFileWithProgress(path, filename) {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", `${BASE_URL}/files/download?root=${currentRoot}&path=${encodeURIComponent(path)}`);
    xhr.responseType = "blob";

    xhr.onload = () => {
        const blob = xhr.response;
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        a.click();
    };

    xhr.send();
}

// ================= CONTEXT MENU =================
function showContextMenu(e, path, name, isFolder) {
    contextFilePath = path;
    contextFileName = name;
    contextIsFolder = isFolder;

    const menu = document.getElementById("context-menu");
    menu.style.top = e.pageY + "px";
    menu.style.left = e.pageX + "px";
    menu.style.display = "block";
}

document.addEventListener("click", () => {
    const menu = document.getElementById("context-menu");
    if (menu) menu.style.display = "none";
});

function contextDownload() {
    if (contextIsFolder) {
        window.open(
            `${BASE_URL}/folders/download?root=${currentRoot}&path=${encodeURIComponent(contextFilePath)}`,
            "_blank"
        );
    } else {
        downloadFileWithProgress(contextFilePath, contextFileName);
    }
}

function contextDelete() {
    if (!confirm("Delete this item?")) return;

    fetch(`${BASE_URL}/folders/delete?root=${currentRoot}&path=${encodeURIComponent(contextFilePath)}`, {
        method: "DELETE"
    })
        .then(() => {
            showToast("🗑 Deleted");
            loadFiles(currentPath);
        })
        .catch(() => showToast("❌ Delete failed"));
}

function contextRename() {
    const newName = prompt("New name:", contextFileName);
    if (!newName) return;

    fetch(`${BASE_URL}/folders/rename?root=${currentRoot}&path=${encodeURIComponent(contextFilePath)}&new_name=${encodeURIComponent(newName)}`, {
        method: "POST"
    })
        .then(() => {
            showToast("✏ Renamed");
            loadFiles(currentPath);
        })
        .catch(() => showToast("❌ Rename failed"));
}

// ================= NAVIGATION =================
function navigateBack() {
    if (navIndex <= 0) return;
    navIndex--;
    loadFiles(navHistory[navIndex], false);
}

function navigateForward() {
    if (navIndex >= navHistory.length - 1) return;
    navIndex++;
    loadFiles(navHistory[navIndex], false);
}

// Keyboard shortcuts (Alt + ← / →)
document.addEventListener("keydown", (e) => {
    const filesPage = document.getElementById("files");
    if (!filesPage || !filesPage.classList.contains("active")) return;

    if (e.altKey && e.key === "ArrowLeft") {
        e.preventDefault();
        navigateBack();
    }

    if (e.altKey && e.key === "ArrowRight") {
        e.preventDefault();
        navigateForward();
    }
});

// ================= INIT =================
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("root-select")) {
        loadRoots();
    }
});
