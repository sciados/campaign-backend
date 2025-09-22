# =====================================
# File: src/intelligence/services/pdf_report_service.py
# =====================================

"""
PDF Report Generation Service for Intelligence Analytics

Generates comprehensive PDF reports containing intelligence insights,
marketing strategies, and actionable recommendations for campaigns.
"""

import io
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

logger = logging.getLogger(__name__)


class PDFReportService:
    """Service for generating comprehensive PDF reports from intelligence data"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""

        # Brand colors
        self.brand_primary = HexColor('#3B82F6')  # Blue
        self.brand_secondary = HexColor('#8B5CF6')  # Purple
        self.brand_success = HexColor('#10B981')  # Green
        self.brand_warning = HexColor('#F59E0B')  # Amber
        self.brand_danger = HexColor('#EF4444')  # Red

        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=self.brand_primary,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=self.brand_primary,
            keepWithNext=True
        ))

        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15,
            textColor=self.brand_secondary,
            keepWithNext=True
        ))

        self.styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=20,
            rightIndent=20,
            backgroundColor=HexColor('#F8FAFC'),
            borderPadding=10
        ))

        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leftIndent=10,
            rightIndent=10
        ))

    async def generate_intelligence_report(
        self,
        campaign_id: str,
        intelligence_data: Dict[str, Any],
        include_sections: List[str],
        format: str = 'pdf'
    ) -> bytes:
        """
        Generate a comprehensive PDF report from intelligence data

        Args:
            campaign_id: Campaign identifier
            intelligence_data: Intelligence analysis results
            include_sections: List of sections to include in report
            format: Output format (currently only 'pdf' supported)

        Returns:
            PDF bytes
        """
        try:
            logger.info(f"Generating PDF report for campaign {campaign_id}")

            # Create PDF document
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            # Build content
            story = []

            # Title page
            story.extend(self._create_title_page(campaign_id, intelligence_data))
            story.append(PageBreak())

            # Table of contents placeholder
            story.append(Paragraph("Table of Contents", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            story.append(PageBreak())

            # Generate sections based on include_sections
            for section in include_sections:
                section_content = self._generate_section(section, intelligence_data)
                if section_content:
                    story.extend(section_content)
                    story.append(PageBreak())

            # Build PDF
            doc.build(story)

            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"PDF report generated successfully: {len(pdf_bytes)} bytes")
            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF report generation failed: {e}")
            raise Exception(f"Failed to generate PDF report: {str(e)}")

    def _create_title_page(self, campaign_id: str, intelligence_data: Dict[str, Any]) -> List:
        """Create the title page content"""
        content = []

        # Main title
        content.append(Paragraph("Intelligence Analysis Report", self.styles['CustomTitle']))
        content.append(Spacer(1, 30))

        # Campaign info
        campaign_name = intelligence_data.get('campaign_name', f'Campaign {campaign_id}')
        content.append(Paragraph(f"<b>Campaign:</b> {campaign_name}", self.styles['ExecutiveSummary']))
        content.append(Spacer(1, 10))

        # URL analyzed
        url = intelligence_data.get('salespage_url', 'N/A')
        content.append(Paragraph(f"<b>Sales Page URL:</b> {url}", self.styles['ExecutiveSummary']))
        content.append(Spacer(1, 10))

        # Generation date
        content.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['ExecutiveSummary']))
        content.append(Spacer(1, 40))

        # Executive summary box
        summary = intelligence_data.get('executive_summary', 'No executive summary available.')
        content.append(Paragraph("<b>Executive Summary</b>", self.styles['SectionHeader']))
        content.append(Paragraph(summary, self.styles['HighlightBox']))

        return content

    def _generate_section(self, section_name: str, intelligence_data: Dict[str, Any]) -> List:
        """Generate content for a specific section"""

        section_generators = {
            'executive_summary': self._generate_executive_summary,
            'product_analysis': self._generate_product_analysis,
            'target_audience': self._generate_target_audience,
            'competition_analysis': self._generate_competition_analysis,
            'marketing_strategy': self._generate_marketing_strategy,
            'content_recommendations': self._generate_content_recommendations,
            'sales_psychology': self._generate_sales_psychology,
            'conversion_opportunities': self._generate_conversion_opportunities,
            'actionable_insights': self._generate_actionable_insights
        }

        generator = section_generators.get(section_name)
        if generator:
            return generator(intelligence_data)
        else:
            logger.warning(f"Unknown section: {section_name}")
            return []

    def _generate_executive_summary(self, data: Dict[str, Any]) -> List:
        """Generate executive summary section"""
        content = []
        content.append(Paragraph("Executive Summary", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        summary = data.get('executive_summary', 'No executive summary available.')
        content.append(Paragraph(summary, self.styles['ExecutiveSummary']))
        content.append(Spacer(1, 20))

        # Key metrics if available
        if 'confidence_score' in data:
            content.append(Paragraph("Analysis Confidence", self.styles['SubsectionHeader']))
            confidence = data.get('confidence_score', 0)
            content.append(Paragraph(f"Analysis Confidence Score: {confidence:.1%}", self.styles['Normal']))
            content.append(Spacer(1, 10))

        return content

    def _generate_product_analysis(self, data: Dict[str, Any]) -> List:
        """Generate product analysis section"""
        content = []
        content.append(Paragraph("Product Analysis", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        # Product information
        product_info = data.get('product_information', {})
        if product_info:
            content.append(Paragraph("Product Overview", self.styles['SectionHeader']))

            # Product name
            if 'product_name' in product_info:
                content.append(Paragraph(f"<b>Product Name:</b> {product_info['product_name']}", self.styles['Normal']))

            # Description
            if 'description' in product_info:
                content.append(Paragraph(f"<b>Description:</b> {product_info['description']}", self.styles['Normal']))

            # Price
            if 'price' in product_info:
                content.append(Paragraph(f"<b>Price:</b> {product_info['price']}", self.styles['Normal']))

            # Category
            if 'category' in product_info:
                content.append(Paragraph(f"<b>Category:</b> {product_info['category']}", self.styles['Normal']))

            content.append(Spacer(1, 15))

        # Features and benefits
        features = data.get('features', [])
        if features:
            content.append(Paragraph("Key Features & Benefits", self.styles['SectionHeader']))
            for i, feature in enumerate(features[:10], 1):  # Limit to top 10
                content.append(Paragraph(f"{i}. {feature}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        return content

    def _generate_target_audience(self, data: Dict[str, Any]) -> List:
        """Generate target audience section"""
        content = []
        content.append(Paragraph("Target Audience Analysis", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        audience_data = data.get('target_audience', {})
        if audience_data:

            # Demographics
            demographics = audience_data.get('demographics', {})
            if demographics:
                content.append(Paragraph("Demographics", self.styles['SectionHeader']))
                for key, value in demographics.items():
                    if value:
                        content.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", self.styles['Normal']))
                content.append(Spacer(1, 15))

            # Pain points
            pain_points = audience_data.get('pain_points', [])
            if pain_points:
                content.append(Paragraph("Pain Points", self.styles['SectionHeader']))
                for i, pain_point in enumerate(pain_points[:8], 1):
                    content.append(Paragraph(f"{i}. {pain_point}", self.styles['Normal']))
                content.append(Spacer(1, 15))

            # Interests
            interests = audience_data.get('interests', [])
            if interests:
                content.append(Paragraph("Interests & Behaviors", self.styles['SectionHeader']))
                for i, interest in enumerate(interests[:8], 1):
                    content.append(Paragraph(f"{i}. {interest}", self.styles['Normal']))
                content.append(Spacer(1, 15))

        return content

    def _generate_competition_analysis(self, data: Dict[str, Any]) -> List:
        """Generate competition analysis section"""
        content = []
        content.append(Paragraph("Competition Analysis", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        competitors = data.get('competitors', [])
        if competitors:
            content.append(Paragraph("Key Competitors", self.styles['SectionHeader']))

            for i, competitor in enumerate(competitors[:5], 1):  # Top 5 competitors
                content.append(Paragraph(f"<b>Competitor {i}:</b> {competitor.get('name', 'Unknown')}", self.styles['SubsectionHeader']))

                if 'strengths' in competitor:
                    content.append(Paragraph(f"<b>Strengths:</b> {competitor['strengths']}", self.styles['Normal']))

                if 'weaknesses' in competitor:
                    content.append(Paragraph(f"<b>Weaknesses:</b> {competitor['weaknesses']}", self.styles['Normal']))

                content.append(Spacer(1, 10))

        return content

    def _generate_marketing_strategy(self, data: Dict[str, Any]) -> List:
        """Generate marketing strategy section"""
        content = []
        content.append(Paragraph("Marketing Strategy Recommendations", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        # Marketing angles
        angles = data.get('marketing_angles', [])
        if angles:
            content.append(Paragraph("Recommended Marketing Angles", self.styles['SectionHeader']))
            for i, angle in enumerate(angles[:6], 1):
                content.append(Paragraph(f"{i}. {angle}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Platforms
        platforms = data.get('recommended_platforms', [])
        if platforms:
            content.append(Paragraph("Recommended Platforms", self.styles['SectionHeader']))
            for i, platform in enumerate(platforms[:8], 1):
                content.append(Paragraph(f"{i}. {platform}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Content themes
        themes = data.get('content_themes', [])
        if themes:
            content.append(Paragraph("Content Themes", self.styles['SectionHeader']))
            for i, theme in enumerate(themes[:6], 1):
                content.append(Paragraph(f"{i}. {theme}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        return content

    def _generate_content_recommendations(self, data: Dict[str, Any]) -> List:
        """Generate content recommendations section"""
        content = []
        content.append(Paragraph("Content Recommendations", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        # Content types
        content_types = data.get('recommended_content_types', [])
        if content_types:
            content.append(Paragraph("Recommended Content Types", self.styles['SectionHeader']))
            for i, content_type in enumerate(content_types[:8], 1):
                content.append(Paragraph(f"{i}. {content_type}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Key messages
        messages = data.get('key_messages', [])
        if messages:
            content.append(Paragraph("Key Messages to Emphasize", self.styles['SectionHeader']))
            for i, message in enumerate(messages[:6], 1):
                content.append(Paragraph(f"{i}. {message}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Call-to-action recommendations
        cta_recommendations = data.get('cta_recommendations', [])
        if cta_recommendations:
            content.append(Paragraph("Call-to-Action Recommendations", self.styles['SectionHeader']))
            for i, cta in enumerate(cta_recommendations[:5], 1):
                content.append(Paragraph(f"{i}. {cta}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        return content

    def _generate_sales_psychology(self, data: Dict[str, Any]) -> List:
        """Generate sales psychology section"""
        content = []
        content.append(Paragraph("Sales Psychology Insights", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        # Psychological triggers
        triggers = data.get('psychological_triggers', [])
        if triggers:
            content.append(Paragraph("Psychological Triggers to Leverage", self.styles['SectionHeader']))
            for i, trigger in enumerate(triggers[:8], 1):
                content.append(Paragraph(f"{i}. {trigger}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Emotional appeals
        appeals = data.get('emotional_appeals', [])
        if appeals:
            content.append(Paragraph("Emotional Appeals", self.styles['SectionHeader']))
            for i, appeal in enumerate(appeals[:6], 1):
                content.append(Paragraph(f"{i}. {appeal}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Objection handling
        objections = data.get('common_objections', [])
        if objections:
            content.append(Paragraph("Common Objections & How to Address Them", self.styles['SectionHeader']))
            for i, objection in enumerate(objections[:5], 1):
                content.append(Paragraph(f"{i}. {objection}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        return content

    def _generate_conversion_opportunities(self, data: Dict[str, Any]) -> List:
        """Generate conversion opportunities section"""
        content = []
        content.append(Paragraph("Conversion Opportunities", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        # Optimization opportunities
        optimizations = data.get('optimization_opportunities', [])
        if optimizations:
            content.append(Paragraph("Conversion Optimization Opportunities", self.styles['SectionHeader']))
            for i, opportunity in enumerate(optimizations[:8], 1):
                content.append(Paragraph(f"{i}. {opportunity}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Traffic strategies
        traffic_strategies = data.get('traffic_strategies', [])
        if traffic_strategies:
            content.append(Paragraph("Traffic Generation Strategies", self.styles['SectionHeader']))
            for i, strategy in enumerate(traffic_strategies[:6], 1):
                content.append(Paragraph(f"{i}. {strategy}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        return content

    def _generate_actionable_insights(self, data: Dict[str, Any]) -> List:
        """Generate actionable insights section"""
        content = []
        content.append(Paragraph("Actionable Insights & Next Steps", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))

        # Immediate actions
        immediate_actions = data.get('immediate_actions', [])
        if immediate_actions:
            content.append(Paragraph("Immediate Actions (Next 7 Days)", self.styles['SectionHeader']))
            for i, action in enumerate(immediate_actions[:5], 1):
                content.append(Paragraph(f"{i}. {action}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Short-term strategy
        short_term = data.get('short_term_strategy', [])
        if short_term:
            content.append(Paragraph("Short-Term Strategy (Next 30 Days)", self.styles['SectionHeader']))
            for i, strategy in enumerate(short_term[:5], 1):
                content.append(Paragraph(f"{i}. {strategy}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Long-term recommendations
        long_term = data.get('long_term_recommendations', [])
        if long_term:
            content.append(Paragraph("Long-Term Recommendations (Next 3 Months)", self.styles['SectionHeader']))
            for i, recommendation in enumerate(long_term[:5], 1):
                content.append(Paragraph(f"{i}. {recommendation}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        # Success metrics
        success_metrics = data.get('success_metrics', [])
        if success_metrics:
            content.append(Paragraph("Success Metrics to Track", self.styles['SectionHeader']))
            for i, metric in enumerate(success_metrics[:6], 1):
                content.append(Paragraph(f"{i}. {metric}", self.styles['Normal']))
            content.append(Spacer(1, 15))

        return content


# Service instance
pdf_report_service = PDFReportService()