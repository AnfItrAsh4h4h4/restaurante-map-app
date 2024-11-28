// Inicializa o mapa com a visão de Brasília
var map = L.map('map').setView([-15.7942, -47.8822], 13);

// Adiciona o tile layer ao mapa (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

// Função para buscar e exibir os restaurantes na lista e no mapa
fetch('/api/restaurants')
    .then(response => response.json())
    .then(data => {
        const restaurantList = document.getElementById('restaurant-items');
        
        data.forEach(restaurant => {
            const listItem = document.createElement('li');
            const user = "{{ current_user.id }}"; // Flask injeta o ID do usuário logado
            
            // Verifica se o usuário já avaliou o restaurante
            const userReview = restaurant.reviews && restaurant.reviews[user];
            const userRating = userReview ? userReview : "Não avaliado";

            // Criação do item na lista de restaurantes
            listItem.innerHTML = `
                <strong>${restaurant.name}</strong> - ${restaurant.cuisine} | Avaliação média: ${restaurant.rating}
                <br>
                <label for="rating-${restaurant.name}">Sua Avaliação (atual: ${userRating}):</label>
                <select id="rating-${restaurant.name}">
                    <option value="1" ${userRating === 1 ? "selected" : ""}>1</option>
                    <option value="2" ${userRating === 2 ? "selected" : ""}>2</option>
                    <option value="3" ${userRating === 3 ? "selected" : ""}>3</option>
                    <option value="4" ${userRating === 4 ? "selected" : ""}>4</option>
                    <option value="5" ${userRating === 5 ? "selected" : ""}>5</option>
                </select>
                <button onclick="submitReview('${restaurant.name}')">Salvar Avaliação</button>
            `;
            restaurantList.appendChild(listItem);

            // Adiciona um marcador para o restaurante no mapa
            const marker = L.marker([restaurant.latitude, restaurant.longitude]).addTo(map);
            marker.bindPopup(`<b>${restaurant.name}</b><br>${restaurant.cuisine}<br>Avaliação média: ${restaurant.rating}`);
        });
    })
    .catch(error => console.error('Erro ao carregar os restaurantes:', error));

// Função para enviar a avaliação do usuário para o servidor
function submitReview(restaurantName) {
    const rating = document.getElementById(`rating-${restaurantName}`).value;
    fetch('/api/reviews', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: restaurantName,
            review: parseInt(rating)
        }),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        location.reload(); // Atualiza os dados da interface
    })
    .catch(error => console.error('Erro ao salvar avaliação:', error));
}
