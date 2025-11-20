// ===============================
// NOTIFICATION POPUP (Toast)
// ===============================
function showNotification(message, type = "info") {
    // Création du conteneur si inexistant
    let container = document.getElementById("notif-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "notif-container";
        Object.assign(container.style, {
            position: "fixed",
            top: "20px",
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 9999,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "10px",
        });
        document.body.appendChild(container);
    }

    // Création de la notification
    const notif = document.createElement("div");
    notif.textContent = message;
    notif.classList.add("notif-box", type);

    // Style intégré
    Object.assign(notif.style, {
        minWidth: "250px",
        padding: "12px 20px",
        borderRadius: "8px",
        color: "#fff",
        fontWeight: "500",
        textAlign: "center",
        opacity: 0,
        transition: "opacity 0.3s, transform 0.3s",
        transform: "translateY(-20px)",
        boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
    });

    // Couleurs selon le type
    if (type === "success") notif.style.backgroundColor = "#28a745";
    else if (type === "error") notif.style.backgroundColor = "#dc3545";
    else if (type === "warning") notif.style.backgroundColor = "#ffc107";
    else notif.style.backgroundColor = "#17a2b8"; // info par défaut

    container.appendChild(notif);

    // Animation entrée
    setTimeout(() => {
        notif.style.opacity = 1;
        notif.style.transform = "translateY(0)";
    }, 10);

    // Suppression automatique
    setTimeout(() => {
        notif.style.opacity = 0;
        notif.style.transform = "translateY(-20px)";
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}

window.showNotification = showNotification;
