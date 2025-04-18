from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom
from loguru import logger


class SVGManipulator:
    """
    A class to manipulate SVG files - change colors, background, dimensions, etc.
    """
    
    def __init__(self, svg_file_path: Path | None = None, svg_content: str | None = None):
        """
        Initialize with either SVG content as string or a path to an SVG file.
        
        Args:
            svg_content: The SVG content as a string
            svg_file_path: Path to an SVG file
        """
        if svg_content:
            self.svg_content = svg_content
        elif svg_file_path:
            with open(svg_file_path, 'r') as f:
                self.svg_content = f.read()
        else:
            raise ValueError("Either svg_content or svg_file_path must be provided")
            
        # Parse the SVG content
        # Register the SVG namespace
        ET.register_namespace('', "http://www.w3.org/2000/svg")
        self.root = ET.fromstring(self.svg_content)
        self.namespaces = {'svg': 'http://www.w3.org/2000/svg'}
    
    def _get_all_elements_with_color(self) -> list:
        """Get all elements that have color attributes."""
        elements = []
        
        # Find elements with fill attribute (not "none")
        for elem in self.root.findall(".//*[@fill]", self.namespaces):
            if elem.get('fill', 'none').lower() != 'none':
                elements.append(elem)
                
        # Find elements with stroke attribute (not "none")
        for elem in self.root.findall(".//*[@stroke]", self.namespaces):
            if elem.get('stroke', 'none').lower() != 'none':
                elements.append(elem)
        
        return elements
    
    def change_color(
        self, new_color: str, target_color: str | None = None,
        fill: bool=True, fill_if_none: bool=False,
        stroke: bool=True, stroke_if_none: bool=False
        ) -> 'SVGManipulator':
        """Change the color of SVG elements.
        
        Args:
            new_color (str): The new color to apply (hex, rgb, etc.)
            target_color (str, optional): If specified, only elements with this color will be changed. Defaults to None.
            
            fill (bool, optional): If True, will color all not-none fill elements. Defaults to True.
            fill_if_none (bool, optional): If True, will color all fill elements. Defaults to False.
            
            stroke (bool, optional): If True, will color all not-none stroke elements. Defaults to True.
            stroke_if_none (bool, optional): If True, will color all stroke elements. Defaults to False.
        """
        elements = self._get_all_elements_with_color()
        
        for elem in elements:
            # Check for fill color
            if fill or fill_if_none:
                if 'fill' in elem.attrib and (elem.get('fill').lower() != 'none' or fill_if_none):
                    if target_color is None or elem.get('fill') == target_color:
                        elem.set('fill', new_color)
            
            # Check for stroke color
            if stroke or stroke_if_none:
                if 'stroke' in elem.attrib and (elem.get('stroke').lower() != 'none' or stroke_if_none):
                    if target_color is None or elem.get('stroke') == target_color:
                        elem.set('stroke', new_color)
                    
        return self
    
    def add_background(self, bg_color: str) -> 'SVGManipulator':
        """
        Add or change the background of the SVG.
        
        Args:
            bg_color: Background color to apply
        """
        # Check if a rectangle covering the whole SVG already exists
        background_rect = None
        
        # Look for a rectangle with x,y at 0,0 and width,height matching viewBox
        for rect in self.root.findall(".//svg:rect", self.namespaces):
            if (rect.get('x', '0') == '0' and rect.get('y', '0') == '0' and
                    (rect.get('width') == self.root.get('width') or
                     rect.get('width') == self.root.get('viewBox').split()[2])):    # type: ignore
                background_rect = rect
                break
        
        if background_rect is not None:
            # Update existing background
            background_rect.set('fill', bg_color)
        else:
            # Create new background rectangle
            viewBox = self.root.get('viewBox')
            if viewBox:
                _, _, width, height = viewBox.split()
            else:
                width = self.root.get('width', '100%')
                height = self.root.get('height', '100%')
            
            # Create the rectangle element
            rect = ET.Element('{http://www.w3.org/2000/svg}rect')
            rect.set('x', '0')
            rect.set('y', '0')
            rect.set('width', width)
            rect.set('height', height)
            rect.set('fill', bg_color)
            
            # Insert background as the first child to ensure it's at the back
            self.root.insert(0, rect)
            
        return self
    
    def resize(self, width: str | int | float = 'SVGManipulator', 
               height: str | int | float | None=None,
               scale: float | None=None) -> SVGManipulator:
        """
        Resize the SVG.
        
        Args:
            width: New width (can be int for pixels or string for %)
            height: New height (can be int for pixels or string for %)
            scale: Scale factor to multiply both dimensions by
        """
        # Get current dimensions from viewBox or width/height attributes
        viewBox = self.root.get('viewBox')
        if viewBox:
            min_x, min_y, view_width, view_height = map(float, viewBox.split())
        else:
            # Default to whatever width/height are set, or 100% if not set
            view_width = float(self.root.get('width', '100').rstrip('px%'))
            view_height = float(self.root.get('height', '100').rstrip('px%'))
            min_x, min_y = 0, 0
        
        # Calculate new dimensions
        if scale is not None:
            new_width = view_width * scale
            new_height = view_height * scale
        else:
            width = float(width.rstrip('px%')) if isinstance(width, str) else width
            new_width = width if width is not None else view_width
            height = float(height.rstrip('px%')) if isinstance(height, str) else height
            new_height = height if height is not None else view_height
        
        # Update attributes
        if width is not None:
            self.root.set('width', str(width) if isinstance(width, str) else f"{width}px")
        if height is not None:
            self.root.set('height', str(height) if isinstance(height, str) else f"{height}px")
        
        # Update viewBox if it exists
        if viewBox:
            self.root.set('viewBox', f"{min_x} {min_y} {new_width} {new_height}")
            
        return self
    
    def save(self, output_path: str) -> 'SVGManipulator':
        """
        Save the modified SVG to a file.
        
        Args:
            output_path: Path to save the SVG file
        """
        # Get the pretty-printed SVG string
        pretty_svg = self.get_svg_string(pretty=True)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_svg)
            
        return self
    
    def get_svg_string(self, pretty: bool = True) -> str:
        """
        Return the SVG as a string.
        
        Args:
            pretty: Whether to format the SVG with indentation for human readability
            
        Returns:
            The SVG content as a string
        """
        # Convert to string
        rough_string = ET.tostring(self.root, encoding='utf-8').decode('utf-8')
        
        if pretty:
            # Use minidom to format the XML with proper indentation
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            # Clean up extra whitespace that minidom sometimes adds
            pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
            
            # Ensure XML declaration is present
            if not pretty_xml.startswith('<?xml'):
                pretty_xml = '<?xml version="1.0" encoding="utf-8"?>\n' + pretty_xml
                
            return pretty_xml
        else:
            # Just ensure XML declaration
            if not rough_string.startswith('<?xml'):
                rough_string = '<?xml version="1.0" encoding="utf-8"?>\n' + rough_string
                
            return rough_string
    
    def simplify(self) -> 'SVGManipulator':
        """Simplify the SVG by removing unnecessary attributes and metadata."""
        # This method requires lxml to work fully with comments and metadata
        try:
            from lxml import etree

            # Convert ElementTree to lxml tree for better handling
            xml_string = ET.tostring(self.root)
            lxml_tree = etree.fromstring(xml_string)
            
            # Remove metadata
            for metadata in lxml_tree.xpath("//svg:metadata", namespaces=self.namespaces):
                metadata.getparent().remove(metadata)
                
            # Remove comments
            for comment in lxml_tree.xpath("//comment()"):
                comment.getparent().remove(comment)
            
            # Remove unnecessary attributes
            unnecessary_attrs = ['id', 'data-name', 'class']
            for elem in lxml_tree.iter():
                for attr in unnecessary_attrs:
                    if attr in elem.attrib:
                        del elem.attrib[attr]
            
            # Convert back to string and parse with ElementTree
            clean_xml = etree.tostring(lxml_tree)
            self.root = ET.fromstring(clean_xml)
            
        except ImportError:
            # Fallback for when lxml is not available
            # This won't be able to handle comments, but can still remove attributes
            
            # Remove unnecessary attributes
            unnecessary_attrs = ['id', 'data-name', 'class']
            for elem in self.root.iter():
                for attr in unnecessary_attrs:
                    if attr in elem.attrib:
                        del elem.attrib[attr]
            
            logger.warning("lxml not available. Limited simplification applied.")
            
        return self