window.onload = function() {
    $('#onload').fadeOut(); /* Cuando se termine de cargar toda la página, desaparecer onload*/
    $('body').removeClass('hidden');
}

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            // Asignamos el atributo src a la tag de imagen
            $('#previo').attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}
// El listener va asignado al input
$("#file").change(function() {
    readURL(this);
    var mensaje_subido = document.getElementById("men_file");
    document.getElementById("men_file").innerHTML = "✅ Subido con éxito", mensaje_subido.style.color = "#19DD44";
});

function espera_captura() {
    return swal("Foto capturada en procesamiento", "Debe esperar unos segundos y automaticamente se redirigirá al panel de análisis final. Presione OK", "success");
}

function espera() {
    if ($('#file').val().length == 0) {
        /*swal("😱", "Error, debe subir una imagen para el procesamiento.", "error");*/
    } else {
        return swal("Imagen en procesamiento", "Debe esperar unos segundos y automaticamente se redirigirá al panel de análisis final. Presione OK", "success");
    }
}