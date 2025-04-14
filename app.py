import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Replace with your Amazon Product Advertising API credentials
AWS_ACCESS_KEY = 'YOUR_AWS_ACCESS_KEY'
AWS_SECRET_KEY = 'YOUR_AWS_SECRET_KEY'
ASSOCIATE_TAG = 'YOUR_ASSOCIATE_TAG'

def get_amazon_product_info(product_name):
    try:
        client = boto3.client(
            'product-advertising',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name='us-east-1'
        )

        response = client.search_items(
            Keywords=product_name,
            Resources=['ItemInfo.Title', 'ItemInfo.CustomerReviews'],
            PartnerTag=ASSOCIATE_TAG,
            PartnerType='Associates',
            Marketplace='www.amazon.com'
        )

        items = response.get('ItemsResult', {}).get('Items', [])
        if not items:
            return 'No products found.'

        product = items[0]
        title = product.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', 'N/A')
        rating = product.get('ItemInfo', {}).get('CustomerReviews', {}).get('AverageRating', 'N/A')
        total_reviews = product.get('ItemInfo', {}).get('CustomerReviews', {}).get('TotalReviews', 'N/A')

        return f"Title: {title}\nRating: {rating}\nTotal Reviews: {total_reviews}"

    except (BotoCoreError, ClientError) as error:
        return f"An error occurred: {error}"

# Example usage
product_name = 'iPhone 13'
print(get_amazon_product_info(product_name))
