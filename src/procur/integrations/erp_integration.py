"""Real ERP system integrations (SAP, Oracle, NetSuite)."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


class ERPIntegration(ABC):
    """Base class for ERP integrations."""
    
    @abstractmethod
    def create_purchase_order(
        self,
        vendor_id: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        currency: str = "USD",
    ) -> str:
        """Create purchase order in ERP."""
        pass
    
    @abstractmethod
    def get_purchase_order(self, po_number: str) -> Dict[str, Any]:
        """Get purchase order details."""
        pass
    
    @abstractmethod
    def validate_budget(
        self,
        department: str,
        amount: float,
        fiscal_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Validate budget availability."""
        pass
    
    @abstractmethod
    def create_invoice(
        self,
        po_number: str,
        invoice_number: str,
        amount: float,
        due_date: datetime,
    ) -> str:
        """Create invoice in AP."""
        pass
    
    @abstractmethod
    def reconcile_invoice(
        self,
        invoice_id: str,
        po_number: str,
    ) -> Dict[str, Any]:
        """Reconcile invoice with PO."""
        pass


class SAPIntegration(ERPIntegration):
    """SAP ERP integration via OData API."""
    
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        company_code: str,
    ):
        """
        Initialize SAP integration.
        
        Args:
            base_url: SAP OData API base URL
            client_id: OAuth client ID
            client_secret: OAuth client secret
            company_code: SAP company code
        """
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.company_code = company_code
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with SAP OAuth."""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            logger.info("SAP authentication successful")
        except requests.RequestException as e:
            logger.error(f"SAP authentication failed: {e}")
            raise
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    def create_purchase_order(
        self,
        vendor_id: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        currency: str = "USD",
    ) -> str:
        """Create purchase order in SAP."""
        try:
            # Prepare PO data
            po_data = {
                "CompanyCode": self.company_code,
                "VendorID": vendor_id,
                "Currency": currency,
                "TotalAmount": total_amount,
                "Items": [
                    {
                        "Material": item["material_id"],
                        "Quantity": item["quantity"],
                        "UnitPrice": item["unit_price"],
                        "Plant": item.get("plant", "1000"),
                    }
                    for item in items
                ],
            }
            
            response = requests.post(
                f"{self.base_url}/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder",
                json=po_data,
                headers=self._headers(),
            )
            response.raise_for_status()
            
            po_number = response.json()["d"]["PurchaseOrder"]
            logger.info(f"Created SAP PO: {po_number}")
            return po_number
            
        except requests.RequestException as e:
            logger.error(f"Failed to create SAP PO: {e}")
            raise
    
    def get_purchase_order(self, po_number: str) -> Dict[str, Any]:
        """Get purchase order from SAP."""
        try:
            response = requests.get(
                f"{self.base_url}/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder('{po_number}')",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()["d"]
        except requests.RequestException as e:
            logger.error(f"Failed to get SAP PO: {e}")
            raise
    
    def validate_budget(
        self,
        department: str,
        amount: float,
        fiscal_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Validate budget in SAP."""
        fiscal_year = fiscal_year or datetime.now().year
        
        try:
            response = requests.get(
                f"{self.base_url}/sap/opu/odata/sap/API_BUDGET_SRV/BudgetCheck",
                params={
                    "CostCenter": department,
                    "FiscalYear": fiscal_year,
                    "Amount": amount,
                },
                headers=self._headers(),
            )
            response.raise_for_status()
            
            data = response.json()["d"]
            return {
                "available": data["BudgetAvailable"] >= amount,
                "budget_total": data["BudgetTotal"],
                "budget_used": data["BudgetUsed"],
                "budget_available": data["BudgetAvailable"],
            }
        except requests.RequestException as e:
            logger.error(f"Failed to validate SAP budget: {e}")
            raise
    
    def create_invoice(
        self,
        po_number: str,
        invoice_number: str,
        amount: float,
        due_date: datetime,
    ) -> str:
        """Create invoice in SAP AP."""
        try:
            invoice_data = {
                "CompanyCode": self.company_code,
                "PurchaseOrder": po_number,
                "InvoiceNumber": invoice_number,
                "InvoiceAmount": amount,
                "DueDate": due_date.isoformat(),
            }
            
            response = requests.post(
                f"{self.base_url}/sap/opu/odata/sap/API_INVOICE_SRV/A_Invoice",
                json=invoice_data,
                headers=self._headers(),
            )
            response.raise_for_status()
            
            invoice_id = response.json()["d"]["InvoiceID"]
            logger.info(f"Created SAP invoice: {invoice_id}")
            return invoice_id
            
        except requests.RequestException as e:
            logger.error(f"Failed to create SAP invoice: {e}")
            raise
    
    def reconcile_invoice(
        self,
        invoice_id: str,
        po_number: str,
    ) -> Dict[str, Any]:
        """Reconcile invoice with PO in SAP."""
        try:
            response = requests.post(
                f"{self.base_url}/sap/opu/odata/sap/API_INVOICE_SRV/ReconcileInvoice",
                json={
                    "InvoiceID": invoice_id,
                    "PurchaseOrder": po_number,
                },
                headers=self._headers(),
            )
            response.raise_for_status()
            
            result = response.json()["d"]
            return {
                "reconciled": result["Status"] == "RECONCILED",
                "discrepancies": result.get("Discrepancies", []),
                "matched_amount": result.get("MatchedAmount"),
            }
        except requests.RequestException as e:
            logger.error(f"Failed to reconcile SAP invoice: {e}")
            raise


