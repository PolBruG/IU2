function toggleMenu(idElemento) {
  var x = document.getElementById(idElemento);
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show"; // Lo muestra
  } else { 
    x.className = x.className.replace(" w3-show", ""); // Lo oculta
  }
}

function myDropFunc() {
    var x = document.getElementById("demoDrop");
    if (x.className.indexOf("w3-show") == -1) {
	x.className += " w3-show";
	x.previousElementSibling.className += " w3-green";
    }
    else { 
	x.className = x.className.replace(" w3-show", "");
	x.previousElementSibling.className = x.previousElementSibling.className.replace(" w3-green", "");
    }
}

function openNav() {
    document.getElementById("mySidebar").style.display = "block";
}

function closeNav() {
    document.getElementById("mySidebar").style.display = "none";
}

function toggleDropdown() {
    document.getElementById("myDropdown").classList.toggle("show");
}

window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}
		
function toggleEstat(boto) {
    let barraDispositiu = boto.closest('.dispositiu-barra');    
    let icono = barraDispositiu.querySelector('.icono');

    if (boto.innerHTML === "ON") {	
        boto.innerHTML = "OFF";
        boto.classList.remove("w3-green");
        boto.classList.add("w3-red");
        icono.style.opacity = "0.3";
        icono.style.filter = "grayscale(100%)";
    } else {
        boto.innerHTML = "ON";
        boto.classList.remove("w3-red");
        boto.classList.add("w3-green");
        icono.style.opacity = "1";
        icono.style.filter = "grayscale(0%)";
    }
    
}
	
function canviarEstat(casaId, habitacioId, dispId) {
    // Llamamos a una ruta especial que termina en /toggle
    fetch(`/casas/${casaId}/habitacions/${habitacioId}/dispositius/${dispId}/toggle`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            // Si Python nos dice que lo ha guardado, recargamos la página para ver el nuevo color
            window.location.reload();
        } else {
            alert("Error al canviar l'estat del dispositiu.");
        }
    })
    .catch(error => console.error('Error:', error));
}

function obrirDesplegable(id) {	
    var x = document.getElementById(id);
    if (x.className.indexOf("w3-show") == -1) {
        x.className += " w3-show"; 
    } else { 
        x.className = x.className.replace(" w3-show", "");
    }	
}

function guardarCasaReal() {
    const nomCasa = document.getElementById('inputNomCasaReal').value;

    //Enviamos la petición POST a la API de tu Flask
    fetch('/casas', {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nom: nomCasa })
    })
    .then(response => {
        if (response.ok) {
            //Si todo va bien, cerramos el modal
            document.getElementById('modalCasa').style.display = 'none';
            
            document.getElementById('inputNomCasaReal').value = '';
            
            // Recargamos la página para que se vea la nueva casa
            window.location.reload(); 
        } else {
            alert("Hi ha hagut un error en desar la casa.");
        }
    })
    .catch(error => console.error('Error:', error));
}

function guardarHabitacioReal(casaId) {
    const nomHab = document.getElementById('inputNomHabitacio').value;
    const plantaHab = document.getElementById('inputPlantaHabitacio').value;

    // Lo enviamos a la URL específica de esta casa
    fetch(`/casas/${casaId}/habitacions`, {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json'
        },
        // Enviamos el nombre y la planta
        body: JSON.stringify({ nom: nomHab, planta: plantaHab }) 
    })
    .then(response => {
        if (response.ok) {
            // 3. Cerramos modal y recargamos para ver los cambios
            document.getElementById('modalHabitacio').style.display = 'none';
            window.location.reload(); 
        } else {
            alert("Hi ha hagut un error en desar l'habitació.");
        }
    })
    .catch(error => console.error('Error:', error));
}

function filtrarCases(query) {
    const text = query.toLowerCase().trim();
    document.querySelectorAll('.habitacio-card').forEach(function(card) {
        const h2 = card.querySelector('h2');
        const nom = h2 ? h2.innerText.toLowerCase() : '';
        card.style.display = nom.includes(text) ? '' : 'none';
    });
}


function filtrarHabitacions(query) {
    const text = query.toLowerCase().trim();
    document.querySelectorAll('.habitacio-card').forEach(function(card) {
        const h2 = card.querySelector('h2');
        const nom = h2 ? h2.innerText.toLowerCase() : '';
        card.style.display = nom.includes(text) ? '' : 'none';
    });
}
function guardarDispositiuReal(casaId, habitacioId) {
    // 1. Leemos lo que ha escrito el usuario en el modal
    const nomDisp = document.getElementById('inputNomDisp').value;
    const tipusDisp = document.getElementById('inputTipusDisp').value;

    if (nomDisp.trim() === "" || tipusDisp.trim() === "") {
        alert("Si us plau, omple tots els camps.");
        return;
    }

    // 2. Enviamos la petición a la URL específica de esta habitación
    fetch(`/casas/${casaId}/habitacions/${habitacioId}/dispositius`, {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nom: nomDisp, tipus: tipusDisp }) 
    })
    .then(response => {
        if (response.ok) {
            // 3. Cerramos el modal y recargamos para ver el nuevo dispositivo
            document.getElementById('modalDispositiu').style.display = 'none';
            window.location.reload(); 
        } else {
            alert("Hi ha hagut un error en desar el dispositiu.");
        }
    })
    .catch(error => console.error('Error:', error));
}