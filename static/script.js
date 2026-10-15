document.addEventListener("DOMContentLoaded", function () {
    // Live search for the members table
    var search = document.getElementById("memberSearch");
    var table = document.getElementById("memberTable");

    if (search && table) {
        search.addEventListener("input", function () {
            var query = search.value.trim().toLowerCase();
            table.querySelectorAll("tbody tr").forEach(function (row) {
                if (row.querySelector("td[colspan]")) return; // empty-state row
                row.hidden = query !== "" && !row.textContent.toLowerCase().includes(query);
            });
        });
    }

    // Confirm before submitting any form that has data-confirm
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!window.confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    // Prevent double submits on POST forms
    document.querySelectorAll("form[method='POST']").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (event.defaultPrevented) return;
            var button = form.querySelector("button[type='submit']");
            if (button) {
                setTimeout(function () { button.disabled = true; }, 0);
            }
        });
    });
});