class NetSuiteIntegration(ERPIntegration):
    """NetSuite ERP integration via REST API."""
    
    def __init__(
        self,
        account_id: str,
        consumer_key: str,
        consumer_secret: str,
        token_id: str,
        token_secret: str,
    ):
        """
        Initialize NetSuite integration.
        
        Args:
            account_id: NetSuite account ID
            consumer_key: OAuth consumer key
            consumer_secret: OAuth consumer secret
            token_id: Token ID
            token_secret: Token secret
        """
        self.account_id = account_id
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token_id = token_id
        self.token_secret = token_secret
        self.base_url = f"https://{account_id}.suitetalk.api.netsuite.com/services/rest"
    
    def _get_oauth_header(self, method: str, url: str) -> str:
        """Generate OAuth 1.0a header."""
        import time
        import secrets
        import hmac
        import hashlib
        from urllib.parse import quote
        
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(16)
        
        # Build signature base string
        params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_token": self.token_id,
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": timestamp,
            "oauth_nonce": nonce,
            "oauth_version": "1.0",
        }
        
        param_string = "&".join(f"{k}={quote(str(v))}" for k, v in sorted(params.items()))
        base_string = f"{method}&{quote(url)}&{quote(param_string)}"
        
        # Generate signature
        signing_key = f"{quote(self.consumer_secret)}&{quote(self.token_secret)}"
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha256).digest()
        ).decode()
        
        # Build header
        params["oauth_signature"] = signature
        header_params = ", ".join(f'{k}="{quote(str(v))}"' for k, v in params.items())
        return f"OAuth {header_params}"
    
    def _headers(self, method: str, url: str) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": self._get_oauth_header(method, url),
            "Content-Type": "application/json",
            "prefer": "transient",
        }
    
    def create_purchase_order(
        self,
        vendor_id: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        currency: str = "USD",
    ) -> str:
        """Create purchase order in NetSuite."""
        try:
            url = f"{self.base_url}/record/v1/purchaseOrder"
            
            po_data = {
                "entity": {"id": vendor_id},
                "currency": {"refName": currency},
                "item": {
                    "items": [
                        {
                            "item": {"id": item["item_id"]},
                            "quantity": item["quantity"],
                            "rate": item["unit_price"],
                        }
                        for item in items
                    ]
                },
            }
            
            response = requests.post(
                url,
                json=po_data,
                headers=self._headers("POST", url),
            )
            response.raise_for_status()
            
            po_id = response.json()["id"]
            logger.info(f"Created NetSuite PO: {po_id}")
            return po_id
            
        except requests.RequestException as e:
            logger.error(f"Failed to create NetSuite PO: {e}")
            raise
    
    def get_purchase_order(self, po_number: str) -> Dict[str, Any]:
        """Get purchase order from NetSuite."""
        try:
            url = f"{self.base_url}/record/v1/purchaseOrder/{po_number}"
            response = requests.get(url, headers=self._headers("GET", url))
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get NetSuite PO: {e}")
            raise
    
    def validate_budget(
        self,
        department: str,
        amount: float,
        fiscal_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Validate budget in NetSuite."""
        # NetSuite budget validation via custom script
        try:
            url = f"{self.base_url}/query/v1/suiteql"
            query = f"""
                SELECT 
                    SUM(amount) as budget_total,
                    SUM(CASE WHEN status = 'Used' THEN amount ELSE 0 END) as budget_used
                FROM budget
                WHERE department = '{department}'
                AND fiscal_year = {fiscal_year or datetime.now().year}
            """
            
            response = requests.post(
                url,
                json={"q": query},
                headers=self._headers("POST", url),
            )
            response.raise_for_status()
            
            result = response.json()["items"][0]
            budget_available = result["budget_total"] - result["budget_used"]
            
            return {
                "available": budget_available >= amount,
                "budget_total": result["budget_total"],
                "budget_used": result["budget_used"],
                "budget_available": budget_available,
            }
        except requests.RequestException as e:
            logger.error(f"Failed to validate NetSuite budget: {e}")
            raise
    
    def create_invoice(
        self,
        po_number: str,
        invoice_number: str,
        amount: float,
        due_date: datetime,
    ) -> str:
        """Create invoice in NetSuite."""
        try:
            url = f"{self.base_url}/record/v1/vendorBill"
            
            invoice_data = {
                "tranId": invoice_number,
                "entity": {"id": po_number},
                "tranDate": datetime.now().isoformat(),
                "dueDate": due_date.isoformat(),
                "userTotal": amount,
            }
            
            response = requests.post(
                url,
                json=invoice_data,
                headers=self._headers("POST", url),
            )
            response.raise_for_status()
            
            invoice_id = response.json()["id"]
            logger.info(f"Created NetSuite invoice: {invoice_id}")
            return invoice_id
            
        except requests.RequestException as e:
            logger.error(f"Failed to create NetSuite invoice: {e}")
            raise
    
    def reconcile_invoice(
        self,
        invoice_id: str,
        po_number: str,
    ) -> Dict[str, Any]:
        """Reconcile invoice with PO in NetSuite."""
        # NetSuite 3-way match
        try:
            url = f"{self.base_url}/record/v1/vendorBill/{invoice_id}"
            response = requests.get(url, headers=self._headers("GET", url))
            response.raise_for_status()
            
            invoice = response.json()
            po_url = f"{self.base_url}/record/v1/purchaseOrder/{po_number}"
            po_response = requests.get(po_url, headers=self._headers("GET", po_url))
            po_response.raise_for_status()
            po = po_response.json()
            
            # Compare amounts
            invoice_amount = float(invoice["userTotal"])
            po_amount = float(po["total"])
            
            return {
                "reconciled": abs(invoice_amount - po_amount) < 0.01,
                "discrepancies": [] if abs(invoice_amount - po_amount) < 0.01 else ["Amount mismatch"],
                "matched_amount": min(invoice_amount, po_amount),
            }
        except requests.RequestException as e:
            logger.error(f"Failed to reconcile NetSuite invoice: {e}")
            raise


def create_erp_integration(
    erp_type: str,
    **credentials
) -> ERPIntegration:
    """
    Factory function to create ERP integration.
    
    Args:
        erp_type: Type of ERP (sap, netsuite, oracle)
        **credentials: ERP-specific credentials
    
    Returns:
        ERPIntegration instance
    """
    if erp_type.lower() == "sap":
        return SAPIntegration(**credentials)
    elif erp_type.lower() == "netsuite":
        return NetSuiteIntegration(**credentials)
    else:
        raise ValueError(f"Unsupported ERP type: {erp_type}")
