/*En el clic del botón hacemos una petición a ./guardar_foto*/
const $btnTomarFotoServidor = document.querySelector("#btnTomarFotoServidor"),
    $estado = document.querySelector("#estado");
$btnTomarFotoServidor.onclick = async() => {
    $estado.textContent = "Tomando foto";
    const respuestaRaw = await fetch("./guardar_foto");
    const respuesta = await respuestaRaw.json();
    let mensaje = "";
    if (respuesta.ok) {
        mensaje = 'Foto guardada como: ${respuesta.nombre_foto}';
    } else {
        mensaje = 'Error al tomar foto';
    }
    $estado.textContent = mensaje;
};