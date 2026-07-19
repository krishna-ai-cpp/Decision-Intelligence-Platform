// ----------------------------------------------------------------------
// DIP web app — pure front-end behaviour only. Never talks to the
// backend directly; every action still goes through a normal Flask
// form POST / link so phase*.py stays the single source of truth.
// ----------------------------------------------------------------------

function toggleSidebar(force) {
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");
  if (!sidebar) return;
  const show = force !== undefined ? force : !sidebar.classList.contains("open");
  sidebar.classList.toggle("open", show);
  if (backdrop) backdrop.classList.toggle("open", show);
}

function toggleProfileMenu() {
  const menu = document.getElementById("profile-dropdown");
  if (menu) menu.classList.toggle("open");
}

document.addEventListener("click", function (e) {
  const menu = document.getElementById("profile-dropdown");
  const btn = e.target.closest(".profile-btn");
  if (menu && !btn && !e.target.closest(".profile-dropdown")) {
    menu.classList.remove("open");
  }
});

function confirmLogout() {
  if (confirm("Log out of your DIP session? Any unsaved progress in this session stays saved on the server, but the in-memory working data for this project will be cleared.")) {
    document.getElementById("logout-form").submit();
  }
  return false;
}

// Generic search-as-you-type filter for a <table>. Hides rows whose text
// doesn't match; purely client-side, no backend/query involved.
function filterTable(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  const countEl = document.getElementById(inputId.replace("search", "count")) ||
                  document.getElementById(tableId.replace("table", "count"));
  if (!input || !table) return;
  const q = input.value.trim().toLowerCase();
  const rows = table.querySelectorAll("tr");
  let visible = 0;
  rows.forEach(function (row, i) {
    if (i === 0) return; // header row
    const match = row.textContent.toLowerCase().includes(q);
    row.style.display = match ? "" : "none";
    if (match) visible++;
  });
  if (countEl) countEl.textContent = visible + " project(s)";
}

// Auto-dismiss toasts after 6s, but only ones that aren't console-output
// (those tend to be longer and worth reading, so leave them until closed).
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".toast").forEach(function (toast) {
    if (!toast.classList.contains("console")) {
      setTimeout(function () {
        toast.classList.add("toast-hide");
        setTimeout(function () { toast.remove(); }, 300);
      }, 6000);
    }
  });

  // Show a full-page loading overlay whenever a form on this page is
  // submitted, since several backend calls (training, EDA, reports)
  // take a few seconds and users need to know something is happening.
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (form.dataset.noLoading) return;
      if (form.hasAttribute("data-confirm") && !confirm(form.getAttribute("data-confirm"))) {
        e.preventDefault();
        return;
      }
      const overlay = document.getElementById("loading-overlay");
      if (overlay) overlay.classList.add("visible");
      const btn = form.querySelector("button[type=submit]");
      if (btn) btn.disabled = true;
    });
  });

  // Any link marked data-confirm asks before navigating (used for
  // destructive/irreversible actions like resuming over unsaved work).
  document.querySelectorAll("a[data-confirm]").forEach(function (link) {
    link.addEventListener("click", function (e) {
      if (!confirm(link.getAttribute("data-confirm"))) e.preventDefault();
    });
  });
});
