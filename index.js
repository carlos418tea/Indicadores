
//---Direcciones de la API---//
direc = 'http://127.0.0.1:8000/indicadores/?rango='

//---Selecciona 'x' para llamar 'x' dirección---//
function elije_direccion() {
  var index = document.getElementById("options").value //Opcion de Rango elejida
  var fecha_obj = document.getElementById("fecha").value //Fecha elejida

  // Para darle la vuelta a la fecha de YYYY-MM-DD a DD-MM-YYYY
  let Fecha_inversa = fecha_obj
  const [ano, mes, dia] = Fecha_inversa.split("-");
  let Fecha_ESP = `${dia}/${mes}/${ano}`;

  console.log(Fecha_ESP)
  Direccion_completa = direc + index + "&fecha=" + Fecha_ESP ;
  console.log(Direccion_completa)
  Datos_API()
}

//---Llamada Ajax---//
function Datos_API() {
    const xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      let estatus = this.status;

      if (this.readyState == 4){
        switch (estatus) {
          case 200:
            //Zona de indicadores
            var api = JSON.parse(this.responseText);
            document.getElementById("demo").innerHTML ="Número Clientes: " + api.numero_clientes + "<br> "
            + "Número Expedientes: " + api.numero_expedientes + "<br> " 
            + "Número Usuarios: " +  api.numero_usuarios;
            console.log(api)
            break;

          case 404:
            alert("Error de llamada " + this.status);
            break;
          
          case 418:
            var api_habla = JSON.parse(this.responseText);
            document.getElementById("demo").innerHTML = "Error: 418 <br> FastApi dice: " + api_habla.detail;
            break;

          case 512:
            var api_habla = JSON.parse(this.responseText);
            document.getElementById("demo").innerHTML = "Error: 512 <br> FastApi dice: " + api_habla.detail;
            break;

          case 500:
            var api_habla = JSON.parse(this.responseText);
            document.getElementById("demo").innerHTML = "Error: 500 <br> FastApi dice: " + api_habla.detail;
            break;

          case 0:
            alert("Problema relacionado con la BD. Estado: " + this.status)
            break;

          default: "Número de Error Estado no encontrado."
        }
      }
    }
    xhttp.open("GET", Direccion_completa, true);
    xhttp.send();
  }
  
  
  


