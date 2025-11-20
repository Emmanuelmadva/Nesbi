const container = document.getElementById('productsContainer');
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggleSidebar');
const categoriesList = document.getElementById('categoriesList');

let produits = []; // tableau vide, rempli depuis l'API

// Toggle sidebar
toggleBtn.addEventListener('click', () => {
  sidebar.style.display = (sidebar.style.display === 'none' || sidebar.style.display === '') ? 'block' : 'none';
});

// Fonction pour afficher les produits
function afficherProduits(categorie = null) {
  container.innerHTML = '';
  const filtres = categorie ? produits.filter(p => p.category === categorie) : produits;

  filtres.forEach(p => {
    const card = document.createElement('div');
    card.className = 'col-sm-6 col-md-4 col-lg-3';

    // URL de l'image via l'endpoint public
    const imageUrl = `http://127.0.0.1:8000/products/${p.id}/image/public`;

    card.innerHTML = `
      <div class="card h-100">
        <img src="${imageUrl}" class="card-img-top" alt="${p.name}" onerror="this.src='https://via.placeholder.com/150';">
        <div class="card-body d-flex flex-column">
          <h6 class="card-title">${p.name}</h6>
          <p class="text-muted mb-2">${p.category || 'Non catégorisé'}</p>
          <p class="fw-bold mb-3">${p.price} FCFA</p>
          <div class="mt-auto d-flex gap-2">
            <button class="btn btn-success btn-sm flex-fill">Ajouter au panier</button>
            <button class="btn btn-primary btn-sm flex-fill">Voir</button>
          </div>
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

// Fonction pour générer la liste des catégories
function initCategories() {
  const categories = [...new Set(produits.map(p => p.category).filter(c => c))]; // ignore null/undefined
  categoriesList.innerHTML = '';

  categories.forEach(cat => {
    const li = document.createElement('li');
    li.className = 'list-group-item list-group-item-action';
    li.textContent = cat;
    li.style.cursor = 'pointer';
    li.style.background = 'transparent';
    li.style.color = 'white';
    li.onclick = () => afficherProduits(cat);
    categoriesList.appendChild(li);
  });

  // Ajouter un bouton "Tous"
  const allLi = document.createElement('li');
  allLi.className = 'list-group-item list-group-item-action';
  allLi.textContent = 'Tous';
  allLi.style.cursor = 'pointer';
  allLi.style.background = 'transparent';
  allLi.style.color = 'white';
  allLi.onclick = () => afficherProduits();
  categoriesList.prepend(allLi);
}

// Appel API pour récupérer les produits
async function loadProducts() {
  try {
    const response = await fetch('http://127.0.0.1:8000/products/all');
    if (!response.ok) throw new Error('Erreur lors de la récupération des produits');
    produits = await response.json();
    initCategories();
    afficherProduits();
  } catch (error) {
    console.error(error);
    container.innerHTML = `<p class="text-danger">Impossible de charger les produits pour le moment.</p>`;
  }
}

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', loadProducts);
