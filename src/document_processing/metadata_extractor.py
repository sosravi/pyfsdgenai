"""
Metadata Extractor

This module implements the MetadataExtractor class for extracting structured
metadata from document text content.
"""

import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extracts structured metadata from document text content."""
    
    def __init__(self):
        """Initialize MetadataExtractor with extraction patterns."""
        self.extraction_patterns = {
            "contract_id": [
                r'contract[:\s]*id[:\s]*([A-Za-z0-9\-_]+)',
                r'agreement[:\s]*id[:\s]*([A-Za-z0-9\-_]+)',
                r'document[:\s]*id[:\s]*([A-Za-z0-9\-_]+)',
            ],
            "effective_date": [
                r'effective[:\s]*date[:\s]*([A-Za-z0-9\s\-\/]+)',
                r'start[:\s]*date[:\s]*([A-Za-z0-9\s\-\/]+)',
                r'commencement[:\s]*date[:\s]*([A-Za-z0-9\s\-\/]+)',
            ],
            "expiration_date": [
                r'expiration[:\s]*date[:\s]*([A-Za-z0-9\s\-\/]+)',
                r'end[:\s]*date[:\s]*([A-Za-z0-9\s\-\/]+)',
                r'termination[:\s]*date[:\s]*([A-Za-z0-9\s\-\/]+)',
            ],
            "parties": [
                r'parties?[:\s]*([^\n]+)',
                r'between[:\s]*([^\n]+)',
                r'company[:\s]*([^\n]+)',
            ],
            "value": [
                r'value[:\s]*\$?([\d,]+\.?\d*)',
                r'amount[:\s]*\$?([\d,]+\.?\d*)',
                r'total[:\s]*\$?([\d,]+\.?\d*)',
                r'price[:\s]*\$?([\d,]+\.?\d*)',
            ],
            "currency": [
                r'currency[:\s]*([A-Z]{3})',
                r'\$([\d,]+\.?\d*)\s*(USD|usd)',
                r'([A-Z]{3})\s*[\d,]+\.?\d*',
            ]
        }
        
        logger.info("MetadataExtractor initialized")
    
    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract basic metadata from document text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dict containing extracted metadata
        """
        try:
            if not text or not text.strip():
                return {"success": True}
            
            metadata = {"success": True}
            
            # Extract contract ID
            contract_id = self._extract_pattern(text, self.extraction_patterns["contract_id"])
            if contract_id:
                metadata["contract_id"] = contract_id.strip()
            
            # Extract effective date
            effective_date = self._extract_pattern(text, self.extraction_patterns["effective_date"])
            if effective_date:
                metadata["effective_date"] = self._parse_date(effective_date.strip())
            
            # Extract expiration date
            expiration_date = self._extract_pattern(text, self.extraction_patterns["expiration_date"])
            if expiration_date:
                metadata["expiration_date"] = self._parse_date(expiration_date.strip())
            
            # Extract parties
            parties = self._extract_pattern(text, self.extraction_patterns["parties"])
            if parties:
                metadata["parties"] = self._parse_parties(parties.strip())
            
            # Extract value
            value = self._extract_pattern(text, self.extraction_patterns["value"])
            if value:
                metadata["value"] = self._parse_decimal(value.strip())
            
            # Extract currency
            currency = self._extract_pattern(text, self.extraction_patterns["currency"])
            if currency:
                metadata["currency"] = currency.strip().upper()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to extract metadata: {str(e)}"
            }
    
    def extract_pricing_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract pricing-specific metadata from document text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dict containing pricing metadata
        """
        try:
            if not text or not text.strip():
                return {"success": True}
            
            metadata = {"success": True}
            
            # Extract base price
            base_price_patterns = [
                r'base[:\s]*price[:\s]*\$?([\d,]+\.?\d*)',
                r'unit[:\s]*price[:\s]*\$?([\d,]+\.?\d*)',
                r'rate[:\s]*\$?([\d,]+\.?\d*)',
            ]
            base_price = self._extract_pattern(text, base_price_patterns)
            if base_price:
                metadata["base_price"] = self._parse_decimal(base_price.strip())
            
            # Extract volume discount
            discount_patterns = [
                r'volume[:\s]*discount[:\s]*(\d+\.?\d*)\s*%',
                r'discount[:\s]*(\d+\.?\d*)\s*%',
                r'reduction[:\s]*(\d+\.?\d*)\s*%',
            ]
            discount = self._extract_pattern(text, discount_patterns)
            if discount:
                metadata["volume_discount"] = self._parse_decimal(discount.strip())
            
            # Extract payment terms
            payment_patterns = [
                r'payment[:\s]*terms?[:\s]*([^\n]+)',
                r'terms?[:\s]*([^\n]*net[^\n]*)',
                r'net[:\s]*(\d+)[:\s]*days?',
            ]
            payment_terms = self._extract_pattern(text, payment_patterns)
            if payment_terms:
                metadata["payment_terms"] = payment_terms.strip()
            
            # Extract late payment fee
            late_fee_patterns = [
                r'late[:\s]*payment[:\s]*fee[:\s]*(\d+\.?\d*)\s*%',
                r'penalty[:\s]*(\d+\.?\d*)\s*%',
                r'interest[:\s]*(\d+\.?\d*)\s*%',
            ]
            late_fee = self._extract_pattern(text, late_fee_patterns)
            if late_fee:
                metadata["late_payment_fee"] = self._parse_decimal(late_fee.strip())
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting pricing metadata: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to extract pricing metadata: {str(e)}"
            }
    
    def extract_terms_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract terms and conditions metadata from document text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dict containing terms metadata
        """
        try:
            if not text or not text.strip():
                return {"success": True}
            
            metadata = {"success": True}
            
            # Extract termination clause
            termination_patterns = [
                r'termination[:\s]*([^\n]+)',
                r'terminate[:\s]*([^\n]+)',
                r'notice[:\s]*([^\n]+)',
            ]
            termination = self._extract_pattern(text, termination_patterns)
            if termination:
                metadata["termination_clause"] = termination.strip()
            
            # Extract liability limit
            liability_patterns = [
                r'liability[:\s]*limit[:\s]*\$?([\d,]+\.?\d*)',
                r'liability[:\s]*\$?([\d,]+\.?\d*)',
                r'limit[:\s]*\$?([\d,]+\.?\d*)',
            ]
            liability = self._extract_pattern(text, liability_patterns)
            if liability:
                metadata["liability_limit"] = self._parse_decimal(liability.strip())
            
            # Extract force majeure
            force_majeure_patterns = [
                r'force[:\s]*majeure[:\s]*([^\n]+)',
                r'act[:\s]*of[:\s]*god[:\s]*([^\n]+)',
                r'circumstances[:\s]*([^\n]+)',
            ]
            force_majeure = self._extract_pattern(text, force_majeure_patterns)
            if force_majeure:
                metadata["force_majeure"] = force_majeure.strip()
            
            # Extract governing law
            governing_law_patterns = [
                r'governing[:\s]*law[:\s]*([^\n]+)',
                r'law[:\s]*of[:\s]*([^\n]+)',
                r'jurisdiction[:\s]*([^\n]+)',
            ]
            governing_law = self._extract_pattern(text, governing_law_patterns)
            if governing_law:
                metadata["governing_law"] = governing_law.strip()
            
            # Extract dispute resolution
            dispute_patterns = [
                r'dispute[:\s]*resolution[:\s]*([^\n]+)',
                r'arbitration[:\s]*([^\n]+)',
                r'mediation[:\s]*([^\n]+)',
            ]
            dispute_resolution = self._extract_pattern(text, dispute_patterns)
            if dispute_resolution:
                metadata["dispute_resolution"] = dispute_resolution.strip()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting terms metadata: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to extract terms metadata: {str(e)}"
            }
    
    def _extract_pattern(self, text: str, patterns: List[str]) -> Optional[str]:
        """
        Extract text using the first matching pattern.
        
        Args:
            text: Text to search
            patterns: List of regex patterns
            
        Returns:
            First match found, or None
        """
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                return matches[0]
        return None
    
    def _parse_decimal(self, value_str: str) -> Optional[Decimal]:
        """
        Parse a string value to Decimal.
        
        Args:
            value_str: String value to parse
            
        Returns:
            Decimal value, or None if parsing fails
        """
        try:
            # Remove commas and currency symbols
            cleaned = re.sub(r'[,$]', '', value_str)
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            logger.warning(f"Failed to parse decimal value: {value_str}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse a date string to ISO format.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            ISO formatted date string, or None if parsing fails
        """
        try:
            # Common date formats
            date_formats = [
                '%B %d, %Y',      # January 1, 2025
                '%m/%d/%Y',       # 01/01/2025
                '%m-%d-%Y',       # 01-01-2025
                '%Y-%m-%d',       # 2025-01-01
                '%d %B %Y',       # 1 January 2025
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return original string
            return date_str.strip()
            
        except Exception as e:
            logger.warning(f"Failed to parse date: {date_str}")
            return None
    
    def _parse_parties(self, parties_str: str) -> List[str]:
        """
        Parse parties string to list of party names.
        
        Args:
            parties_str: Parties string to parse
            
        Returns:
            List of party names
        """
        try:
            # Split by common separators
            separators = [' and ', ' & ', ', ', '; ', '\n']
            
            parties = [parties_str]
            for sep in separators:
                new_parties = []
                for party in parties:
                    new_parties.extend(party.split(sep))
                parties = new_parties
            
            # Clean up party names
            cleaned_parties = []
            for party in parties:
                cleaned = party.strip()
                if cleaned and len(cleaned) > 2:  # Filter out very short strings
                    cleaned_parties.append(cleaned)
            
            return cleaned_parties
            
        except Exception as e:
            logger.warning(f"Failed to parse parties: {parties_str}")
            return [parties_str]
    
    def extract_invoice_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract invoice-specific metadata from document text.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dict containing invoice metadata
        """
        try:
            if not text or not text.strip():
                return {"success": True}
            
            metadata = {"success": True}
            
            # Extract invoice number
            invoice_patterns = [
                r'invoice[:\s]*number[:\s]*([A-Za-z0-9\-_]+)',
                r'invoice[:\s]*#?([A-Za-z0-9\-_]+)',
                r'inv[:\s]*#?([A-Za-z0-9\-_]+)',
            ]
            invoice_number = self._extract_pattern(text, invoice_patterns)
            if invoice_number:
                metadata["invoice_number"] = invoice_number.strip()
            
            # Extract invoice date
            invoice_date_patterns = [
                r'invoice[:\s]*date[:\s]*([A-Za-z0-9\s\-\/]+)',
                r'date[:\s]*([A-Za-z0-9\s\-\/]+)',
            ]
            invoice_date = self._extract_pattern(text, invoice_date_patterns)
            if invoice_date:
                metadata["invoice_date"] = self._parse_date(invoice_date.strip())
            
            # Extract due date
            due_date_patterns = [
                r'due[:\s]*date[:\s]*([A-Za-z0-9\s\-\/]+)',
                r'payment[:\s]*due[:\s]*([A-Za-z0-9\s\-\/]+)',
            ]
            due_date = self._extract_pattern(text, due_date_patterns)
            if due_date:
                metadata["due_date"] = self._parse_date(due_date.strip())
            
            # Extract vendor
            vendor_patterns = [
                r'vendor[:\s]*([^\n]+)',
                r'supplier[:\s]*([^\n]+)',
                r'from[:\s]*([^\n]+)',
            ]
            vendor = self._extract_pattern(text, vendor_patterns)
            if vendor:
                metadata["vendor"] = vendor.strip()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting invoice metadata: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to extract invoice metadata: {str(e)}"
            }
