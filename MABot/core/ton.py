from config import MNEMONIC, TONCENTER_API_KEY, IS_TESTNET

from decimal import Decimal
from datetime import datetime

from MABot.core.mongo import PaymentsCol

from tonutils.wallet import WalletV5R1
from tonutils.client import ToncenterV3Client

FEE_DEDUCT_TON = Decimal('0.005')
FEE_DEDUCT_NANO = int(FEE_DEDUCT_TON * 1_000_000_000)

class TonPaymentError(Exception):
    """Base exception for TON payment failures."""
    pass

class LowBalanceError(TonPaymentError):
    pass

class AmountTooSmallError(TonPaymentError):
    pass

class InsufficientReserveError(TonPaymentError):
    pass

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

    balance = await wallet.get_balance(client, sender_address)
    balance_nano = int(balance * 1_000_000_000)

    if balance_nano < desired_nano:
        raise LowBalanceError("Wallet balance is lower than requested amount")
    
    if send_nano <= 0:
        raise AmountTooSmallError("Amount too small to cover fee")

    # Check tx can be sent
    # if balance_nano < send_nano + 50_000_000:  # some reserve
    #     raise InsufficientReserveError("Not enough balance for reserve")


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
        raise TonPaymentError(f"Failed to send TON Payment: {e}") from e
