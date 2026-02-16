from config import MNEMONIC, TONCENTER_API_KEY, IS_TESTNET

from decimal import Decimal
from datetime import datetime

from MABot.logging import LOGGER
from MABot.core.mongo import PaymentsCol

from tonutils.wallet import WalletV5R1
from tonutils.client import ToncenterV3Client

FEE_DEDUCT_TON = Decimal('0.005')
FEE_DEDUCT_NANO = int(FEE_DEDUCT_TON * 1_000_000_000)

async def send_ton(
    deal_id: str,
    advertiser_id: int,
    to_address: str,
    amount: float,
) -> str | None:
    client = ToncenterV3Client(
        api_key=TONCENTER_API_KEY,
        is_testnet=IS_TESTNET,
        rps=5,
        max_retries=3
    )

    wallet, _, _, _ = WalletV5R1.from_mnemonic(client, MNEMONIC)
    sender_address = wallet.address.to_str(is_test_only=IS_TESTNET, is_bounceable=False)

    desired_nano = int(amount * 1_000_000_000)
    send_nano = desired_nano - FEE_DEDUCT_NANO

    balance_nano = await wallet.get_balance(client, sender_address)
    if balance_nano < desired_nano:
        LOGGER(__name__).error("Low balance")
        return None
    
    if send_nano <= 0:
        LOGGER(__name__).error("Amount too small to cover fee")
        return None

    # Check tx can be sent
    if balance_nano < send_nano + 50_000_000:  # some reserve
        LOGGER(__name__).error("Not enough balance")
        return None


    try:

        tx_hash = await wallet.transfer(
            destination=to_address,
            amount=amount,
            body=f"Deal:{deal_id} Refund",
        )

        # Insert into MongoDB
        await PaymentsCol.insert_one({
            "userId": advertiser_id,
            "type": "received",
            "amount": amount,
            "from": sender_address,
            "to": to_address,
            "label": f"Deal #${deal_id} - Payment Refund",
            "date": datetime.now(),
            "txHash": tx_hash
        })

        return tx_hash
    except Exception as e:
        LOGGER(__name__).error(f"Failed to send TON Payment: {str(e)}")
        return
