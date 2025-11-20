document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.getElementById("toggleSidebar");
  const overlay = document.getElementById("overlay");
  const mainContent = document.getElementById("main-content");

  // =======================
  // Sidebar et overlay
  // =======================
  sidebar.style.position = "fixed";
  sidebar.style.top = "0";
  sidebar.style.left = "-250px"; // cachée par défaut
  sidebar.style.width = "250px";
  sidebar.style.height = "100%";
  sidebar.style.backgroundColor = "#198754";
  sidebar.style.color = "#fff";
  sidebar.style.paddingTop = "20px";
  sidebar.style.transition = "left 0.3s";
  sidebar.style.zIndex = "1000";

  sidebar.querySelectorAll("a").forEach(link => {
    link.style.color = "#fff";
    link.style.display = "block";
    link.style.padding = "10px 15px";
    link.style.textDecoration = "none";
    link.addEventListener("mouseover", () => link.style.backgroundColor = "rgb(10 87 37)");
    link.addEventListener("mouseout", () => link.style.backgroundColor = "transparent");
  });

  overlay.style.position = "fixed";
  overlay.style.top = "0";
  overlay.style.left = "0";
  overlay.style.width = "100%";
  overlay.style.height = "100%";
  overlay.style.backgroundColor = "rgba(0,0,0,0.5)";
  overlay.style.display = "none";
  overlay.style.zIndex = "900";

  let open = false;

  function openSidebar() {
    sidebar.style.left = "0";
    overlay.style.display = "block";
    open = true;
  }

  function closeSidebar() {
    sidebar.style.left = "-250px";
    overlay.style.display = "none";
    open = false;
  }

  toggleBtn.addEventListener("click", () => {
    open ? closeSidebar() : openSidebar();
  });

  overlay.addEventListener("click", closeSidebar);

  window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
      sidebar.style.left = "0";
      overlay.style.display = "none";
      open = false;
    } else {
      sidebar.style.left = "-250px";
    }
  });

  // =======================
  // Style du contenu principal
  // =======================
  mainContent.style.padding = "20px 30px"; // padding haut/bas et gauche/droite
  const cards = mainContent.querySelectorAll(".card");
  cards.forEach(card => {
    card.style.margin = "10px"; // marge autour des cartes
    card.style.borderRadius = "10px"; // coins arrondis
    card.style.boxShadow = "0 2px 10px rgba(0,0,0,0.1)"; // ombre légère
  });

  // =======================
  // Récupération des données du dashboard
  // =======================
  async function loadDashboardData() {
    try {
      const res = await fetch("/dashboard/data");
      if (!res.ok) throw new Error("Erreur de récupération des données");
      const data = await res.json();
      document.getElementById("sales-count").textContent = data.sales || 0;
      document.getElementById("products-count").textContent = data.products || 0;
      document.getElementById("clients-count").textContent = data.clients || 0;
      document.getElementById("orders-count").textContent = data.orders || 0;
    } catch (err) {
      console.error(err);
    }
  }

  loadDashboardData();
});
