// Gestion des boutons +/-
document.addEventListener('DOMContentLoaded', function() {
    const plusBtn = document.querySelector('.btn-plus');
    const minusBtn = document.querySelector('.btn-minus');
    const chambresInput = document.getElementById('nbChambres');

    if (plusBtn && minusBtn && chambresInput) {
        plusBtn.addEventListener('click', function() {
            chambresInput.value = parseInt(chambresInput.value) + 1;
        });

        minusBtn.addEventListener('click', function() {
            if (parseInt(chambresInput.value) > 1) {
                chambresInput.value = parseInt(chambresInput.value) - 1;
            }
        });
    }

    // Gestion du formulaire de prédiction
    const form = document.querySelector('.form-estimation');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validation du lieu
            const lieuInput = document.getElementById('lieu');
            if (!lieuInput.value.trim()) {
                alert('Veuillez saisir un lieu');
                lieuInput.focus();
                return;
            }
            
            // Récupération des données du formulaire
            const formData = {
                lieu: document.getElementById('lieu').value,
                nbChambres: parseInt(document.getElementById('nbChambres').value),
                typeChambre: document.getElementById('typeChambre').value,
                genre: document.getElementById('genre').value,
                wifi: document.getElementById('wifi').checked,
                electricite: document.getElementById('electricite').checked,
                eau: document.getElementById('eau').checked
            };

            console.log('Données envoyées:', formData);
            
           
            fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    const prix = result.prediction;
                    window.location.href = `/resultat?prix=${prix}`;
                } else {
                    alert('Erreur: ' + result.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de connexion au serveur');
            });
        });
    }
});


document.querySelector('.form-estimation')?.addEventListener('submit', function(e) {
    // Vérifier si c'est le formulaire d'aide (a contient un champ montant)
    const montantInput = document.getElementById('montant');
    if (montantInput) {
        e.preventDefault();
        
        const formData = {
            lieu: document.getElementById('lieu').value,
            nbChambres: parseInt(document.getElementById('nbChambres').value),
            typeChambre: document.getElementById('typeChambre').value,
            myGenre: document.getElementById('myGenre').value,
            wifi: document.getElementById('wifi').checked,
            electricite: document.getElementById('electricite').checked,
            eau: document.getElementById('eau').checked,
            montant: parseFloat(document.getElementById('montant').value)
        };
        
        console.log("Données aide envoyées:", formData);
        
        // Afficher un indicateur de chargement
        const resultDiv = document.getElementById('resultat-message');
        if (resultDiv) {
            resultDiv.innerHTML = '<div style="text-align: center; padding: 15px; background: #fff3cd; color: #856404; border-radius: 8px; border: 1px solid #ffeaa7;">⏳ Envoi en cours...</div>';
        }
        
        fetch('/add-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(result => {
            if (resultDiv) {
                if (result.success) {
                    resultDiv.innerHTML = `
                        <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; border: 1px solid #c3e6cb; text-align: center; font-weight: bold;">
                            ${result.message}
                        </div>
                    `;
                    // Vider le formulaire après succès
                    this.reset();
                } else {
                    resultDiv.innerHTML = `
                        <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border: 1px solid #f5c6cb; text-align: center; font-weight: bold;">
                            Erreur: ${result.error}
                        </div>
                    `;
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (resultDiv) {
                resultDiv.innerHTML = `
                    <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; border: 1px solid #f5c6cb; text-align: center; font-weight: bold;">
                        Erreur de connexion au serveur
                    </div>
                `;
            }
        });
    }
});