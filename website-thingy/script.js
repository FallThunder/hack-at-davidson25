document.getElementById('fetch-data').addEventListener('click', () => {
    fetchBusinesses();
});

async function fetchBusinesses() {
    try {
        const response = await fetch('YOUR_GOOGLE_CLOUD_FUNCTION_URL');
        const data = await response.json();
        displayBusinesses(data);
    } catch (error) {
        console.error('Error fetching businesses:', error);
    }
}

function displayBusinesses(businesses) {
    const businessList = document.getElementById('business-list');
    businessList.innerHTML = '';
    businesses.forEach(business => {
        const businessItem = document.createElement('div');
        businessItem.className = 'business-item';
        businessItem.innerHTML = `
            <h2>${business.name}</h2>
            <p>${business.address}</p>
            <p>${business.phone}</p>
        `;
        businessList.appendChild(businessItem);
    });
}
