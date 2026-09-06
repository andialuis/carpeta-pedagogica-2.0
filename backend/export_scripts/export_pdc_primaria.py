/**
 * MOTOR PDC DINÁMICO (V14 - CORREGIDO Y BLINDADO MULTI-ÁREA)
 * Conectado a la Plantilla: "Plantilla PDC por Area Minedu 2026 Brita"
 */

function procesarPDC_V14() {
  const ID_CARPETA_ENTRADA = "1g2QRr1X-Zp2oeSeXDlu-mqZYcYKpxHnW"; 
  const ID_CARPETA_SALIDA   = "1jPfFlrbsy8_Mi3XaL8GaGdzHJa_Vun9p";
  // ID de la Plantilla Minedu 2026 Brita
  const ID_PLANTILLA_DOC   = "1Fzz1XdxdVljRCmSKq_oULj-HcjW9gC9LP3ZhXCCadPo";
  const URL_CARPETA_SALIDA = "https://drive.google.com/drive/folders/" + ID_CARPETA_SALIDA;

  console.log("=== INICIANDO MOTOR PDC V14 ===");
  
  const TIEMPO_INICIO = Date.now();
  const LIMITE_TIEMPO_MS = 5.5 * 60 * 1000; 
  const ZONA_HORARIA = Session.getScriptTimeZone(); 

  const carpetaEntrada = DriveApp.getFolderById(ID_CARPETA_ENTRADA);
  const carpetaSalida = DriveApp.getFolderById(ID_CARPETA_SALIDA);
  const plantilla = DriveApp.getFileById(ID_PLANTILLA_DOC);
  const archivos = carpetaEntrada.getFilesByType(MimeType.GOOGLE_DOCS);
  
  while (archivos.hasNext()) {
    if (Date.now() - TIEMPO_INICIO > LIMITE_TIEMPO_MS) break;

    let archivoGemini = archivos.next();
    let nombreOriginal = archivoGemini.getName();
    
    // SE AGREGÓ "_ERROR" PARA EVITAR BUCLES INFINITOS EN FUTURAS EJECUCIONES
    if (nombreOriginal.endsWith("_PROCESADO") || nombreOriginal.endsWith("_BORRADOR") || nombreOriginal.endsWith("_ERROR") || nombreOriginal.startsWith("PDC_")) continue;

    try {
      console.log("Procesando: " + nombreOriginal);
      let docOrigen = DocumentApp.openById(archivoGemini.getId());
      let textoBorrador = docOrigen.getBody().getText();
      
      let fechaCorta = Utilities.formatDate(new Date(), ZONA_HORARIA, "dd-MM-yyyy");
      let fechaLarga = Utilities.formatDate(new Date(), ZONA_HORARIA, "dd/MM/yyyy HH:mm");
      
      let mapa = mapearV14(textoBorrador);
      
      let numPDC = mapa["NUM_PDC"] ? mapa["NUM_PDC"].trim() : "00";
      let maestro = mapa["MAESTRO"] ? mapa["MAESTRO"].split(" ")[0] : "Docente"; 
      let trimestre = mapa["TRIMESTRE"] ? mapa["TRIMESTRE"].split(" ")[0] : "Trimestre"; 
      let nombreFinal = `PDC_N${numPDC}_${maestro}_${trimestre}_${fechaCorta}`.replace(/\s+/g, "_");

      let archivoFinal = plantilla.makeCopy(nombreFinal, carpetaSalida);
      let docFinal = DocumentApp.openById(archivoFinal.getId());
      let cuerpoFinal = docFinal.getBody();
      
      // FASE 1: INYECCIÓN
      Object.keys(mapa).forEach(tag => {
        let valor = mapa[tag];
        if (valor) inyectarV14(cuerpoFinal, tag, valor);
      });

      // FASE 2: LIMPIEZA
      // CORRECCIÓN: Regex global y abarcador para eliminar etiquetas residuales que no se inyectaron
      cuerpoFinal.replaceText("[\\[\\{]{1,2}[\\s\\w]+[\\]\\}]{1,2}", ""); 
      limpiarTablaV14(cuerpoFinal);
      docFinal.saveAndClose();
      
      // FASE 3: TRAZABILIDAD Y ÉXITO
      let bodyOrigen = docOrigen.getBody();
      let textoMarca = `✅ ESTE BORRADOR FUE PROCESADO Y EXPORTADO EL ${fechaLarga}. Encuentra tu documento aquí: ${URL_CARPETA_SALIDA}`;
      let parrafo = bodyOrigen.insertParagraph(0, textoMarca);
      
      parrafo.setAttributes({
        [DocumentApp.Attribute.FOREGROUND_COLOR]: '#008000',
        [DocumentApp.Attribute.FONT_SIZE]: 12,
        [DocumentApp.Attribute.BOLD]: true
      });
      
      let textObj = parrafo.editAsText();
      let inicioEnlace = textoMarca.indexOf(URL_CARPETA_SALIDA);
      let finEnlace = inicioEnlace + URL_CARPETA_SALIDA.length - 1;
      textObj.setLinkUrl(inicioEnlace, finEnlace, URL_CARPETA_SALIDA);
      
      docOrigen.saveAndClose();
      archivoGemini.setName(nombreOriginal + "_PROCESADO");
      console.log("✅ Éxito: " + nombreFinal);

    } catch (e) { 
      console.error("❌ Error en [" + nombreOriginal + "]: " + e.message); 
      
      // MANEJO DE ERROR: MODIFICAR DOCUMENTO Y CAMBIAR NOMBRE
      try {
        let fechaLargaError = Utilities.formatDate(new Date(), ZONA_HORARIA, "dd/MM/yyyy HH:mm");
        let docError = DocumentApp.openById(archivoGemini.getId());
        let bodyError = docError.getBody();
        
        let textoError = `❌ ERROR DE PROCESAMIENTO (${fechaLargaError}): ${e.message}. Revisa el formato y vuelve a intentarlo eliminando la terminación "_ERROR" del título.`;
        let parrafoError = bodyError.insertParagraph(0, textoError);
        
        parrafoError.setAttributes({
          [DocumentApp.Attribute.FOREGROUND_COLOR]: '#FF0000', // Rojo
          [DocumentApp.Attribute.FONT_SIZE]: 12,
          [DocumentApp.Attribute.BOLD]: true
        });
        
        docError.saveAndClose();
        archivoGemini.setName(nombreOriginal + "_ERROR");
      } catch (errorSecundario) {
        console.error("No se pudo escribir el mensaje de error en el documento: " + errorSecundario.message);
      }
    }
  }
}

