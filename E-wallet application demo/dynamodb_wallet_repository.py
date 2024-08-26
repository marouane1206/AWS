import re
import boto3
import uuid

from ewallet.repository.base_repository import BaseRepository
from ewallet.model.wallet import Wallet

class DynamoDbWalletRepository(BaseRepository):
    """
    Concrete class for that implements the Repository interface.
    This class is responsible to handle Wallet objects
    interacting with the DynamoDB database.
    """

    def __init__(self, dynamodb_client: boto3.client, wallet_table_name: str):
        self.dynamodb_client = dynamodb_client
        self.wallet_table_name = wallet_table_name

    def list_wallets(self) -> list[Wallet]:
        """
        Lists all wallets from the DynamoDB database.

        :return: A list of all wallets.
        :rtype: list[Wallet]
        """
        response = self.dynamodb_client.scan(
            TableName=self.wallet_table_name
        )

        items = response.get('Items')

        if items is None:
            return []

        return [Wallet(item.get('name').get('S')) for item in items]

    def save(self, wallet: Wallet) -> str:
        """
        Saves a wallet to the DynamoDB database.

        :param wallet: The wallet to save.
        :return: The id of the saved wallet.
        :rtype: str
        """
        wallet.id = str(uuid.uuid4())

        self.dynamodb_client.put_item(
            TableName=self.wallet_table_name,
            Item={
                'id': {'S': wallet.id},
                'name': {'S': wallet.name}
            }
        )

        return wallet.id
    

    def find(self, id: str) -> Wallet:
        """
        Finds a wallet by id.

        :param str id: The id of the wallet to find.
        :return: The wallet found.
        :rtype: Wallet
        """
        # Input validation
        if not id or not isinstance(id, str):
            raise ValueError("Invalid wallet ID. ID must be a non-empty string.")

        # Validate the ID format (e.g., alphanumeric with a maximum length of 20 characters)
        id_pattern = r'^[\w]{1,20}$'
        if not re.match(id_pattern, id):
            raise ValueError("Invalid wallet ID format. ID must be alphanumeric and no longer than 20 characters.")

        try:
            response = self.dynamodb_client.get_item(
                TableName=self.wallet_table_name,
                Key={
                    'id': {'S': id}
                }
            )

            item = response.get('Item')

            if item is None:
                return None

            wallet = Wallet(item.get('name').get('S'))

            return wallet
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"Error occurred while retrieving wallet: {e}")
            return None
