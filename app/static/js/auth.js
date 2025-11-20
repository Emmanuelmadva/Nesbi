

document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");
  const showSignup = document.getElementById("showSignup");
  const showLogin = document.getElementById("showLogin");
  const modalTitle = document.getElementById("authModalLabel");
  const modalElement = document.getElementById("authModal");

  let modal = null;

  /* -------------------------
      SWITCH FORM
  ------------------------- */

  showSignup.addEventListener("click", function (e) {
    e.preventDefault();
    loginForm.classList.add("d-none");
    signupForm.classList.remove("d-none");
    modalTitle.textContent = "Inscription";
  });

  showLogin.addEventListener("click", function (e) {
    e.preventDefault();
    signupForm.classList.add("d-none");
    loginForm.classList.remove("d-none");
    modalTitle.textContent = "Connexion";
  });

  /* -------------------------
            LOGIN
  ------------------------- */
  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    toggleLoading(loginForm, true);

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();
      toggleLoading(loginForm, false);

      if (res.ok && data.access_token) {
        localStorage.setItem("token", data.access_token);
        showNotification("Connexion réussie ✔", "success");

        if (!modal) modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
      } else {
        showNotification(data.detail || "Identifiants incorrects ❌", "error");
      }
    } catch (error) {
      toggleLoading(loginForm, false);
      console.error(error);
      showNotification("Erreur réseau", "error");
    }
  });

  /* -------------------------
            REGISTER
  ------------------------- */
  signupForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("signupName").value.trim();
    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("signupPassword").value.trim();
    const role = "vendeur";

    toggleLoading(signupForm, true);

    try {
      const res = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password, role })
      });

      const data = await res.json();
      toggleLoading(signupForm, false);

      if (res.ok && data.id) {
        showNotification("Compte créé avec succès 🎉", "success");

        signupForm.classList.add("d-none");
        loginForm.classList.remove("d-none");
        modalTitle.textContent = "Connexion";

      } else {
        showNotification(data.detail || "Erreur lors de l'inscription ❌", "error");
      }
    } catch (error) {
      toggleLoading(signupForm, false);
      console.error(error);
      showNotification("Erreur réseau", "error");
    }
  });

  /* -------------------------
      BUTTON LOADER SYSTEM
  ------------------------- */
  function toggleLoading(form, isLoading) {
    const btn = form.querySelector("button[type=submit]");

    if (!btn.dataset.original) {
      btn.dataset.original = btn.innerHTML;
    }

    if (isLoading) {
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Patientez...`;
    } else {
      btn.disabled = false;
      btn.innerHTML = btn.dataset.original;
    }
  }
});
