// LOGIN AJAX HANDLER — does NOT modify HTML
document.addEventListener("submit", async function(e) {
    if (e.target.closest("form")) {
        e.preventDefault();

        const form = e.target.closest("form");
        const data = new FormData(form);

        const response = await fetch("/api/login/", {
            method: "POST",
            body: data
        });

        const result = await response.json();

        if (result.success) {
            window.location.href = result.redirect;
        } 
        else if (result.warning) {
            alert(result.warning);
        } 
        else if (result.error) {
            alert(result.error);
        }
    }
});
