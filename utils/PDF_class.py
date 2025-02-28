"""
PDF Class - A utility class for generating PDF reports
This class extends the FPDF library to create customized PDF reports for the Klimaneutral 20245 project.
It provides methods for creating headers, footers, adding images, tables, and formatted text.
The class is designed to maintain consistent styling and layout across all generated PDFs.
"""

from fpdf import FPDF # type: ignore

class PDF(FPDF):
    def header(self):
        """Defines the header that appears on each page of the PDF document."""
        # Logo
        # Calculate the x-position to place the image in the right corner
        image_width = 20
        image_x = self.w - self.r_margin - image_width

        # Set the position of the image and add it
        self.image('assets/business-report.png', image_x, 8, image_width)
        
        # Set font for the title
        self.set_font('Arial', 'B', 15)
        
        # Calculate page width for positioning
        page_width = self.w - 2 * self.l_margin

        # Center the title, adjusting for the logo
        title_width = 100
        title_x = (page_width - title_width)/2 + image_width/2

        # Set position and add the main title
        self.set_x(title_x)
        self.cell(title_width, 10, 'Zusammenfassung', 0, 1, 'C')
        
        # Add subtitle with smaller font
        self.set_font('Arial', '', 8)
        self.cell(0, 10, 'Klimaneutral 20245', 0, 1, 'C')
        
        # Add space after the header
        self.ln(5)

    def footer(self):
        """Defines the footer that appears on each page of the PDF document."""
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', '', 8)
        # Add page number with total pages
        self.cell(0, 10, '' + str(self.page_no()) + '/{nb}', 0, 0, 'R')

    def add_image(self, image_path, x, y, w, h):
        """Adds an image on a new page at the specified position and dimensions."""
        self.add_page()
        self.image(image_path, x, y, w, h)

    def add_szenario_description(self, description, value):
        """Adds a scenario description with its value in a formatted cell."""
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'{description}: {value}', 0, 1)
    
    def add_image_with_text(self, image_path, name, text, w, h):
        """Adds an image with a title and description text, centered on the page.
        Automatically moves to a new page if there's not enough space."""
        # Set font for the text
        self.set_font('Arial', '', 8)
        self.write_html(f'<p>{name}<br><br>{text}</p>')
        
        # Check if there's enough space on the current page
        if self.get_y() + h > self.h - self.b_margin:
            self.add_page()
        
        # Center the image on the page
        x = (self.w - w) / 2
        
        # Add the image and some spacing after it
        self.image(image_path, x, self.get_y(), w, h)
        self.ln(h + 5)  # Line break after the image with extra spacing

    def add_table(self, data):
        """Creates a simple table with the provided data.
        First row is formatted as header (bold)."""
        self.set_font('Arial', '', 12)
        col_width = self.w / 2.5  # Width of columns
        row_height = self.font_size * 1.5  # Height of rows

        # Process each row of data
        for i, row in enumerate(data):
            if i == 0:
                self.set_font('Arial', 'B', 8)  # Format first row as header (bold)
            else:
                self.set_font('Arial', '', 8)  # Format other rows as normal text
                
            # Add each cell in the row
            for item in row:
                self.cell(col_width, row_height, str(item), border=1)
            self.ln(row_height)  # Move to next row