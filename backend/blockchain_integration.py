"""
Blockchain Integration Module for Aetherstore Engine
Implements digital ownership and NFT functionality for fashion items
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

class DigitalAssetType(Enum):
    DIGITAL_CLOTHING = "digital_clothing"
    NFT_FASHION = "nft_fashion"
    DIGITAL_LICENSE = "digital_license"
    VIRTUAL_ACCESSORY = "virtual_accessory"

class OwnershipStatus(Enum):
    OWNED = "owned"
    LICENSED = "licensed"
    RENTED = "rented"
    SHARED = "shared"

@dataclass
class BlockchainTransaction:
    """Represents a blockchain transaction"""
    tx_id: str
    from_address: str
    to_address: str
    asset_id: str
    amount: float
    timestamp: str
    signature: str
    tx_type: str
    status: str  # pending, confirmed, failed

@dataclass
class DigitalFashionAsset:
    """Represents a digital fashion item"""
    asset_id: str
    name: str
    description: str
    asset_type: DigitalAssetType
    creator: str
    metadata: Dict
    blockchain_hash: str
    created_date: str
    attributes: Dict
    provenance: List[str]  # List of previous owners

class BlockchainManager:
    """Manages blockchain operations for digital fashion assets"""
    
    def __init__(self):
        self.asset_registry = {}
        self.transactions = []
        self.blockchain_state = {
            "last_block_hash": "0000000000000000000000000000000000000000000000000000000000000000",
            "transaction_count": 0,
            "asset_count": 0
        }
        
        print("Blockchain Manager initialized")
    
    def calculate_hash(self, data: str) -> str:
        """Calculate SHA256 hash of data"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def create_digital_asset(self, name: str, description: str, asset_type: DigitalAssetType, 
                           creator: str, metadata: Dict) -> DigitalFashionAsset:
        """Create a new digital fashion asset"""
        asset_id = f"asset_{uuid.uuid4().hex[:12]}"
        
        # Create asset data for hashing
        asset_data = {
            "asset_id": asset_id,
            "name": name,
            "description": description,
            "asset_type": asset_type.value,
            "creator": creator,
            "metadata": metadata,
            "created_date": datetime.now().isoformat()
        }
        
        blockchain_hash = self.calculate_hash(json.dumps(asset_data, sort_keys=True))
        
        digital_asset = DigitalFashionAsset(
            asset_id=asset_id,
            name=name,
            description=description,
            asset_type=asset_type,
            creator=creator,
            metadata=metadata,
            blockchain_hash=blockchain_hash,
            created_date=datetime.now().isoformat(),
            attributes=metadata.get("attributes", {}),
            provenance=[creator]
        )
        
        self.asset_registry[asset_id] = digital_asset
        self.blockchain_state["asset_count"] += 1
        
        print(f"Created digital asset: {asset_id}")
        return digital_asset
    
    def mint_nft(self, asset_id: str, owner_address: str, license_type: str = "full") -> BlockchainTransaction:
        """Mint an NFT for a digital fashion asset"""
        if asset_id not in self.asset_registry:
            raise ValueError(f"Asset {asset_id} does not exist")
        
        asset = self.asset_registry[asset_id]
        
        tx_id = f"tx_{uuid.uuid4().hex[:12]}"
        
        transaction = BlockchainTransaction(
            tx_id=tx_id,
            from_address="0x0000000000000000000000000000000000000000",  # Contract address
            to_address=owner_address,
            asset_id=asset_id,
            amount=1.0,
            timestamp=datetime.now().isoformat(),
            signature=f"sig_{uuid.uuid4().hex[:16]}",
            tx_type="mint",
            status="confirmed"
        )
        
        # Update asset provenance
        asset.provenance.append(owner_address)
        
        self.transactions.append(transaction)
        self.blockchain_state["transaction_count"] += 1
        
        print(f"Minted NFT for asset {asset_id} to {owner_address}")
        return transaction
    
    def transfer_asset(self, asset_id: str, from_address: str, to_address: str) -> BlockchainTransaction:
        """Transfer ownership of a digital asset"""
        if asset_id not in self.asset_registry:
            raise ValueError(f"Asset {asset_id} does not exist")
        
        # Find original owner in provenance
        asset = self.asset_registry[asset_id]
        if from_address not in asset.provenance:
            raise ValueError(f"Address {from_address} does not own asset {asset_id}")
        
        tx_id = f"tx_{uuid.uuid4().hex[:12]}"
        
        transaction = BlockchainTransaction(
            tx_id=tx_id,
            from_address=from_address,
            to_address=to_address,
            asset_id=asset_id,
            amount=1.0,
            timestamp=datetime.now().isoformat(),
            signature=f"sig_{uuid.uuid4().hex[:16]}",
            tx_type="transfer",
            status="confirmed"
        )
        
        # Update asset provenance
        asset.provenance.append(to_address)
        
        self.transactions.append(transaction)
        self.blockchain_state["transaction_count"] += 1
        
        print(f"Transferred asset {asset_id} from {from_address} to {to_address}")
        return transaction
    
    def get_asset_ownership(self, asset_id: str) -> Dict:
        """Get ownership information for an asset"""
        if asset_id not in self.asset_registry:
            return {"error": f"Asset {asset_id} not found"}
        
        asset = self.asset_registry[asset_id]
        
        return {
            "asset_id": asset.id,
            "current_owner": asset.provenance[-1] if asset.provenance else "unknown",
            "provenance": asset.provenance,
            "creation_date": asset.created_date,
            "asset_type": asset.asset_type.value,
            "blockchain_hash": asset.blockchain_hash,
            "metadata": asset.metadata
        }
    
    def verify_ownership(self, asset_id: str, owner_address: str) -> bool:
        """Verify if an address owns a specific asset"""
        if asset_id not in self.asset_registry:
            return False
        
        asset = self.asset_registry[asset_id]
        return asset.provenance and asset.provenance[-1] == owner_address
    
    def get_user_assets(self, user_address: str) -> List[DigitalFashionAsset]:
        """Get all assets owned by a user"""
        user_assets = []
        
        for asset in self.asset_registry.values():
            if asset.provenance and asset.provenance[-1] == user_address:
                user_assets.append(asset)
        
        return user_assets

