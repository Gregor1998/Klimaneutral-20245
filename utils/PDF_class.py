from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Logo
        # Berechne die x-Position des Bildes, um es in die rechte Ecke zu verschieben
        image_width = 20
        image_x = self.w - self.r_margin - image_width

        # Setze die Position des Bildes
        self.image('assets/business-report.png', image_x, 8, image_width)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Berechne die Breite der Seite
        page_width = self.w - 2 * self.l_margin

        # Berechne die Position des Titels, um ihn zu zentrieren
        title_width = 100
        title_x = (page_width - title_width)/2 + image_width/2

        # Setze die Position des Titels
        self.set_x(title_x)

        # Titel
        self.cell(title_width, 10, 'Zusammenfassung', 0, 1, 'C')
        #Subtitel
        self.set_font('Arial', '', 8)
        self.cell(0, 10, 'Klimaneutral 20245', 0, 1, 'C')
        # Line break
        self.ln(5)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', '', 8)
        # Page number
        self.cell(0, 10, '' + str(self.page_no()) + '/{nb}', 0, 0, 'R')

    def add_image(self, image_path, x, y, w, h):
        self.add_page()
        self.image(image_path, x, y, w, h)

    def add_szenario_description(self, description, value):
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'{description}: {value}', 0, 1)
    
    def add_image_with_text(self, image_path, name, text, w, h):
        self.set_font('Arial', '', 8)
        self.write_html(f'<p>{name}<br><br>{text}</p>')
        
        # Überprüfen, ob genügend Platz auf der aktuellen Seite vorhanden ist
        if self.get_y() + h > self.h - self.b_margin:
            self.add_page()
        
        # Berechnen der x-Position, um das Bild zu zentrieren
        x = (self.w - w) / 2
        
        self.image(image_path, x, self.get_y(), w, h)
        self.ln(h + 5)  # Zeilenumbruch nach dem Bild

    def add_table(self, data):
        self.set_font('Arial', '', 12)
        col_width = self.w / 2.5  # Breite der Spalten
        row_height = self.font_size * 1.5  # Höhe der Zeilen

       

        for i, row in enumerate(data):
            if i == 0:
                self.set_font('Arial', 'B', 8)  # Erste Zeile fett
            else:
                self.set_font('Arial', '', 8)  # Andere Zeilen normal
            for item in row:
                self.cell(col_width, row_height, str(item), border=1)
            self.ln(row_height)