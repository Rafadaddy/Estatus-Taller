// Script para la impresión de reportes
document.addEventListener("DOMContentLoaded", function() {
    // Buscar el botón de impresión
    const btnImprimir = document.getElementById("imprimirBtn");
    
    if (btnImprimir) {
        // Añadir listener de evento
        btnImprimir.addEventListener("click", generarReporte);
    }
});

// Función para generar e imprimir el reporte
function generarReporte() {
    try {
        // Obtener datos del formulario
        const unitNumber = document.getElementById("unit_number").value;
        const operator = document.getElementById("operator_name").value;
        const description = document.getElementById("description").value;
        
        // Verificar que todos los campos necesarios estén completados
        if (!unitNumber || !operator || !description) {
            alert("Por favor complete todos los campos del formulario antes de imprimir el reporte.");
            return;
        }
        
        // Obtener la fecha actual formateada
        const fecha = new Date();
        const fechaFormateada = fecha.toLocaleDateString('es-MX');
        
        // Crear HTML del reporte
        const reporteHTML = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Taller - ${unitNumber}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                @page {
                    size: 8.5in 4in;
                    margin: 0;
                }
                .contenedor {
                    width: 8.5in;
                    height: 4in;
                    padding: 0.5in;
                    box-sizing: border-box;
                }
                .encabezado {
                    display: flex;
                    justify-content: space-between;
                    border-bottom: 1px solid #000;
                    margin-bottom: 10px;
                    padding-bottom: 5px;
                }
                .titulo {
                    font-weight: bold;
                    font-size: 14px;
                }
                .fecha {
                    font-weight: bold;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 10px;
                }
                td {
                    padding: 3px 5px;
                }
                .etiqueta {
                    font-weight: bold;
                    width: 90px;
                }
                .valor {
                    border-bottom: 1px solid #000;
                }
                .seccion-trabajo {
                    margin-top: 10px;
                    font-weight: bold;
                }
                .linea {
                    border-bottom: 1px solid #000;
                    height: 25px;
                    margin-bottom: 5px;
                }
                .firmas {
                    display: flex;
                    justify-content: space-between;
                    margin-top: 20px;
                }
                .firma {
                    border-top: 1px solid #000;
                    width: 45%;
                    text-align: center;
                    padding-top: 5px;
                    font-size: 10px;
                }
            </style>
        </head>
        <body>
            <div class="contenedor">
                <div class="encabezado">
                    <div class="titulo">REPORTE DE TALLER</div>
                    <div class="fecha">${fechaFormateada}</div>
                </div>
                
                <table>
                    <tr>
                        <td class="etiqueta">MOTORISTA:</td>
                        <td class="valor">${unitNumber}</td>
                    </tr>
                    <tr>
                        <td class="etiqueta">OPERADOR:</td>
                        <td class="valor">${operator}</td>
                    </tr>
                    <tr>
                        <td class="etiqueta">SOLICITUD:</td>
                        <td class="valor">${description}</td>
                    </tr>
                </table>
                
                <div class="seccion-trabajo">TRABAJO DE TALLER REALIZADO:</div>
                <div class="linea"></div>
                <div class="linea"></div>
                <div class="linea"></div>
                <div class="linea"></div>
                <div class="linea"></div>
                <div class="linea"></div>
                <div class="linea"></div>
                
                <div class="firmas">
                    <div class="firma">Firma del Mecánico</div>
                    <div class="firma">V° B° Supervisor</div>
                </div>
            </div>
        </body>
        </html>
        `;
        
        // Abrir una nueva ventana para el reporte
        const ventanaReporte = window.open("", "_blank");
        ventanaReporte.document.write(reporteHTML);
        ventanaReporte.document.close();
        
        // Imprimir después de que se cargue completamente
        setTimeout(function() {
            ventanaReporte.print();
            // Cerrar la ventana después de imprimir (en algunos navegadores)
            ventanaReporte.onfocus = function() {
                ventanaReporte.close();
            };
        }, 500);
        
    } catch (error) {
        console.error("Error al generar el reporte:", error);
        alert("Ocurrió un error al generar el reporte. Por favor intente nuevamente.");
    }
}