
document.getElementById('fetch-drugs').addEventListener('click', function() {
    fetch('/stocked-drugs')
        .then(response => response.json())
        .then(data => {
            const drugList = document.getElementById('drug-list');
            drugList.innerHTML = '';
            data.forEach(drug => {
                const listItem = document.createElement('li');
                listItem.textContent = `${drug['Drug Name']} - ${drug['Stock Quantity']} in stock`;
                drugList.appendChild(listItem);
            });
        });
});
document.getElementById('addStockForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = {
        drug_name: document.getElementById('drug_name').value,
        batch_number: document.getElementById('batch_number').value,
        medicine_type: document.getElementById('medicine_type').value,
        manufacturer: document.getElementById('manufacturer').value,
        stock_quantity: document.getElementById('stock_quantity').value,
        expiry_date: document.getElementById('expiry_date').value,
        price: document.getElementById('price').value
    };

    const response = await fetch('/add-stock', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    });

    const result = await response.json();
    const messageDiv = document.getElementById('message');

    if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.style.color = 'green';
    } else {
        messageDiv.textContent = 'Failed to add stock';
        messageDiv.style.color = 'red';
    }

    // Clear the form
    document.getElementById('addStockForm').reset();
});

document.getElementById('send-message-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    fetch('/send-message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        alert(result.message);
    });
});