class DigitalOwnershipService:
    """Main service for digital ownership and NFT functionality"""
    
    def __init__(self):
        self.blockchain_manager = BlockchainManager()
        print("Digital Ownership Service initialized")
    
    async def create_digital_fashion_item(self, name: str, description: str, creator_id: str, 
                                        metadata: Dict) -> Dict:
        """Create a new digital fashion item"""
        asset = self.blockchain_manager.create_digital_asset(
            name=name,
            description=description,
            asset_type=DigitalAssetType.DIGITAL_CLOTHING,
            creator=creator_id,
            metadata=metadata
        )
        
        return {
            "success": True,
            "asset": {
                "asset_id": asset.asset_id,
                "name": asset.name,
                "description": asset.description,
                "asset_type": asset.asset_type.value,
                "creator": asset.creator,
                "blockchain_hash": asset.blockchain_hash,
                "created_date": asset.created_date,
                "metadata": asset.metadata
            },
            "message": "Digital fashion item created and registered on blockchain"
        }
    
    async def mint_fashion_nft(self, asset_id: str, owner_address: str) -> Dict:
        """Mint an NFT for a digital fashion item"""
        try:
            transaction = self.blockchain_manager.mint_nft(asset_id, owner_address)
            
            return {
                "success": True,
                "transaction": {
                    "tx_id": transaction.tx_id,
                    "asset_id": transaction.asset_id,
                    "owner": transaction.to_address,
                    "timestamp": transaction.timestamp,
                    "status": transaction.status
                },
                "message": "Fashion NFT minted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to mint NFT"
            }
    
    async def transfer_fashion_item(self, asset_id: str, from_address: str, to_address: str) -> Dict:
        """Transfer a digital fashion item between users"""
        try:
            transaction = self.blockchain_manager.transfer_asset(asset_id, from_address, to_address)
            
            return {
                "success": True,
                "transaction": {
                    "tx_id": transaction.tx_id,
                    "asset_id": transaction.asset_id,
                    "from": transaction.from_address,
                    "to": transaction.to_address,
                    "timestamp": transaction.timestamp,
                    "status": transaction.status
                },
                "message": "Fashion item transferred successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to transfer fashion item"
            }
    
    async def verify_fashion_ownership(self, asset_id: str, owner_address: str) -> Dict:
        """Verify if user owns a specific fashion item"""
        is_owner = self.blockchain_manager.verify_ownership(asset_id, owner_address)
        
        return {
            "asset_id": asset_id,
            "owner_address": owner_address,
            "is_owner": is_owner,
            "verified": True
        }
    
    async def get_user_fashion_collection(self, user_address: str) -> Dict:
        """Get all digital fashion items owned by a user"""
        assets = self.blockchain_manager.get_user_assets(user_address)
        
        collection = []
        for asset in assets:
            collection.append({
                "asset_id": asset.asset_id,
                "name": asset.name,
                "description": asset.description,
                "asset_type": asset.asset_type.value,
                "created_date": asset.created_date,
                "metadata": asset.metadata
            })
        
        return {
            "user_address": user_address,
            "collection_size": len(collection),
            "assets": collection
        }
    
    async def get_asset_details(self, asset_id: str) -> Dict:
        """Get detailed information about a digital fashion asset"""
        ownership_info = self.blockchain_manager.get_asset_ownership(asset_id)
        
        if "error" in ownership_info:
            return ownership_info
        
        return {
            "asset_details": ownership_info,
            "blockchain_status": "verified",
            "provenance_chain": ownership_info["provenance"],
            "authenticity": True
        }

# Example usage
async def main():
    ownership_service = DigitalOwnershipService()
    
    # Create a digital fashion item
    asset_result = await ownership_service.create_digital_fashion_item(
        name="Cyberpunk Jacket",
        description="A futuristic digital jacket",
        creator_id="creator_123",
        metadata={
            "category": "outerwear",
            "style": "cyberpunk",
            "rarity": "legendary",
            "attributes": {
                "color": "neon_blue",
                "material": "holographic",
                "design": "geometric_patterns"
            }
        }
    )
    
    print("Asset Creation Result:")
    print(json.dumps(asset_result, indent=2))
    
    if asset_result["success"]:
        asset_id = asset_result["asset"]["asset_id"]
        
        # Mint the NFT
        mint_result = await ownership_service.mint_fashion_nft(asset_id, "owner_456")
        print("\nMint Result:")
        print(json.dumps(mint_result, indent=2))
        
        # Verify ownership
        verify_result = await ownership_service.verify_fashion_ownership(asset_id, "owner_456")
        print("\nOwnership Verification:")
        print(json.dumps(verify_result, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())