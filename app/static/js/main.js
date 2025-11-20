// ===========================================
// BOOTSTRAP HELPERS
// ===========================================
function showToast(message, type = "success") {
    const toastId = "toast-" + Date.now();

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    $("#toastContainer").append(toastHtml);
    const toast = new bootstrap.Toast(document.getElementById(toastId), { delay: 4000 });
    toast.show();
}

function openModal(id) {
    new bootstrap.Modal(document.getElementById(id)).show();
}

function closeModal(id) {
    bootstrap.Modal.getInstance(document.getElementById(id))?.hide();
}

// ===========================================
// AJAX GLOBAL SETTINGS
// ===========================================
$.ajaxSetup({
    contentType: "application/json",
    dataType: "json",
    error: function (xhr) {
        const msg = xhr.responseJSON?.detail || "Une erreur est survenue";
        showToast(msg, "danger");
    }
});

// ===========================================
// SPINNER / LOADER
// ===========================================
function showLoader() {
    $("#loader").removeClass("d-none");
}

function hideLoader() {
    $("#loader").addClass("d-none");
}

// ===========================================
// FORM HANDLING – LOGIN
// ===========================================
$(document).on("submit", "#loginForm", function (e) {
    e.preventDefault();
    showLoader();

    const data = {
        email: $("#loginEmail").val(),
        password: $("#loginPassword").val()
    };

    $.ajax({
        method: "POST",
        url: "/auth/login",
        data: JSON.stringify(data),
        success: function (res) {
            hideLoader();
            closeModal("loginModal");
            showToast("Connexion réussie !");
            localStorage.setItem("token", res.access_token);
        }
    });
});

// ===========================================
// SIGNUP FORM
// ===========================================
$(document).on("submit", "#signupForm", function (e) {
    e.preventDefault();
    showLoader();

    const data = {
        username: $("#signupUsername").val(),
        email: $("#signupEmail").val(),
        password: $("#signupPassword").val()
    };

    $.ajax({
        method: "POST",
        url: "/auth/register",
        data: JSON.stringify(data),
        success: function () {
            hideLoader();
            closeModal("signupModal");
            showToast("Compte créé avec succès !");
        }
    });
});

// ===========================================
// AUTHENTICATED REQUEST EXAMPLE
// ===========================================
function apiGet(url, callback) {
    $.ajax({
        method: "GET",
        url: url,
        headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
        },
        success: callback,
    });
}

// Exemple d'appel protégé
// apiGet("/user/profile", (data) => console.log(data));


// ===========================================
// SMOOTH SCROLL + BUTTON TOP + ANIMATIONS
// ===========================================
$("a[href^='#']").on("click", function (e) {
    const target = $(this.getAttribute("href"));
    if (target.length) {
        e.preventDefault();
        $("html, body").animate({ scrollTop: target.offset().top - 70 }, 500);
    }
});

const backToTop = $(`
    <button class="btn btn-success rounded-circle"
            style="position:fixed;bottom:25px;right:25px;display:none;z-index:999;">
        ↑
    </button>
`);

$("body").append(backToTop);

$(window).on("scroll", () => {
    if ($(window).scrollTop() > 400) backToTop.show();
    else backToTop.hide();
});

backToTop.on("click", () => $("html, body").animate({ scrollTop: 0 }, 400));


// ===========================================
// FADE-IN ANIMATIONS
// ===========================================
$(".fade-in").css({ opacity: 0, transform: "translateY(30px)", transition: "0.6s" });

function applyFade() {
    $(".fade-in").each(function () {
        const rect = this.getBoundingClientRect();
        if (rect.top < window.innerHeight - 80) {
            $(this).css({ opacity: 1, transform: "translateY(0)" });
        }
    });
}

$(window).on("scroll load", applyFade);