function mapearV14(texto) {
  let mapa = {};
  // CORRECCIÓN: Se agregó flexibilidad en los espacios antes y después del tag de cierre (\s*\1\s*)
  let regex = /[\[\{]{1,2}\s*INICIO\s*:\s*([^\]\}]+?)\s*[\]\}]{1,2}([\s\S]*?)[\[\{]{1,2}\s*FIN\s*:\s*\s*\1\s*\s*[\]\}]{1,2}/gi;
  let match;
  
  while ((match = regex.exec(texto)) !== null) {
    let tag = match[1].trim().toUpperCase();
    let contenido = match[2].trim();
    
    // MEJORA INTEGRAL: Si la etiqueta ya existe (duplicada en el borrador), acumula el contenido con saltos de línea
    if (mapa[tag]) {
      mapa[tag] += "\n\n" + contenido;
    } else {
      mapa[tag] = contenido;
    }
  }
  return mapa;
}

function inyectarV14(cuerpo, tag, texto) {
  let marcadorRegex = "[\\[\\{]{1,2}\\s*" + tag + "\\s*[\\]\\}]{1,2}";
  let regexExacto = new RegExp("[\\[\\{]{1,2}\\s*" + tag + "\\s*[\\]\\}]{1,2}", "g");
  let hallado = cuerpo.findText(marcadorRegex);
  
  let intentos = 0;
  while (hallado && intentos < 50) {
    intentos++;
    let el = hallado.getElement();
    let celda = null;
    let curr = el.getParent();
    
    while (curr && curr.getType() !== DocumentApp.ElementType.BODY_SECTION) {
      if (curr.getType() === DocumentApp.ElementType.TABLE_CELL) { celda = curr; break; }
      curr = curr.getParent();
    }
    
    if (celda) {
      let textoCelda = celda.getText().trim();
      let esUnico = textoCelda.match(regexExacto) && textoCelda.replace(regexExacto, "").trim() === "";
      
      if (esUnico) {
        celda.clear(); 
        let lineas = texto.split(/\r?\n/);
        lineas.forEach(l => {
          if (l.trim() !== "") {
            let p = celda.appendParagraph(l.trim());
            p.setAttributes({ [DocumentApp.Attribute.FONT_FAMILY]: 'Arial Narrow', [DocumentApp.Attribute.FONT_SIZE]: 10 });
          }
        });
        if (celda.getNumChildren() > 1 && celda.getChild(0).asParagraph().getText() === "") {
          celda.removeChild(celda.getChild(0));
        }
      } else {
        let textElement = el.asText();
        textElement.setText(textElement.getText().replace(regexExacto, texto));
      }
    } else {
      let textElement = el.asText();
      textElement.setText(textElement.getText().replace(regexExacto, texto));
    }
    hallado = cuerpo.findText(marcadorRegex);
  }
}

function limpiarTablaV14(cuerpo) {
  let tablas = cuerpo.getTables();
  for (let t = 0; t < tablas.length; t++) {
    let tabla = tablas[t];
    for (let i = tabla.getNumRows() - 1; i >= 0; i--) {
      let fila = tabla.getRow(i);
      let textoFila = fila.getText().replace(/\s+/g, "");
      
      if (textoFila === "") {
        let tieneImagen = false;
        let numCeldas = fila.getNumCells();
        for (let c = 0; c < numCeldas; c++) {
          if (fila.getCell(c).findElement(DocumentApp.ElementType.INLINE_IMAGE)) {
            tieneImagen = true;
            break; 
          }
        }
        if (!tieneImagen) {
          try { tabla.removeRow(i); } catch(e) {}
        }
      }
    }
  }
}
