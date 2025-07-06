import re
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from helper import check_and_fix_contrast, calculate_contrast_ratio, get_contrast_level, calculate_delta_e_2000
from processor import process_config

# PDF generation imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, white, red, green, blue
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.graphics.shapes import Drawing, Rect
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: ReportLab not installed. PDF reports will not be available.")
    print("Install with: pip install reportlab")

class AccessibleColorProcessor:
    def __init__(self, css_file_path: str = "cm-vars.css", report_dir: str = "reports"):
        self.css_file_path = css_file_path
        self.report_dir = report_dir
        self.processed_results = []
        
        # Create reports directory if it doesn't exist
        os.makedirs(report_dir, exist_ok=True)
        
    def process_brand_palette(self, config) -> List[Dict]:
        """
        Main function: Process brand palette and generate accessible colors
        Returns processed palette with accessibility improvements
        """
        color_scheme = process_config(config)
        processed_palette = []
        
        for i, color_pair in enumerate(color_scheme):
            try:
                # Extract color information
                text_color = self._parse_color(color_pair['text']['color'])
                bg_color = self._parse_color(color_pair['bg']['color'])
                text_type = color_pair.get('type', 'normal')
                is_large = text_type == 'large'
                
                # Get original contrast info
                original_contrast = calculate_contrast_ratio(text_color, bg_color)
                original_level = get_contrast_level(original_contrast, is_large)
                
                # Generate accessible colors using our rigorous helper
                accessible_text, accessible_bg = check_and_fix_contrast(
                    text_color, bg_color, is_large
                )
                
                # Calculate improvement metrics
                new_contrast = calculate_contrast_ratio(accessible_text, accessible_bg)
                new_level = get_contrast_level(new_contrast, is_large)
                delta_e = calculate_delta_e_2000(text_color, accessible_text)
                
                # Determine which CSS variable to use
                text_var = color_pair['text'].get('custom') or color_pair['text']['default']
                bg_var = color_pair['bg'].get('custom') or color_pair['bg']['default']
                
                # Create processed result
                processed_result = {
                    'index': i,
                    'original': {
                        'text': text_color,
                        'bg': bg_color,
                        'contrast': original_contrast,
                        'level': original_level
                    },
                    'accessible': {
                        'text': accessible_text,
                        'bg': accessible_bg,
                        'contrast': new_contrast,
                        'level': new_level
                    },
                    'metrics': {
                        'delta_e': delta_e,
                        'contrast_improvement': new_contrast - original_contrast,
                        'level_improved': original_level != new_level and new_level != 'FAIL',
                        'brand_preservation': 'Excellent' if delta_e <= 2.0 else 'Good' if delta_e <= 3.0 else 'Fair'
                    },
                    'css_vars': {
                        'text': text_var,
                        'bg': bg_var
                    },
                    'type': text_type
                }
                
                processed_palette.append(processed_result)
                
            except Exception as e:
                print(f"Error processing color pair {i}: {e}")
                continue
        
        self.processed_results = processed_palette
        return processed_palette
    
    def generate_accessible_css(self, processed_palette: List[Dict]) -> str:
        """
        Generate CSS with accessible color variables
        """
        css_rules = []
        
        # Generate .color-scheme class with all accessible colors
        css_rules.append(".color-scheme {")
        
        for result in processed_palette:
            text_color = result['accessible']['text']
            bg_color = result['accessible']['bg']
            text_var = result['css_vars']['text']
            bg_var = result['css_vars']['bg']
            
            # Convert RGB tuples to CSS format
            text_css = f"rgb({text_color[0]}, {text_color[1]}, {text_color[2]})"
            bg_css = f"rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]})"
            
            css_rules.append(f"  {text_var}: {text_css};")
            css_rules.append(f"  {bg_var}: {bg_css};")
        
        css_rules.append("}")
        
        return "\n".join(css_rules)
    
    def update_css_file(self, processed_palette: List[Dict]) -> bool:
        """
        Update cm-vars.css file with accessible colors
        Only touches .color-scheme class, preserves everything else
        """
        try:
            # Read existing CSS file
            css_content = ""
            try:
                with open(self.css_file_path, 'r', encoding='utf-8') as file:
                    css_content = file.read()
            except FileNotFoundError:
                print(f"Creating new CSS file: {self.css_file_path}")
                css_content = ""
            
            # Generate new .color-scheme CSS
            new_color_scheme = self.generate_accessible_css(processed_palette)
            
            # Pattern to match .color-scheme class (including nested braces)
            color_scheme_pattern = r'\.color-scheme\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            
            # Check if .color-scheme already exists
            if re.search(color_scheme_pattern, css_content, re.DOTALL):
                # Replace existing .color-scheme
                updated_content = re.sub(
                    color_scheme_pattern, 
                    new_color_scheme, 
                    css_content, 
                    flags=re.DOTALL
                )
            else:
                # Add new .color-scheme at the end
                if css_content and not css_content.endswith('\n'):
                    css_content += '\n'
                updated_content = css_content + '\n' + new_color_scheme + '\n'
            
            # Write updated CSS back to file
            with open(self.css_file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            return True
            
        except Exception as e:
            print(f"Error updating CSS file: {e}")
            return False
    
    def generate_pdf_report(self, processed_palette: List[Dict]) -> str:
        """
        Generate comprehensive PDF accessibility report
        """
        if not REPORTLAB_AVAILABLE:
            print("ReportLab not available. Generating text report instead.")
            return self._generate_text_report(processed_palette)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"color_contrast_accessibility_report_{timestamp}.pdf"
        pdf_path = os.path.join(self.report_dir, pdf_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceBefore=20,
            spaceAfter=10
        )
        
        # Title page
        story.append(Paragraph("Accessibility Report", title_style))
        story.append(Paragraph("Color Palette Analysis & Optimization", styles['Heading3']))
        story.append(Spacer(1, 30))
        
        # Add timestamp and summary
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"CSS File: {self.css_file_path}", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
        
        total_pairs = len(processed_palette)
        improved_pairs = sum(1 for r in processed_palette if r['metrics']['level_improved'])
        avg_delta_e = sum(r['metrics']['delta_e'] for r in processed_palette) / total_pairs if total_pairs > 0 else 0
        
        # Summary statistics table
        summary_data = [
            ['Metric', 'Value', 'Assessment'],
            ['Total Color Pairs', str(total_pairs), 'Processed'],
            ['Improved Accessibility', f"{improved_pairs}/{total_pairs}", 'Enhanced' if improved_pairs > 0 else 'Maintained'],
            ['Average Delta E', f"{avg_delta_e:.2f}", 'Excellent' if avg_delta_e <= 2.0 else 'Good' if avg_delta_e <= 3.0 else 'Fair'],
            ['Brand Preservation', f"{((total_pairs - improved_pairs) / total_pairs * 100):.1f}%", 'High' if avg_delta_e <= 2.0 else 'Medium']
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Detailed Analysis
        story.append(Paragraph("Detailed Color Analysis", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
        
        for i, result in enumerate(processed_palette):
            # Color pair header
            story.append(Paragraph(f"Color Pair {i + 1} - {result['type'].title()} Text", styles['Heading3']))
            
            # Create color swatches and details table
            detail_data = [
                ['Property', 'Original', 'Accessible', 'Improvement'],
                ['Text Color', self._rgb_to_hex(result['original']['text']), self._rgb_to_hex(result['accessible']['text']), ''],
                ['Background Color', self._rgb_to_hex(result['original']['bg']), self._rgb_to_hex(result['accessible']['bg']), ''],
                ['Contrast Ratio', f"{result['original']['contrast']:.2f}", f"{result['accessible']['contrast']:.2f}", f"+{result['metrics']['contrast_improvement']:.2f}"],
                ['WCAG Level', result['original']['level'], result['accessible']['level'], '✓' if result['metrics']['level_improved'] else '='],
                ['Delta E (Brand Impact)', '-', f"{result['metrics']['delta_e']:.2f}", result['metrics']['brand_preservation']],
                ['CSS Variables', f"{result['css_vars']['text']}\n{result['css_vars']['bg']}", '', '']
            ]
            
            detail_table = Table(detail_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            
            story.append(detail_table)
            story.append(Spacer(1, 20))
        
        # Recommendations section
        story.append(PageBreak())
        story.append(Paragraph("Recommendations", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
        
        recommendations = self._generate_recommendations(processed_palette)
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Technical details
        story.append(Paragraph("Technical Implementation", heading_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
        
        tech_details = [
            "Color difference calculated using CIE Delta E 2000 formula",
            "Contrast ratios calculated according to WCAG 2.1 standards",
            "OKLCH color space used for perceptually uniform adjustments",
            "Brand preservation prioritized with Delta E ≤ 2.0 target",
            "Hierarchical adjustment: Lightness → Chroma → Hue"
        ]
        
        for detail in tech_details:
            story.append(Paragraph(f"• {detail}", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 50))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        story.append(Paragraph("Generated by CM-Colors - Accessible Color Management System", 
                               ParagraphStyle('Footer', parent=styles['Normal'], 
                                            fontSize=8, textColor=colors.grey, 
                                            alignment=TA_CENTER)))
        
        # Build PDF
        doc.build(story)
        
        return pdf_path
    
    def _generate_text_report(self, processed_palette: List[Dict]) -> str:
        """
        Fallback text report when PDF is not available
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_filename = f"accessibility_report_{timestamp}.txt"
        txt_path = os.path.join(self.report_dir, txt_filename)
        
        report = []
        report.append("=" * 60)
        report.append("ACCESSIBILITY REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"CSS File: {self.css_file_path}")
        report.append("")
        
        # Summary
        total_pairs = len(processed_palette)
        improved_pairs = sum(1 for r in processed_palette if r['metrics']['level_improved'])
        avg_delta_e = sum(r['metrics']['delta_e'] for r in processed_palette) / total_pairs if total_pairs > 0 else 0
        
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 20)
        report.append(f"Total color pairs processed: {total_pairs}")
        report.append(f"Pairs with improved accessibility: {improved_pairs}")
        report.append(f"Average brand preservation (Delta E): {avg_delta_e:.2f}")
        report.append(f"Brand preservation quality: {'Excellent' if avg_delta_e <= 2.0 else 'Good' if avg_delta_e <= 3.0 else 'Fair'}")
        report.append("")
        
        # Detailed results
        for i, result in enumerate(processed_palette):
            report.append(f"COLOR PAIR {i + 1} - {result['type'].upper()} TEXT")
            report.append("-" * 40)
            report.append(f"Original: {result['original']['text']} on {result['original']['bg']}")
            report.append(f"Accessible: {result['accessible']['text']} on {result['accessible']['bg']}")
            report.append(f"Contrast: {result['original']['contrast']:.2f} → {result['accessible']['contrast']:.2f}")
            report.append(f"WCAG Level: {result['original']['level']} → {result['accessible']['level']}")
            report.append(f"Brand Impact (Delta E): {result['metrics']['delta_e']:.2f} ({result['metrics']['brand_preservation']})")
            report.append(f"CSS Variables: {result['css_vars']['text']}, {result['css_vars']['bg']}")
            report.append("")
        
        # Write to file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        return txt_path
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _generate_recommendations(self, processed_palette: List[Dict]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check for high Delta E values
        high_delta_e = [r for r in processed_palette if r['metrics']['delta_e'] > 3.0]
        if high_delta_e:
            recommendations.append(f"Consider reviewing {len(high_delta_e)} color pairs with high brand impact (Delta E > 3.0)")
        
        # Check for accessibility improvements
        improved = [r for r in processed_palette if r['metrics']['level_improved']]
        if improved:
            recommendations.append(f"Excellent! {len(improved)} color pairs achieved better accessibility levels")
        
        # Check for failed accessibility
        failed = [r for r in processed_palette if r['accessible']['level'] == 'FAIL']
        if failed:
            recommendations.append(f"Warning: {len(failed)} color pairs still don't meet minimum accessibility standards")
        
        # General recommendations
        recommendations.append("Test the new color scheme with actual users for usability validation")
        recommendations.append("Consider implementing these changes gradually in your design system")
        recommendations.append("Monitor brand perception after implementing accessibility improvements")
        
        return recommendations
    
    def _parse_color(self, color_value) -> Tuple[int, int, int]:
        """
        Parse color value to RGB tuple
        Supports various formats: (r,g,b), [r,g,b], "rgb(r,g,b)", "#hex"
        """
        if isinstance(color_value, (tuple, list)) and len(color_value) == 3:

            return (int(color_value[0]), int(color_value[1]), int(color_value[2]))
        
        if isinstance(color_value, str):
            # Handle hex colors
            if color_value.startswith('#'):
                hex_color = color_value[1:]
                if len(hex_color) == 6:
                    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
                    return (r, g, b)
                elif len(hex_color) == 3:
                    r = int(hex_color[0]*2, 16)
                    g = int(hex_color[1]*2, 16)
                    b = int(hex_color[2]*2, 16)
                    return (r, g, b)
            
            # Handle rgb() format
            if color_value.startswith('rgb('):
                rgb_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_value)
                if rgb_match:
                    r, g, b = [int(rgb_match.group(i)) for i in (1, 2, 3)]
                    return (r, g, b)
        
        raise ValueError(f"Invalid color format: {color_value}")

# Main processing function
def process_brand_palette(config_path, css_file_path: str = "cm-vars.css", 
                         report_dir: str = "reports",with_report=False) -> Dict:
    """
    Main function to process brand palette and generate accessible CSS with PDF report
    
    Args:
        config_path: Config path for css variables config
        css_file_path: Path to CSS file to update
        report_dir: Directory to save PDF report
        with_report: Flag to indicate if report generation is required

    Returns:
        Dictionary with processed results, CSS content, and report path
    """
    processor = AccessibleColorProcessor(css_file_path, report_dir)
    
    # Process the palette
    processed_palette = processor.process_brand_palette(config_path)

    # Update CSS file
    css_updated = processor.update_css_file(processed_palette)
    
    # Generate PDF report
    report_path = processor.generate_pdf_report(processed_palette) if with_report else None
    
    if report_path:
        return {
        'processed_palette': processed_palette,
        'css_updated': css_updated,
        'css_content': processor.generate_accessible_css(processed_palette),
        'report_path': report_path,
        'summary': {
            'total_pairs': len(processed_palette),
            'improved_pairs': sum(1 for r in processed_palette if r['metrics']['level_improved']),
            'avg_delta_e': sum(r['metrics']['delta_e'] for r in processed_palette) / len(processed_palette) if processed_palette else 0
        }
    }
    else:
            return {
        'processed_palette': processed_palette,
        'css_updated': css_updated,
        'css_content': processor.generate_accessible_css(processed_palette),
        'summary': {
            'total_pairs': len(processed_palette),
            'improved_pairs': sum(1 for r in processed_palette if r['metrics']['level_improved']),
            'avg_delta_e': sum(r['metrics']['delta_e'] for r in processed_palette) / len(processed_palette) if processed_palette else 0
        }
    }
