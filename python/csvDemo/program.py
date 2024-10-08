import os
import csv
from nexarClient import NexarClient

mpn_quantities = []

# Reading the MPNs and quantities from the input file
with open("C:/Users/Zach.Gunter/Documents/GitHub/nexar-first-supply-query/python/csvDemo/input.csv", newline="") as inputFile:
    data = csv.reader(inputFile, delimiter=",", quotechar="|")
    for row in data:
        # Assuming each row has two columns: part number and quantity
        mpn = row[0].strip()
        quantity = int(row[1].strip())
        mpn_quantities.append((mpn, quantity))

# GraphQL query
gqlQuery = '''
query csvDemo ($queries: [SupPartMatchQuery!]!) {
  supMultiMatch (
    currency: "USD",
    queries: $queries
  ){
    parts {
      mpn
      name
      sellers {
        company {
          id
          name
        }
        offers {
          inventoryLevel
          prices {
            quantity
            convertedPrice
            convertedCurrency
          }
        }
      }
    }
  }
}
'''

if __name__ == "__main__":
    # Replace with your actual clientId and clientSecret
    clientId = "ad0db8d1-6173-4f04-8856-8772c782d0aa"
    clientSecret = "HcBqkUPaQUBu4ZQbFsqdU9DB4S8VF0wCrINT"
    nexar = NexarClient(clientId, clientSecret)

    # Preparing queries for each MPN
    queries = [{"start": 0, "limit": 1, "mpn": mpn} for mpn, _ in mpn_quantities]
    variables = {"queries": queries}
    results = nexar.get_query(gqlQuery, variables)

    if results:
        with open("output.csv", "w", newline="") as outputFile:
            writer = csv.writer(outputFile)
            writer.writerow(["Part Number", "Quantity", "Vendor 1", "Vendor 1 Unit Price", "Vendor 2", "Vendor 2 Unit Price", "Vendor 3", "Vendor 3 Unit Price"])

            for i, query in enumerate(results.get("supMultiMatch", [])):
                # Get the original MPN and quantity from the input file
                input_mpn, input_quantity = mpn_quantities[i]

                # Find the part in the query results that matches the input MPN
                part = query.get("parts", [])[0]
                part_mpn = part.get("mpn")

                # Only process the part if the MPN matches the input
                if part_mpn != input_mpn:
                    print(f"Warning: Mismatch in MPNs. Expected {input_mpn}, but got {part_mpn}. Skipping.")
                    continue
                
                # Collect vendors and their prices based on the input quantity
                vendor_prices = []
                for seller in part.get("sellers", []):
                    for offer in seller.get("offers", []):
                        # Find the best price for the input quantity
                        best_price = None
                        for price in offer.get("prices", []):
                            if price.get("quantity") <= input_quantity:
                                # Select the closest price based on quantity
                                if best_price is None or price.get("quantity") > best_price.get("quantity"):
                                    best_price = price

                        if best_price:
                            vendor_prices.append({
                                "vendor": seller.get("company").get("name"),
                                "price": best_price.get("convertedPrice")
                            })

                # Sort vendors by price (ascending)
                vendor_prices = sorted(vendor_prices, key=lambda x: x["price"])

                # Ensure there are at least 3 vendors
                if len(vendor_prices) >= 3:
                    cheapest = vendor_prices[0]
                    median = vendor_prices[len(vendor_prices) // 2]
                    expensive = vendor_prices[-1]

                    # Write the data in the desired format
                    writer.writerow([
                        part_mpn,
                        input_quantity,
                        cheapest["vendor"], cheapest["price"],
                        median["vendor"], median["price"],
                        expensive["vendor"], expensive["price"]
                    ])
                else:
                    print(f"Warning: Not enough vendors for part {part_mpn}")
